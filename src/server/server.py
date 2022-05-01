#!/usr/bin/python
import json
import logging
from typing import List

import validators
from fastapi import FastAPI, status, HTTPException
from kafka import KafkaProducer

from server.checker import WebsiteChecker
from common.constants import REMOVE_WEBSITE_CHECKER
from common.database.models import WebsiteCheckerModel
from common.database.repository.errors import RowStillInUse
from common.database.repository.repositories import WebsiteCheckerRepository, MetricRepository, RegExpRepository
from common.dto import WebsiteCheckerRemoveDto
from common.utils import start_up, log_errors
from server.rest_models import WebsiteCheckerRestModel, RegExpRestModel, CreateResponse
from server.website_checker_is import WebsiteCheckerIS

WEBSITE_CHECKER = "/website_checker"
METRIC = "/metric"
REGEXP = "/regexp"
CHECKERS = {}

settings = start_up()

DB_HOST = settings.db_host
DB_PORT = settings.db_port
DB_USER = settings.db_user
DB_PASSWORD = settings.db_password
DB_NAME = settings.db_name
SSL_MODE = settings.ssl_mode

_website_checker_repo = WebsiteCheckerRepository(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, SSL_MODE)
_metrics_repo = MetricRepository(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, SSL_MODE)
_regexp_repo = RegExpRepository(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, SSL_MODE)
_website_is = WebsiteCheckerIS(_website_checker_repo, _regexp_repo)
_producer = KafkaProducer(bootstrap_servers=settings.servers,
                          value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                          security_protocol="SSL",
                          ssl_cafile=settings.ssl_kafka_ca_cert_path, ssl_certfile=settings.ssl_kafka_service_cert_path,
                          ssl_keyfile=settings.ssl_kafka_service_key_path)
NOT_FOUND_EXCEPTION = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")


def _update_website_checker(id: str, is_run: bool) -> WebsiteCheckerModel:
    website_checker = _website_checker_repo.get(id)
    if not website_checker:
        raise NOT_FOUND_EXCEPTION
    website_checker.is_run = is_run
    _website_checker_repo.update(website_checker)
    return website_checker


def restart_checks():
    checkers = _website_checker_repo.get_all()
    for checker in checkers:
        start_checker(checker)


def start_checker(website_checker: WebsiteCheckerModel):
    if website_checker.is_run:
        website_dto = _website_is.to_website_checker_dto(website_checker)
        CHECKERS[website_checker.id] = WebsiteChecker(website_dto, settings.max_timeout, settings.topic,
                                                      settings.servers, settings.ssl_kafka_ca_cert_path,
                                                      settings.ssl_kafka_service_cert_path,
                                                      settings.ssl_kafka_service_key_path)
        CHECKERS[website_checker.id].run()


_logger = logging.getLogger(__name__)
restart_checks()
app = FastAPI(title="Website checker", docs_url="/swaggerui")

_logger.info("APP is started")


@log_errors(_logger)
@app.get(WEBSITE_CHECKER)
def get_websites() -> List[dict]:
    return [model.to_dict() for model in _website_checker_repo.get_all()]


@log_errors(_logger)
@app.get(WEBSITE_CHECKER + "/{id}")
def get_website(id: str) -> dict:
    website_checker = _website_checker_repo.get(id)
    if not website_checker:
        raise NOT_FOUND_EXCEPTION
    return website_checker.to_dict()


@log_errors(_logger)
@app.post(WEBSITE_CHECKER, response_model=CreateResponse, status_code=status.HTTP_201_CREATED)
async def create_website_checker(website_checker: WebsiteCheckerRestModel) -> CreateResponse:
    if website_checker.update_interval <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="update_interval should be at least 1 sec")
    if not validators.url(website_checker.url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid url")

    website_checker_id = _website_checker_repo.insert(website_checker.to_model())
    website_model = website_checker.to_model()
    website_model.id = website_checker_id
    start_checker(website_model)
    return CreateResponse(website_checker_id)


@log_errors(_logger)
@app.delete(WEBSITE_CHECKER + "/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_website_checker(id: str) -> None:
    website_checker = _website_checker_repo.get(id)
    if not website_checker:
        raise NOT_FOUND_EXCEPTION

    if website_checker.is_run:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Website checker is under control, stop it before deleting")

    _producer.send(settings.topic, WebsiteCheckerRemoveDto(id), key=REMOVE_WEBSITE_CHECKER)


@log_errors(_logger)
@app.post(WEBSITE_CHECKER + "/{id}/stop", status_code=status.HTTP_204_NO_CONTENT)
async def website_stop(id: str):
    _update_website_checker(id, False)
    CHECKERS.get(id).stop()


@log_errors(_logger)
@app.post(WEBSITE_CHECKER + "/stop", status_code=status.HTTP_204_NO_CONTENT)
async def website_stop():
    checkers = _website_checker_repo.get_all()
    for checker in checkers:
        _update_website_checker(checker.id, False)
        CHECKERS.get(checker.id).stop()


@log_errors(_logger)
@app.post(WEBSITE_CHECKER + "/{id}/start", status_code=status.HTTP_204_NO_CONTENT)
async def website_start(id: str):
    website_checker = _update_website_checker(id, True)
    if not CHECKERS.get(id):
        start_checker(website_checker)


@log_errors(_logger)
@app.get(METRIC)
async def get_metrics() -> List[dict]:
    return [model.to_dict() for model in _metrics_repo.get_all()]


@log_errors(_logger)
@app.get(METRIC + "/{website_checker_id}")
async def get_metrics_by_website(website_checker_id: str) -> List[dict]:
    website_checker = _website_checker_repo.get(website_checker_id)
    if not website_checker:
        raise NOT_FOUND_EXCEPTION
    return [model.to_dict() for model in _metrics_repo.get_by_website_checker_id(website_checker_id)]


@log_errors(_logger)
@app.get(REGEXP)
async def get_regexps() -> List[dict]:
    return [model.to_dict() for model in _regexp_repo.get_all()]


@log_errors(_logger)
@app.get(REGEXP + "/{id}")
async def get_regexp(id: str) -> dict:
    regexp = _regexp_repo.get(id)
    if not regexp:
        raise NOT_FOUND_EXCEPTION
    return regexp.to_dict()


@log_errors(_logger)
@app.post(REGEXP, response_model=CreateResponse, status_code=status.HTTP_201_CREATED)
async def create_regexp(regexp: RegExpRestModel):
    regexp_id = _regexp_repo.insert(regexp.to_model())
    return CreateResponse(regexp_id)


@log_errors(_logger)
@app.delete(REGEXP + "/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_regexp(id: str) -> None:
    regexp = _regexp_repo.get(id)
    if not regexp:
        raise NOT_FOUND_EXCEPTION
    try:
        _regexp_repo.remove(id)
    except RowStillInUse:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="RegExp is still on use")

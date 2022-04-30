#!/usr/bin/python
import json
import logging

from kafka import KafkaConsumer

from common.constants import ADD_METRIC, REMOVE_WEBSITE_CHECKER
from common.database.models import MetricModel
from common.database.repository.repositories import MetricRepository, WebsiteCheckerRepository
from common.dto import WebsiteCheckerRemoveDto
from common.utils import start_up

settings = start_up()

DB_HOST = settings.db_host
DB_PORT = settings.db_port
DB_USER = settings.db_user
DB_PASSWORD = settings.db_password
DB_NAME = settings.db_name
SSL_MODE = settings.ssl_mode

_logger = logging.getLogger(__name__)
_metrics_repo = MetricRepository(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, SSL_MODE)
_website_checker_repo = WebsiteCheckerRepository(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, SSL_MODE)


def add_metric(metric: dict):
    check = MetricModel.from_dict(metric)
    try:
        _logger.debug("Try to write {}".format(check))
        print(check)
        _metrics_repo.insert(check)
        _logger.info("Wrote new metric")
    except Exception as err:
        _logger.error("ERROR: {}".format(err))
        raise err


def remove_website_checker(website_checker_data):
    checker_id = WebsiteCheckerRemoveDto.from_dict(website_checker_data).id

    _metrics_repo.remove_by_website_checker_id(checker_id)
    _logger.debug(f"Metrics for website_checker {checker_id} are deleted")
    _website_checker_repo.remove(checker_id)
    _logger.debug(f"website_checker {checker_id} is deleted")


ACTIONS_BY_KEY = {
    ADD_METRIC: add_metric,
    REMOVE_WEBSITE_CHECKER: remove_website_checker
}


def handle_message(message):
    action = ACTIONS_BY_KEY.get(message.key)
    if action:
        action(message.value)
    else:
        _logger.error(f"Couldn't find action for key = {message.key}")


consumer = KafkaConsumer(settings.topic, group_id=settings.consumer_group_id, bootstrap_servers=settings.servers,
                         auto_offset_reset='earliest',value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                         security_protocol="SSL", ssl_cafile=settings.ssl_kafka_ca_cert_path,
                         ssl_certfile=settings.ssl_kafka_service_cert_path,
                         ssl_keyfile=settings.ssl_kafka_service_key_path)
_logger.debug("Start Consumer")

while True:
    for message in consumer:
        _logger.debug("Receive message {}".format(message))
        handle_message(message)

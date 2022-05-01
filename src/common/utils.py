import logging
import logging.config

import psycopg2

from common.config import Config, get_config
from common.database.repository.base_repository import BasePostgreSQlRepository


def configure_logger():
    logging.config.fileConfig("resources/logger_config.conf", disable_existing_loggers=False)


def create_db(config: Config):
    conn = None
    try:
        conn = psycopg2.connect(host=config.db_host, port=config.db_port, user=config.db_user,
                                password=config.db_password,
                                dbname=config.db_name,
                                sslmode=config.ssl_mode)
        BasePostgreSQlRepository.run_query(conn,
                                           lambda cursor: cursor.execute(open("resources/db/schema.sql", "r").read()))
    finally:
        if conn:
            conn.close()


def start_up():
    configure_logger()
    config = get_config()
    create_db(config)
    return config


def log_errors(logger: logging.Logger):
    def decorator(function):
        def wrapper(*args, **kwargs):
            try:
                logger.debug(f"Run {function.__name__}")
                return function(*args, **kwargs)
            except Exception as err:
                logger.error("Error: {}".format(err))
                raise err

        return wrapper

    return decorator

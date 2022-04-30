from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    max_timeout: int
    topic: str
    servers: list
    db_host: str
    db_port: int
    db_name: str
    ssl_mode: str
    ssl_kafka_ca_cert_path: str
    ssl_kafka_service_cert_path: str
    ssl_kafka_service_key_path: str
    consumer_group_id: str

    class Config:
        env_file = "resources/config.env"


class Config:
    max_timeout: int
    topic: str
    servers: list
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    ssl_mode: str
    ssl_kafka_ca_cert_path: str
    ssl_kafka_service_cert_path: str
    ssl_kafka_service_key_path: str
    consumer_group_id: str

    def __init__(self, settings: Settings):
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.max_timeout = settings.max_timeout
        self.topic = settings.topic
        self.servers = settings.servers
        self.db_host = settings.db_host
        self.db_port = settings.db_port
        self.db_name = settings.db_name
        self.ssl_mode = settings.ssl_mode
        self.ssl_kafka_ca_cert_path = settings.ssl_kafka_ca_cert_path
        self.ssl_kafka_service_cert_path = settings.ssl_kafka_service_cert_path
        self.ssl_kafka_service_key_path = settings.ssl_kafka_service_key_path
        self.consumer_group_id = settings.consumer_group_id


def get_config():
    return Config(Settings())

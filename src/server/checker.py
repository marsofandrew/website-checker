import json
import logging
import math
import re
import time
from datetime import datetime
from threading import Thread

import requests
import urllib3
from kafka import KafkaProducer

from common.constants import ADD_METRIC
from common.database.models import MetricModel
from common.dto import WebsiteCheckerDto

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WebsiteChecker:
    _logger = logging.getLogger(__name__)

    def __init__(self, website_checker: WebsiteCheckerDto, timeout: int, topic: str, servers, ssl_ca_file,
                 ssl_certificate, ssl_keyfile):
        self._website_checker = website_checker
        self._timeout = timeout

        self._producer = KafkaProducer(bootstrap_servers=servers,
                                       value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                                       key_serializer=str.encode,
                                       security_protocol="SSL",
                                       ssl_cafile=ssl_ca_file, ssl_certfile=ssl_certificate,
                                       ssl_keyfile=ssl_keyfile)
        self._topic = topic
        self._thread = None
        self._is_run = True

    def run(self):
        """
        Starts checking website
        """
        self._thread = Thread(target=self._run, args=(self,))
        self._thread.start()

    @staticmethod
    def _run(checker):
        while checker.is_run:
            checker.run_check()
            start_sleep_time = datetime.utcnow()

            while (checker._website_checker.website_checker.update_interval >= math.ceil(
                    (datetime.utcnow() - start_sleep_time).total_seconds())) and checker.is_run:
                time.sleep(1)

    @property
    def is_run(self):
        return self._is_run

    def stop(self):
        """
        Stops checking website
        """
        self._is_run = False
        if self._thread:
            self._thread.join()

    def run_check(self):
        """
        Executes single check
        """
        check = MetricModel(None, self._website_checker.website_checker.id, -1, -1, None, None, False)
        try:
            check.date_time = datetime.utcnow()
            # use verify=False to allow customers request any website
            response = requests.get(self._website_checker.website_checker.url, timeout=self._timeout, verify=False)
            end_time = datetime.utcnow()
            check.response_time = int((end_time - check.date_time).total_seconds() * 1000)
            check.status_code = response.status_code
            if self._website_checker.regexp:
                if re.match(self._website_checker.regexp, response.text):
                    check.is_match = True
                else:
                    check.is_match = False
            if check.is_match is None or check.is_match:
                check.success = True
        except Exception as err:
            self._logger.error("ERROR (run_check): {}".format(err))
            self._handle_exception_in_check(err)

        self._producer.send(self._topic, check.to_dict(), key=ADD_METRIC)

    def _handle_exception_in_check(self, err: Exception) -> None:
        """
        Handles exception thrown by run_check
        :param err: Exception to handle
        :return: None
        """
        pass

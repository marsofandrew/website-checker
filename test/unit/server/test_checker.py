import time
import unittest
from unittest.mock import patch

from requests.models import Response

from common.database.models import WebsiteCheckerModel
from common.dto import WebsiteCheckerDto
from server.checker import WebsiteChecker
from common.database.models import MetricModel


class TestWebsiteChecker(unittest.TestCase):
    REGEXP = "[A-Z]{4}"
    ID = "website_id"
    URL = "my-test-url"
    UPDATE_INTERVAL = 1
    IS_RUN = True
    WEBSITE_CHECKER_MODEL = WebsiteCheckerModel(ID, URL, UPDATE_INTERVAL, "regexp-id", IS_RUN)
    WEBSITE_CHECKER_DTO = WebsiteCheckerDto(WEBSITE_CHECKER_MODEL, REGEXP)

    @patch('kafka.KafkaProducer.__init__', return_value=None)
    @patch('kafka.KafkaProducer.send')
    @patch('requests.get')
    def test_run_check_success(self, request_mock, send_mock, ign):
        status_code = 200

        response = Response()
        response.status_code = status_code
        response._content = "AAAA".encode("utf-8")

        request_mock.return_value = response

        target = WebsiteChecker(self.WEBSITE_CHECKER_DTO, 10, "", [], None, None, None)

        target.run_check()

        send_mock.assert_called()
        metric_data = send_mock.call_args.args[1]
        metric = MetricModel.from_dict(metric_data)

        self.assertEqual(self.ID, metric.website_checker_id)
        self.assertEqual(status_code, metric.status_code)
        self.assertTrue(metric.is_match)
        self.assertTrue(metric.success)

    @patch('kafka.KafkaProducer.__init__', return_value=None)
    @patch('kafka.KafkaProducer.send')
    @patch('requests.get')
    def test_run_check_fail_if_match_fail(self, request_mock, send_mock, ign):
        status_code = 200

        response = Response()
        response.status_code = status_code
        response._content = "9999".encode("utf-8")

        request_mock.return_value = response

        target = WebsiteChecker(self.WEBSITE_CHECKER_DTO, 10, "", [], None, None, None)

        target.run_check()

        send_mock.assert_called()
        metric_data = send_mock.call_args.args[1]
        metric = MetricModel.from_dict(metric_data)

        self.assertEqual(self.ID, metric.website_checker_id)
        self.assertEqual(status_code, metric.status_code)
        self.assertFalse(metric.is_match)
        self.assertFalse(metric.success)


if __name__ == '__main__':
    unittest.main()

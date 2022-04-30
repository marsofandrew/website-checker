import unittest
from common.database.models import MetricModel
from datetime import datetime


class TestMetricModel(unittest.TestCase):
    ID = "my-id"
    WEBSITE_CHECKER_ID = "website-id"
    STATUS_CODE = 200
    RESPONSE_TIME = 540
    IS_MATCH = False
    DATETIME = datetime(2022, 4, 25, 12, 45, 58)
    SUCCESS = False

    def test_to_dict_success(self):
        metric_model = MetricModel(self.ID, self.WEBSITE_CHECKER_ID, self.STATUS_CODE, self.RESPONSE_TIME,
                                   self.IS_MATCH, self.DATETIME, self.SUCCESS)

        data = metric_model.to_dict()

        self.assertEqual(self.ID, data.get(MetricModel._ID_KEY))
        self.assertEqual(self.WEBSITE_CHECKER_ID, data.get(MetricModel._WEBSITE_CHECKER_ID_KEY))
        self.assertEqual(self.STATUS_CODE, data.get(MetricModel._STATUS_CODE_KEY))
        self.assertEqual(self.RESPONSE_TIME, data.get(MetricModel._RESPONSE_TIME_KEY))
        self.assertEqual(self.IS_MATCH, data.get(MetricModel._IS_MATCH_KEY))
        self.assertEqual(self.SUCCESS, data.get(MetricModel._SUCCESS_KEY))
        self.assertEqual(self.DATETIME.strftime(MetricModel._TIME_FORMAT), data.get(MetricModel._DATE_TIME_KEY))

    def test_from_dict_builds_object(self):
        metric_model = MetricModel(self.ID, self.WEBSITE_CHECKER_ID, self.STATUS_CODE, self.RESPONSE_TIME,
                                   self.IS_MATCH, self.DATETIME, self.SUCCESS)

        data = metric_model.to_dict()

        result = MetricModel.from_dict(data)
        self.assertEqual(metric_model, result)


if __name__ == '__main__':
    unittest.main()

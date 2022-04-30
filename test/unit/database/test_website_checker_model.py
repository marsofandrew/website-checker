import unittest
from common.database.models import WebsiteCheckerModel, AbstractModel


class TestWebsiteCheckerModel(unittest.TestCase):
    ID = "my-id"
    URL = "my-url"
    UPDATE_INTERVAL = 15
    REGEXP_ID = "regexp-id"
    IS_RUN = True

    def test_to_dict_success(self):
        website_checker_model = WebsiteCheckerModel(self.ID, self.URL, self.UPDATE_INTERVAL, self.REGEXP_ID,
                                                    self.IS_RUN)

        data = website_checker_model.to_dict()

        self.assertEqual(self.ID, data.get(WebsiteCheckerModel._ID_KEY))
        self.assertEqual(self.URL, data.get(WebsiteCheckerModel._URL_KEY))
        self.assertEqual(self.UPDATE_INTERVAL, data.get(WebsiteCheckerModel._UPDATE_INTERVAL_KEY))
        self.assertEqual(self.REGEXP_ID, data.get(WebsiteCheckerModel._REGEXP_ID_KEY))
        self.assertEqual(self.IS_RUN, data.get(WebsiteCheckerModel._IS_RUN_KEY))

    def test_from_dict_builds_object(self):
        website_checker_model = WebsiteCheckerModel(self.ID, self.URL, self.UPDATE_INTERVAL, self.REGEXP_ID,
                                                    self.IS_RUN)

        data = website_checker_model.to_dict()

        result = WebsiteCheckerModel.from_dict(data)
        self.assertEqual(website_checker_model, result)


if __name__ == '__main__':
    unittest.main()

import unittest

from common.database.models import RegExpModel


class TestRegExpModelModel(unittest.TestCase):
    ID = "my-id"
    REGEXP = ".*"

    def test_to_dict_success(self):
        regexp_model = RegExpModel(self.ID, self.REGEXP)

        data = regexp_model.to_dict()

        self.assertEqual(self.ID, data.get(RegExpModel._ID_KEY))
        self.assertEqual(self.REGEXP, data.get(RegExpModel._REGEXP_KEY))

    def test_from_dict_builds_object(self):
        regexp_model = RegExpModel(self.ID, self.REGEXP)

        data = regexp_model.to_dict()

        result = RegExpModel.from_dict(data)
        self.assertEqual(regexp_model, result)


if __name__ == '__main__':
    unittest.main()

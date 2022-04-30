class RowStillInUse(Exception):
    def __init__(self, table, details=None):
        self._table = table
        self._details = details

    @property
    def table(self):
        return self._table

    @property
    def details(self):
        return self._details

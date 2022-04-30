from dataclasses import dataclass
from typing import Optional

from common.database.models import WebsiteCheckerModel


@dataclass
class WebsiteCheckerDto:
    website_checker: WebsiteCheckerModel
    regexp: Optional[str]


@dataclass
class WebsiteCheckerRemoveDto:
    _ID_KEY = "id"
    id: str

    @staticmethod
    def from_dict(data):
        return WebsiteCheckerRemoveDto(data[WebsiteCheckerRemoveDto._ID_KEY])

    def to_dict(self):
        return {self._ID_KEY: self.id}

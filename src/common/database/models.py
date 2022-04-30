import abc
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AbstractModel(abc.ABC):
    id: Optional[str]
    _ID_KEY = "id"

    def to_dict(self) -> dict:
        data = self._do_to_dict()
        if not data:
            data = {}
        data.update({self._ID_KEY: self.id})
        return data

    @abc.abstractmethod
    def _do_to_dict(self) -> dict:
        pass


@dataclass
class WebsiteCheckerModel(AbstractModel):
    _URL_KEY = "url"
    _UPDATE_INTERVAL_KEY = "update_interval"
    _REGEXP_ID_KEY = "regexp_id"
    _IS_RUN_KEY = "is_run"

    url: str
    update_interval: int  # in seconds
    regexp_id: Optional[str]
    is_run: bool

    @staticmethod
    def from_dict(data):
        return WebsiteCheckerModel(data.get(AbstractModel._ID_KEY), data.get(WebsiteCheckerModel._URL_KEY),
                                   data.get(WebsiteCheckerModel._UPDATE_INTERVAL_KEY),
                                   data.get(WebsiteCheckerModel._REGEXP_ID_KEY),
                                   data.get(WebsiteCheckerModel._IS_RUN_KEY))

    def _do_to_dict(self) -> dict:
        return {
            self._URL_KEY: self.url,
            self._UPDATE_INTERVAL_KEY: self.update_interval,
            self._REGEXP_ID_KEY: self.regexp_id,
            self._IS_RUN_KEY: self.is_run
        }


@dataclass
class RegExpModel(AbstractModel):
    _REGEXP_KEY = "regexp"

    regexp: str

    @staticmethod
    def from_dict(data):
        return RegExpModel(data.get(AbstractModel._ID_KEY), data.get(RegExpModel._REGEXP_KEY))

    def _do_to_dict(self) -> dict:
        return {self._REGEXP_KEY: self.regexp}


@dataclass
class MetricModel(AbstractModel):
    _WEBSITE_CHECKER_ID_KEY = "website_checker_id"
    _STATUS_CODE_KEY = "status_code"
    _RESPONSE_TIME_KEY = "response_time"
    _IS_MATCH_KEY = "is_match"
    _DATE_TIME_KEY = "date_time"
    _SUCCESS_KEY = "success"

    _TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    website_checker_id: str
    status_code: int
    response_time: Optional[int]  # in milliseconds
    is_match: Optional[bool]
    date_time: Optional[datetime]
    success: bool

    @staticmethod
    def from_dict(data):
        return MetricModel(
            data.get(AbstractModel._ID_KEY), data.get(MetricModel._WEBSITE_CHECKER_ID_KEY),
            data.get(MetricModel._STATUS_CODE_KEY),
            data.get(MetricModel._RESPONSE_TIME_KEY), data.get(MetricModel._IS_MATCH_KEY),
            datetime.strptime(data.get(MetricModel._DATE_TIME_KEY), MetricModel._TIME_FORMAT),
            data.get(MetricModel._SUCCESS_KEY))

    def _do_to_dict(self) -> dict:
        return {
            self._WEBSITE_CHECKER_ID_KEY: self.website_checker_id,
            self._STATUS_CODE_KEY: self.status_code,
            self._RESPONSE_TIME_KEY: self.response_time,
            self._IS_MATCH_KEY: self.is_match,
            self._DATE_TIME_KEY: self.date_time.strftime(self._TIME_FORMAT),
            self._SUCCESS_KEY: self.success
        }

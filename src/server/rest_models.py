from typing import Optional
from dataclasses import dataclass
from common.database.models import WebsiteCheckerModel, RegExpModel
from pydantic import BaseModel


class WebsiteCheckerRestModel(BaseModel):
    url: str
    update_interval: int  # in seconds
    regexp_id: Optional[str] = None
    is_run = True

    def to_model(self):
        return WebsiteCheckerModel(None, self.url, self.update_interval, self.regexp_id, self.is_run)


class RegExpRestModel(BaseModel):
    regexp: str

    def to_model(self):
        return RegExpModel(None, self.regexp)


class CreateResponse(BaseModel):
    id: str

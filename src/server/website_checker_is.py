from common.database.repository.repositories import WebsiteCheckerRepository, RegExpRepository
from common.database.models import WebsiteCheckerModel
from common.dto import WebsiteCheckerDto


class WebsiteCheckerIS:
    _website_checker_repo: WebsiteCheckerRepository
    _regexp_repo: RegExpRepository

    def __init__(self, website_checker_repo, regexp_repo):
        self._website_checker_repo = website_checker_repo
        self._regexp_repo = regexp_repo

    def to_website_checker_dto(self, website_checker_model: WebsiteCheckerModel):
        regexp = None
        if website_checker_model.regexp_id:
            regexp = self._regexp_repo.get(website_checker_model.regexp_id)
            if regexp:
                regexp = regexp.regexp
        return WebsiteCheckerDto(website_checker_model, regexp)

    def get(self, id):
        website_checker = self._website_checker_repo.get(id)
        return self.to_website_checker_dto(website_checker)

    def get_all(self):
        website_checkers = self._website_checker_repo.get_all()
        return [self.to_website_checker_dto(checker) for checker in website_checkers]

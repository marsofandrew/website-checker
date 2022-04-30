from typing import List, Optional

from psycopg2.sql import SQL, Identifier

from common.database.repository.base_repository import BasePostgreSQlRepository
from common.database.models import WebsiteCheckerModel, MetricModel, RegExpModel


class WebsiteCheckerRepository(BasePostgreSQlRepository):
    """
    A class to interact with website_checker table
    """
    def __init__(self, host, port, user, password, dbname, ssl_mode):
        super().__init__("website_checker", host, port, user, password, dbname, ssl_mode)

    def update(self, data: WebsiteCheckerModel) -> str:
        """
        Updates or insert model into a table.
        :param data: WebsiteCheckerModel.
        :return: id of updated object.
        """
        if not data.id:
            return self.insert(data)
        self._run_query(
            lambda cursor: cursor.execute(
                SQL("UPDATE {} SET url=%s, update_interval=%s, regexp_id=%s, is_run=%s WHERE id = %s").format(
                    Identifier(self._table)),
                self._convert_model_to_list(data) + [data.id]))
        return data.id

    def _convert_model_to_list(self, model: WebsiteCheckerModel) -> list:
        return [model.url, model.update_interval, model.regexp_id, model.is_run]

    def _to_model(self, data) -> Optional[WebsiteCheckerModel]:
        if not data:
            return None
        return WebsiteCheckerModel(data["id"], data["url"], data["update_interval"], data["regexp_id"], data["is_run"])

    def _get_column_names(self) -> list:
        return ["url", "update_interval", "regexp_id", "is_run"]


class MetricRepository(BasePostgreSQlRepository):
    """
    A class to interact with metric table
    """
    def __init__(self, host, port, user, password, dbname, ssl_mode):
        super().__init__("metric", host, port, user, password, dbname, ssl_mode)

    def get_by_website_checker_id(self, website_checker_id) -> List[MetricModel]:
        """
        Gets metrics filtered by website_checker_id
        """
        def exec_and_fetch(cursor):
            cursor.execute(
                SQL("SELECT * FROM {} WHERE website_checker_id = %s").format(Identifier(self._table)),
                (website_checker_id,))
            return cursor.fetchall()

        data = self._run_query(exec_and_fetch)
        if not data:
            return []
        return [self._to_model(row) for row in data]

    def remove_by_website_checker_id(self, id: str):
        """
        Removes metrics filtred by website_checker_id
        """
        self._run_query(lambda cursor: cursor.execute(
            SQL("DELETE FROM {} WHERE website_checker_id = %s").format(Identifier(self._table)), (id,)))

    def _convert_model_to_list(self, model: MetricModel) -> list:
        return [model.website_checker_id, model.status_code, model.response_time, model.is_match, model.date_time,
                model.success]

    def _to_model(self, data) -> Optional[MetricModel]:
        if not  data:
            return None
        return MetricModel(data['id'], data['website_checker_id'], data['status_code'], data['response_time'],
                           data['is_match'], data['date_time'], data['success'])

    def _get_column_names(self) -> list:
        return ["website_checker_id", "status_code", "response_time", "is_match", "date_time", "success"]


class RegExpRepository(BasePostgreSQlRepository):
    """
    A class to interact with regexp table
    """
    def __init__(self, host, port, user, password, dbname, ssl_mode):
        super().__init__("regexp", host, port, user, password, dbname, ssl_mode)

    def _convert_model_to_list(self, model: RegExpModel) -> list:
        return [model.regexp]

    def _to_model(self, data) -> Optional[RegExpModel]:
        if not data:
            return None
        return RegExpModel(data['id'], data['regexp'])

    def _get_column_names(self) -> list:
        return ["regexp"]

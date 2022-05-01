import abc
import logging
from typing import List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL, Identifier

from common.database.models import AbstractModel
from common.database.repository.errors import RowStillInUse

_logger = logging.getLogger(__name__)


class RepositoryInterface(abc.ABC):

    @abc.abstractmethod
    def insert(self, model: AbstractModel) -> str:
        """
        Inserts an object into a table
        :param model:  Object to insert
        :return: ID of the object
        """
        pass

    @abc.abstractmethod
    def get(self, id) -> Optional[AbstractModel]:
        """
        Gets single object from DB by ID
        :param id: ID of the object.
        :return: an object from DB
        """
        pass

    @abc.abstractmethod
    def get_all(self) -> List[AbstractModel]:
        """
        :return: All objects from a table.
        """
        pass

    @abc.abstractmethod
    def remove(self, id) -> None:
        """
        Deletes provided object from DB
        :param id:
        :return: None
        """
        pass


class BasePostgreSQlRepository(RepositoryInterface, abc.ABC):

    @staticmethod
    def run_query(connection, cursor_query):
        cursor = None
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            result = cursor_query(cursor)

            connection.commit()
            return result
        except (Exception, psycopg2.Error) as err:
            _logger.error("ERROR: {}".format(err))
            raise err
        finally:
            if connection:
                if cursor:
                    cursor.close()

    def __init__(self, table, host, port, user, password, dbname, sslmode):
        self._table = table
        self._host = host
        self._user = user
        self._password = password
        self._dbname = dbname
        self._port = port
        self._sslmode = sslmode

    def insert(self, model: AbstractModel) -> str:
        def execute_and_fetch(cursor):
            column_names = self._get_column_names()
            insert_string = "INSERT INTO {{0}} ({{1}}) VALUES ({}) RETURNING id".format(
                ",".join(["%s" for _ in column_names]))
            sql_command = SQL(insert_string).format(Identifier(self._table),
                                                    SQL(", ").join([Identifier(row) for row in column_names]))
            cursor.execute(sql_command, self._convert_model_to_list(model))
            return cursor.fetchone().get("id")

        _logger.debug("Try to insert {} to {}".format(model.to_dict(), self._table))

        return self._run_query(execute_and_fetch)

    def get(self, id) -> Optional[AbstractModel]:
        def exec_and_fetch(cursor):
            cursor.execute(SQL("SELECT * FROM {} WHERE id = %s").format(Identifier(self._table)), (id,))
            return cursor.fetchone()
        try:
            query = self._run_query(exec_and_fetch)
            return self._to_model(query)
        except psycopg2.errors.InvalidTextRepresentation as err:
            _logger.error("ERROR: {}".format(err))
            return None

    def get_all(self) -> List[AbstractModel]:
        def execute_and_fetch(cursor):
            cursor.execute(SQL("SELECT * FROM {}").format(Identifier(self._table)))
            return cursor.fetchall()

        data = self._run_query(execute_and_fetch)
        if not data:
            return []
        return [self._to_model(row) for row in data]

    def remove(self, id) -> None:
        try:
            self._run_query(
                lambda cursor: cursor.execute(SQL("DELETE FROM {} WHERE id = %s").format(Identifier(self._table)),
                                              (id,)))
        except psycopg2.errors.ForeignKeyViolation as err:
            raise RowStillInUse(self._table, err)

    @abc.abstractmethod
    def _convert_model_to_list(self, dto: AbstractModel) -> list:
        """
        Converts model to a list of values
        :param dto: model
        :return: a list of values
        """
        pass

    @abc.abstractmethod
    def _to_model(self, data) -> Optional[AbstractModel]:
        """
        Converts DB row to a model
        :param data: DB row
        :return: Model
        """
        pass

    @abc.abstractmethod
    def _get_column_names(self) -> list:
        """
        :return: Column names to inert
        """
        pass

    def _run_query(self, cursor_query):
        conn = None
        try:
            conn = psycopg2.connect(host=self._host, port=self._port, user=self._user, password=self._password,
                                    dbname=self._dbname,
                                    sslmode=self._sslmode)
            return BasePostgreSQlRepository.run_query(conn, cursor_query)
        finally:
            if conn:
                conn.close()

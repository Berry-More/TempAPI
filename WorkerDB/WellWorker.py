import psycopg2
from psycopg2.extras import DictCursor
from dataclasses import dataclass

from WorkerDB.constants import DBNAME, USER, PASSWORD, HOST, DATA_TAB, WELL_TAB


@dataclass
class Well:
    id: int
    name: str
    latitude: float
    longitude: float
    interval_start: float
    interval_end: float
    interval_value: float
    status: str


class WellWorker:
    def __init__(self):
        pass

    @staticmethod
    def post_well(data: Well):

        """
        :param data: class Well
        """

        request_sql = """
        INSERT INTO {0} (name, latitude, longitude, interval_start, interval_end, interval_value, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s);""".format(WELL_TAB)
        request_data = (
            data.name, data.latitude, data.longitude, data.interval_start,
            data.interval_end, data.interval_value, data.status
        )

        with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(request_sql, request_data)

    @staticmethod
    def delete_well(well_id: int):

        """
        :param well_id: well id in database
        """

        request_sql = """
        DELETE FROM {0}
        WHERE id = {1};
        """.format(WELL_TAB, well_id)

        with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(request_sql)

    @staticmethod
    def get_wells() -> list[Well]:

        """
        :return: list of Well objects
        """

        try:
            result = []
            request_sql = """
            SELECT id, name, latitude, longitude, interval_start, interval_end, interval_value, status
            FROM {0};
            """.format(WELL_TAB)

            with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute(request_sql)
                    get_result = cursor.fetchall()

                    if len(get_result) == 0:
                        return result
                    else:
                        for i in get_result:
                            result.append(
                                Well(id=i[0], name=i[1], latitude=i[2], longitude=i[3],
                                     interval_start=i[4], interval_end=i[5], interval_value=i[6], status=i[7])
                            )
            return result

        except psycopg2.OperationalError:
            raise ConnectionError('Unable to connect to database')

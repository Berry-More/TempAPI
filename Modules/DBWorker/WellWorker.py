import psycopg2
from psycopg2.extras import DictCursor
from dataclasses import asdict
from flask import request

from Modules.constants import DBNAME, USER, PASSWORD, HOST, WELL_TAB
from Modules.Data.Well import Well


class WellWorker:
    def __init__(self):
        pass

    @staticmethod
    def request_to_well(post_request: request) -> Well:
        well = Well(
            id=0,
            name=post_request.json['name'],
            latitude=post_request.json['latitude'],
            longitude=post_request.json['longitude'],
            interval_start=post_request.json['interval_start'],
            interval_end=post_request.json['interval_end'],
            interval_value=post_request.json['interval_value'],
            status=post_request.json['status']
        )
        return well

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
    def get_wells() -> list[dict]:

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
                            well_object = Well(id=i[0], name=i[1], latitude=i[2], longitude=i[3],
                                               interval_start=i[4], interval_end=i[5], interval_value=i[6], status=i[7])
                            result.append(asdict(well_object))
            return result

        except psycopg2.OperationalError:
            raise ConnectionError('Unable to connect to database')

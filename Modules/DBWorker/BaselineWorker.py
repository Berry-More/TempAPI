import psycopg2
import numpy as np
from psycopg2 import sql
from psycopg2.extras import DictCursor

from Modules.constants import DBNAME, USER, PASSWORD, HOST, BASELINE_TAB
from Modules.Data.DataArray import DataArray


class BaselineWorker:

    def __init__(self):
        pass

    @staticmethod
    def _sql_select(well_name: str) -> np.array:
        with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                select = """
                SELECT depth, temp
                FROM {0}
                WHERE place = '{1}'
                ORDER BY depth
                """.format(BASELINE_TAB, well_name)

                cursor.execute(select)
                current_data = cursor.fetchall()
                return np.array(current_data).T

    @staticmethod
    def get(well_name: str) -> DataArray:
        data = BaselineWorker._sql_select(well_name)
        data_object = DataArray(time=0, depth=data[0], temp=data[1], place=well_name)
        return data_object

    @staticmethod
    def _data_array_to_db_format(data: DataArray) -> list:
        values = []
        for i in range(len(data.depth)):
            values.append(
                (data.depth[i], data.temp[i], data.place)
            )
        return values

    @staticmethod
    def _sql_delete(well_name: str):
        with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                delete = f"DELETE FROM {BASELINE_TAB} WHERE place = '{well_name}'"
                cursor.execute(delete)

    @staticmethod
    def _sql_insert(values: list):
        with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                insert_string = f'INSERT INTO {BASELINE_TAB} (depth, temp, place)\nVALUES ' + '{}'
                insert = sql.SQL(insert_string).format(sql.SQL(',').join(map(sql.Literal, values)))
                cursor.execute(insert)

    @staticmethod
    def update(data: DataArray):
        BaselineWorker._sql_delete(data.place)
        values = BaselineWorker._data_array_to_db_format(data)
        BaselineWorker._sql_insert(values)

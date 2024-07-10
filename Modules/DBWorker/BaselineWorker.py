import lasio
import psycopg2
import numpy as np
from psycopg2 import sql
from psycopg2.extras import DictCursor
from datetime import datetime

from Modules.constants import DBNAME, USER, PASSWORD, HOST, BASELINE_TAB, WELL_TAB
from Modules.Data.DataArray import DataArray


class BaselineWorker:

    def __init__(self):
        pass

    @staticmethod
    def _get_date_from_las(las_file: lasio.las.LASFile) -> float:
        time = None
        for info in las_file.header['Well']:
            if info.mnemonic == 'DATE':
                time = datetime.strptime(info.value, '%d.%m.%Y %H-%M-%S').timestamp()
                break
        return time

    @staticmethod
    def _get_well_name_by_id(well_id: int) -> str:
        with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                select = f'SELECT name FROM {WELL_TAB} WHERE id = {well_id}'
                cursor.execute(select)
                well_name = cursor.fetchall()[0][0]
                return well_name

    @staticmethod
    def read_lasio(las_string: str, well_id: int) -> DataArray:
        las_file = lasio.read(las_string)

        temp = las_file.get_curve('TEMP').data
        depth = las_file.get_curve('DEPTH').data
        well_name = BaselineWorker._get_well_name_by_id(well_id)
        time = BaselineWorker._get_date_from_las(las_file)

        data_array = DataArray(time=time, temp=temp, depth=depth, place=well_name)

        return data_array

    @staticmethod
    def _sql_select(well_name: str, interval_start: float, interval_end: float) -> np.array:
        with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                select = """
                SELECT depth, temp, time
                FROM {0}
                WHERE place = '{1}' AND depth >= {2} AND depth <= {3}
                ORDER BY depth
                """.format(BASELINE_TAB, well_name, interval_start, interval_end)

                cursor.execute(select)
                current_data = cursor.fetchall()
                return np.array(current_data).T

    @staticmethod
    def get(well_name: str, interval_start: float, interval_end: float) -> DataArray:
        data = BaselineWorker._sql_select(well_name, interval_start, interval_end)
        data_object = DataArray(time=data[2][0], depth=list(data[0] - min(data[0])), temp=list(data[1]), place=well_name)
        return data_object

    @staticmethod
    def _data_array_to_db_format(data: DataArray) -> list:
        values = []
        for i in range(len(data.depth)):
            values.append(
                (data.depth[i], data.temp[i], data.place, data.time)
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
                insert_string = f'INSERT INTO {BASELINE_TAB} (depth, temp, place, time)\nVALUES ' + '{}'
                insert = sql.SQL(insert_string).format(sql.SQL(',').join(map(sql.Literal, values)))
                cursor.execute(insert)

    @staticmethod
    def update(data: DataArray):
        BaselineWorker._sql_delete(data.place)
        values = BaselineWorker._data_array_to_db_format(data)
        BaselineWorker._sql_insert(values)

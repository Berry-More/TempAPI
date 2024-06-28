import psycopg2
import numpy as np
from psycopg2.extras import DictCursor
from dataclasses import asdict

from Modules.constants import DBNAME, USER, PASSWORD, HOST, DATA_TAB
from Modules.Data.DataArray import DataArray


class DataWorker:
    def __init__(self):
        pass

    @staticmethod
    def _get_raw_last_data(well_name: str) -> list:

        """
        :param well_name: string with well name
        :return: last data array like list with list[time, depth, temperature]
        """

        try:
            with psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    select = """
                            SELECT DISTINCT time, depth, temp
                            FROM {0}
                            WHERE time = (SELECT MAX(time) FROM {0} WHERE place = '{1}') AND place = '{1}'
                            ORDER BY depth
                            """.format(DATA_TAB, well_name)
                    cursor.execute(select)
                    result = cursor.fetchall()
                    return result
        except psycopg2.OperationalError:
            raise ConnectionError('Unable to connect to database')

    @staticmethod
    def _process_raw_last_data(raw_data: list, well_name: str) -> DataArray:
        trans_data = np.array(raw_data).T
        data_object = DataArray(
            time=trans_data[0][0],
            depth=list(trans_data[1]),
            temp=list(trans_data[2]),
            place=well_name
        )
        return data_object

    @staticmethod
    def get_last_data(well_name: str) -> DataArray:
        raw_data = DataWorker._get_raw_last_data(well_name)
        data_object = DataWorker._process_raw_last_data(raw_data, well_name)
        return data_object

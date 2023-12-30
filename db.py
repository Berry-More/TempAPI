import psycopg2
import numpy as np
import pandas as pd

from psycopg2 import sql
from psycopg2.extras import DictCursor


class WorkerDB:

    """
    Class for work with database
    """

    dbname = 'holedb'
    user = 's_ponasenko'
    password = 'Vdycm-8w3uZ'
    host = 'localhost'
    tab = 'holedb_schema.dts'

    def post_data(self, data: dict):

        """
        :param data: dict with keys ['time', 'depth', 'temp', 'place']
        :return: None

        Post temperature data to the database
        """

        if len(data['depth']) > 0:
            values = []
            for i in range(len(data['depth'])):
                values.append(
                    (data['time'],
                     data['depth'][i],
                     data['temp'][i],
                     data['place'])
                )

            with psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    insert = sql.SQL('''
                    INSERT INTO {} (time, depth, temp, place) 
                    VALUES '''.format(self.tab) + '{}').format(sql.SQL(',').join(map(sql.Literal, values)))
                    cursor.execute(insert)

    def get_data(
            self,
            time_start: float,
            time_end: float,
            place: str,
            depth_min: float,
            depth_max: float
    ) -> dict[str, list]:

        try:
            with psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    select = """
                    SELECT DISTINCT time, depth, temp
                    FROM {0}
                    WHERE time > {1} AND time < {2} AND place = '{3}' AND depth >= {4} AND depth <= {5};
                    """.format(self.tab, time_start, time_end, place, depth_min, depth_max)
                    cursor.execute(select)
                    result = np.array(cursor.fetchall()).T

                    if len(result) == 0:
                        raise FileNotFoundError('No data in the selected interval')

                    num_of_measurements = np.count_nonzero(result[1] == float(depth_min))
                    data_dict = {'time': result[0], 'depth': result[1], 'temp': result[2]}
                    df = pd.DataFrame(data_dict).sort_values(['time', 'depth'])
                    numpy_data = df.to_numpy()

                    if len(numpy_data) % num_of_measurements != 0:
                        raise ValueError('Bad matrix length')

                    output_data = np.reshape(
                        numpy_data.T,
                        (3, num_of_measurements, int(len(numpy_data) / num_of_measurements))
                    )

                    return dict(time=output_data[0].T[0].tolist(),
                                depth=output_data[1][0].tolist(),
                                temp=output_data[2].T.tolist())

        except psycopg2.OperationalError:
            raise ConnectionError('Unable to connect to database')

    def get_places(self) -> list[str]:

        """
        :return: list

        Get all wells names there are in database
        """

        try:
            with psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    select = """
                    SELECT DISTINCT place
                    FROM {0}
                    """.format(self.tab)
                    cursor.execute(select)
                    result = cursor.fetchall()

                    if len(result) == 0:
                        raise ValueError('No wells available')
                    else:
                        return sum(result, [])

        except psycopg2.OperationalError:
            raise ConnectionError('Unable to connect to database')

    def get_max_depth(self, time_start: float, time_end: float, place: str) -> float:
        """
        :param time_start: float
        :param time_end: float
        :param place: str
        :return: float

        Get maximum allowed depth value
        """
        try:
            with psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    select = """
                    SELECT DISTINCT MAX(depth)
                    FROM {0}
                    WHERE time > {1} AND time < {2} AND place = '{3}'
                    GROUP BY time;
                    """.format(self.tab, time_start, time_end, place)
                    cursor.execute(select)
                    result = cursor.fetchall()
                    return min(result)[0]

        except psycopg2.OperationalError:
            raise ConnectionError('Unable to connect to database')

    def get_min_depth(self, time_start: float, time_end: float, place: str) -> float:
        """
        :param time_start: float
        :param time_end: float
        :param place: str
        :return: float

        Get minimum allowed depth value
        """
        try:
            with psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    select = """
                    SELECT DISTINCT MIN(depth)
                    FROM {0}
                    WHERE time > {1} AND time < {2} AND place = '{3}'
                    GROUP BY time;
                    """.format(self.tab, time_start, time_end, place)
                    cursor.execute(select)
                    result = cursor.fetchall()
                    return max(result)[0]

        except psycopg2.OperationalError:
            raise ConnectionError('Unable to connect to database')

    def get_times(self, time_start: float, time_end: float, place: str) -> np.array:

        """
        :param time_start: float (timestamp)
        :param time_end: float (timestamp)
        :param place: str
        :return: np.array
        """

        try:
            with psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    select = """
                    SELECT DISTINCT time
                    FROM {0}
                    WHERE time > {1} AND time < {2} AND place = '{3}';
                    """.format(self.tab, time_start, time_end, place)
                    cursor.execute(select)
                    result = cursor.fetchall()

                    if len(result) == 0:
                        raise ValueError('No data for the selected time period')
                    else:
                        return np.array(result).T[0]

        except psycopg2.OperationalError:
            raise ConnectionError('Unable to connect to database')


dataBase = WorkerDB()

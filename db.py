import psycopg2
import numpy as np

from psycopg2 import sql
from psycopg2.extras import DictCursor


class WorkerDB:

    """
    Class for work with database
    """

    dbname = 'holedb'
    user = 's_ponasenko'
    password = 'Vdycm-8w3uZ'
    host = '84.237.52.212'
    tab = 'holedb_schema.dts'
    tab_well = 'holedb_schema.well'

    def post_data(self, data: dict):

        """
        :param data: dictionary with time value, depth array, temperature array and place value
        :return: None
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

    def get_data(self, time_start: float, time_end: float, place: str,
                 depth_min: float, depth_max: float) -> dict[str: list]:

        """
        :param time_start: time in timestamp format
        :param time_end: time in timestamp format
        :param place: well name
        :param depth_min: minimal allowed depth value
        :param depth_max: maximal allowed depth value
        :return: dict with temperature matrix, list of depth and list of times in timestamp format
        """

        try:
            with psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    select = """
                    SELECT DISTINCT time, depth, temp
                    FROM {0}
                    WHERE time > {1} AND time < {2} AND place = '{3}' AND depth >= {4} AND depth <= {5}
                    ORDER BY time, depth""".format(self.tab, time_start, time_end, place, depth_min, depth_max)
                    cursor.execute(select)
                    result = np.array(cursor.fetchall())

                    if len(result) == 0:
                        raise FileNotFoundError('No data in the selected interval')

                    num_of_measurements = np.count_nonzero(result.T[1] == float(depth_min))
                    if len(result) % num_of_measurements != 0:
                        raise ValueError('Bad matrix length')

                    output_data = np.reshape(
                        result.T,
                        (3, num_of_measurements, int(len(result) / num_of_measurements))
                    )

                    return dict(time=output_data[0].T[0].tolist(),
                                depth=output_data[1][0].tolist(),
                                temp=output_data[2].T.tolist())

        except psycopg2.OperationalError:
            raise ConnectionError('Unable to connect to database')

    def get_places(self) -> list[str]:

        """
        :return: list with all names of wells
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

    def post_well(self, data: dict):

        """
        :param data: dictionary with information about well
        """

        with psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                INSERT INTO {0} (name, latitude, longitude, interval_start, interval_end, interval_value, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """.format(self.tab_well), (data['name'], data['latitude'], data['longitude'], data['interval_start'],
                                            data['interval_end'], data['interval_value'], data['status']))

    def delete_well(self, well_id: int):

        """
        :param well_id: well id in database
        """

        with psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                DELETE FROM {0}
                WHERE id = {1};
                """.format(self.tab_well, well_id))

    def get_wells(self) -> list[dict]:

        """
        :return: list of dictionaries with information about all wells
        """

        try:
            result = []
            with psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, name, latitude, longitude, interval_start, interval_end, interval_value, status
                        FROM {0};
                        """.format(self.tab_well))
                    get_result = cursor.fetchall()

                    if len(get_result) == 0:
                        return result
                    else:
                        for i in get_result:
                            result.append(
                                {'id': i[0], 'name': i[1], 'latitude': i[2], 'longitude': i[3], 'interval_start': i[4],
                                 'interval_end': i[5], 'interval_value': i[6], 'status': i[7]})
            return result

        except psycopg2.OperationalError:
            raise ConnectionError('Unable to connect to database')

    def get_max_depth(self, time_start: float, time_end: float, place: str) -> float:

        """
        :param time_start: time in timestamp format
        :param time_end: time in timestamp format
        :param place: well name
        :return: maximal allowed depth value
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
        :param time_start: time in timestamp format
        :param time_end: time in timestamp format
        :param place: well name
        :return: minimal allowed depth value
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


dataBase = WorkerDB()

import pandas as pd
from database import DatabaseConnection, FourmonthDatabase

class FourmonthData:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.df = pd.read_csv('fourmonthData.csv', encoding='utf-8', delimiter=',')
        self.df.fillna(value=self.df.mean(numeric_only=True), inplace=True)

        # 열 이름 설정
        self.df.columns = [
            'station_id', 'date', 'avg_wind_speed', 'avg_pressure', 'avg_humidity',
            'avg_temp', 'avg_water_temp', 'avg_max_wave_height', 'avg_significant_wave_height',
            'max_significant_wave_height', 'max_max_wave_height', 'avg_wave_period',
            'max_wave_period', 'salinity'
        ]

    def insert_data(self):
        insert_query = """
        INSERT INTO weather_data (
            station_id, date, avg_wind_speed, avg_pressure, avg_humidity, avg_temp,
            avg_water_temp, avg_max_wave_height, avg_significant_wave_height,
            max_significant_wave_height, max_max_wave_height, avg_wave_period,
            max_wave_period, salinity
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        with self.db_connection.connection.cursor() as cursor:
            for _, row in self.df.iterrows():
                cursor.execute(insert_query, (
                    row['station_id'],
                    row['date'],
                    row['avg_wind_speed'],
                    row['avg_pressure'],
                    row['avg_humidity'],
                    row['avg_temp'],
                    row['avg_water_temp'],
                    row['avg_max_wave_height'],
                    row['avg_significant_wave_height'],
                    row['max_significant_wave_height'],
                    row['max_max_wave_height'],
                    row['avg_wave_period'],
                    row['max_wave_period'],
                    row['salinity']
                ))
        self.db_connection.connection.commit()

if __name__ == "__main__":
    db_connection = DatabaseConnection(host="localhost", user="root", password="1234", database="mysql")
    db_connection.connect()

    weather_db = FourmonthDatabase(db_connection)
    weather_db.create_table()

    data_info = FourmonthData(db_connection)
    data_info.insert_data()

    db_connection.disconnect()

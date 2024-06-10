from database import DatabaseConnection

class DataFetcher:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def fetch_data(self):
        query = """
            SELECT 
                w.date,
                w.avg_humidity,
                w.salinity,
                w.avg_pressure,
                w.avg_temp,
                w.avg_water_temp,
                w.avg_wind_speed,
                b.growth_rate
            FROM 
                weather_data w
            JOIN 
                bestdate_info b ON w.date = b.time_stamp;
        """
        result = self.db_connection.execute_query(query)
        return result

if __name__ == "__main__":
    db_connection = DatabaseConnection(host="localhost", user="root", password="1234", database="mysql")
    db_connection.connect()
    
    data_fetcher = DataFetcher(db_connection)
    weather_data = data_fetcher.fetch_weather_data()
    
    db_connection.disconnect()
import mysql.connector

class DatabaseConnection:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
    
    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.connection.cursor()
        
    def execute_query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def disconnect(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            self.connection = None
            self.cursor = None


class RadiationTestDatabase:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def create_table(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS radiation_test_data  (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_name VARCHAR(255),
                sample_date DATE,
                collection_location VARCHAR(255),
                cesium_detection VARCHAR(255),
                iodine_detection VARCHAR(255),
                judgement VARCHAR(255),
                investigating_agency VARCHAR(255)
            )
            """
        self.db_connection.cursor.execute(create_table_query)
        self.db_connection.connection.commit()

class BuoyDatabase:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def create_table(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS buoy_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                predicted_weight FLOAT NOT NULL,
                harvest_date DATE NOT NULL
            )
            """
        self.db_connection.cursor.execute(create_table_query)
        self.db_connection.connection.commit()
        
class NewsDatabase:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def create_table(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS news (
                    title VARCHAR(255) NOT NULL,
                    link VARCHAR(255) NOT NULL
            )
            """
        self.db_connection.cursor.execute(create_table_query)
        self.db_connection.connection.commit()

class PriceDatabase:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def create_table(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS price_data (
                    species TEXT,
                    origin TEXT,
                    size TEXT,
                    packaging TEXT,
                    quantity INTEGER,
                    weight REAL,
                    highest_bid INTEGER,
                    lowest_bid INTEGER,
                    average_bid INTEGER
            )
            """
        self.db_connection.cursor.execute(create_table_query)
        self.db_connection.connection.commit()
        
class FourmonthDatabase:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def create_table(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS weather_data (
                station_id INT,
                date DATE,
                avg_wind_speed FLOAT,
                avg_pressure FLOAT,
                avg_humidity FLOAT,
                avg_temp FLOAT,
                avg_water_temp FLOAT,
                avg_max_wave_height FLOAT,
                avg_significant_wave_height FLOAT,
                max_significant_wave_height FLOAT,
                max_max_wave_height FLOAT,
                avg_wave_period FLOAT,
                max_wave_period FLOAT,
                salinity FLOAT
            )
            """
        self.db_connection.cursor.execute(create_table_query)
        self.db_connection.connection.commit()

class WeatherDatabase:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def create_table(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS weather_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                time_stamp DATE,
                weather_condition VARCHAR(50),
                humidity VARCHAR(20),
                precipitation VARCHAR(20),
                temperature VARCHAR(20),
                wind_direction VARCHAR(20),
                wind_speed VARCHAR(20)
            )
        """
        self.db_connection.cursor.execute(create_table_query)
        self.db_connection.connection.commit()

class SeaDatabase:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def create_table(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS sea_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                time_stamp DATE,
                wind_speed FLOAT,
                wave_height FLOAT,
                risk_level VARCHAR(10)
            )
        """
        self.db_connection.cursor.execute(create_table_query)
        self.db_connection.connection.commit()
        
class BestdateDatabase:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def create_table(self):
        # 여기에 새로운 테이블 생성 쿼리를 작성하세요
        create_table_query = """
            CREATE TABLE IF NOT EXISTS bestdate_info (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                time_stamp DATE,
                weight FLOAT,
                growth_rate FLOAT
            )
        """
        self.db_connection.cursor.execute(create_table_query)
        self.db_connection.connection.commit()


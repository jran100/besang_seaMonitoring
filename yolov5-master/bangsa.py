import pandas as pd
from database import DatabaseConnection, RadiationTestDatabase

class RadiationTestData:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.df = pd.read_csv('bangsa.csv', encoding='utf-8')
        self.df.fillna(value=self.df.mean(numeric_only=True), inplace=True)

        self.df.columns = [
            'product_name', 'sample_date', 'collection_location', 'cesium_detection',
            'iodine_detection', 'judgement', 'investigating_agency'
        ]

    def insert_data(self):
        insert_query = """
        INSERT INTO radiation_test_data (
            product_name, sample_date, collection_location, cesium_detection,
            iodine_detection, judgement, investigating_agency
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        with self.db_connection.connection.cursor() as cursor:
            for _, row in self.df.iterrows():
                cursor.execute(insert_query, (
                    row['product_name'],
                    row['sample_date'],
                    row['collection_location'],
                    row['cesium_detection'],
                    row['iodine_detection'],
                    row['judgement'],
                    row['investigating_agency']
                ))
        self.db_connection.connection.commit()

if __name__ == "__main__":
    db_connection = DatabaseConnection(host="localhost", user="root", password="1234", database="mysql")
    db_connection.connect()

    radiation_data = RadiationTestDatabase(db_connection)
    radiation_data.create_table()

    data_info = RadiationTestData(db_connection)
    data_info.insert_data()

    db_connection.disconnect()

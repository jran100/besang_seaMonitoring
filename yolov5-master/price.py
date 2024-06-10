import pandas as pd
from database import DatabaseConnection, PriceDatabase

class PriceData:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.df = pd.read_csv('price.csv', encoding='utf-8', delimiter=',')
        self.df.fillna(value=self.df.mean(numeric_only=True), inplace=True)

        # 열 이름 설정
        self.df.columns = [
            'species', 'origin', 'size', 'packaging', 'quantity',
            'weight', 'highest_bid', 'lowest_bid', 'average_bid'
        ]

    def insert_data(self):
        insert_query = """
        INSERT INTO price_data (
            species, origin, size, packaging, quantity, weight,
            highest_bid, lowest_bid, average_bid
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        with self.db_connection.connection.cursor() as cursor:
            for _, row in self.df.iterrows():
                cursor.execute(insert_query, (
                    row['species'],
                    row['origin'],
                    row['size'],
                    row['packaging'],
                    row['quantity'],
                    row['weight'],
                    row['highest_bid'],
                    row['lowest_bid'],
                    row['average_bid']
                ))
        self.db_connection.connection.commit()

if __name__ == "__main__":
    db_connection = DatabaseConnection(host="localhost", user="root", password="1234", database="mysql")
    db_connection.connect()

    price_db = PriceDatabase(db_connection)
    price_db.create_table()

    data_info = PriceData(db_connection)
    data_info.insert_data()

    db_connection.disconnect()

# app.py
from flask import Flask, jsonify, render_template
from datetime import datetime
from database import DatabaseConnection,WeatherDatabase,SeaDatabase,BestdateDatabase,NewsDatabase,PriceDatabase,RadiationTestDatabase
from fetch import DataFetcher

db_connection = DatabaseConnection(host="localhost", user="root", password="1234", database="mysql")
db_connection.connect()
news_db = NewsDatabase(db_connection)
price_db = PriceDatabase(db_connection)
sea_db = SeaDatabase(db_connection)
bestdate_db = BestdateDatabase(db_connection)
weather_db = WeatherDatabase(db_connection)
radiate_db = RadiationTestDatabase(db_connection)
data_fetcher = DataFetcher(db_connection)




app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page1')
def page1():
    return render_template('page1.html')

@app.route('/weather_data')
def weather_data():
    weather_data = data_fetcher.fetch_data()
    return jsonify(weather_data)

@app.route('/buoy_data')
def buoy_data():
    buoy_query = "SELECT * FROM buoy_info ORDER BY id DESC LIMIT 1"
    buoy_data = db_connection.execute_query(buoy_query)
    return jsonify(buoy_data)
    
@app.route('/page2')
def page2():
    news_query = "SELECT title, link FROM news"
    news_data = db_connection.execute_query(news_query)
    price_query = "SELECT * FROM price_data"
    price_data = db_connection.execute_query(price_query)
    buoy_query = "SELECT * FROM buoy_info ORDER BY id DESC LIMIT 1"
    buoy_data = db_connection.execute_query(buoy_query)
    return render_template('page4.html', news_data=news_data, price_data=price_data, buoy_data=buoy_data)

@app.route('/page3')
def page3():
    sea_query = " SELECT * FROM sea_info ORDER BY id DESC LIMIT 1"
    sea_data = db_connection.execute_query(sea_query)
    weather_query = "SELECT * FROM weather_info ORDER BY id DESC LIMIT 1"
    weather_data = db_connection.execute_query(weather_query)
    departure_risk=sea_data[0][4]
    bangsa_query = """
                    SELECT *
                    FROM radiation_test_data AS r
                    WHERE r.id IN (
                        SELECT MIN(id)
                        FROM radiation_test_data
                        WHERE product_name IN ('전복', '굴', '가리비패각')
                        GROUP BY sample_date, product_name
                    )
                    AND r.product_name IN ('전복', '굴', '가리비패각')
                    ORDER BY id ASC
                    LIMIT 5;
                    """
    bangsa_data = db_connection.execute_query(bangsa_query)
    print(departure_risk)
    return render_template('page3.html', sea_data=sea_data, weather_data=weather_data, departure_risk=departure_risk, bangsa_data=bangsa_data)

if __name__ == '__main__':
    app.run(debug=True)
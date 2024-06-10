from database import DatabaseConnection
import matplotlib.pyplot as plt

def fetch_weather_data():
    query = """
        SELECT 
            w.date,
            w.salinity,
            b.growth_rate
        FROM 
            weather_data w
        JOIN 
            bestdate_info b ON w.date = b.time_stamp;
    """
    result = db_connection.execute_query(query)
    return result

if __name__ == "__main__":
    db_connection = DatabaseConnection(host="localhost", user="root", password="1234", database="mysql")
    db_connection.connect()
    weather_data = fetch_weather_data()
    db_connection.disconnect()

    dates = [row[0] for row in weather_data]
    salinities = [row[1] for row in weather_data]
    growth_rates = [row[2] for row in weather_data]

    # 염분 변화량과 생장률 변화량을 동시에 그래프에 표시
    plt.figure(figsize=(10, 5))

    plt.plot(dates, salinities, marker='o', color='b', label='Salinity')
    plt.plot(dates, growth_rates, marker='s', color='r', label='Growth Rate')

    plt.title('Salinity and Growth Rate Changes Over Time')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

from database import DatabaseConnection
import matplotlib.pyplot as plt

def fetch_weather_data():
    query = """
        SELECT 
            w.date,
            w.avg_temp,
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
    temperatures = [row[1] for row in weather_data]
    growth_rates = [row[2] for row in weather_data]

    fig, ax1 = plt.subplots(figsize=(10, 5))

    color = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Average Temperature', color=color)
    ax1.plot(dates, temperatures, marker='o', color=color, label='Average Temperature')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Growth Rate', color=color)
    ax2.plot(dates, growth_rates, marker='s', color=color, label='Growth Rate')
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.title('Average Temperature and Growth Rate Changes Over Time')
    plt.xticks(rotation=45)
    fig.legend(loc='upper left')
    plt.grid(True)
    plt.show()

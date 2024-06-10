import requests
from bs4 import BeautifulSoup
from datetime import datetime

class WeatherPredictor:
    def __init__(self):
        self.base_url = "https://www.weatheri.co.kr/forecast/forecast01.php?mNum=1&sNum=1&n=n1"
        self.temp_url_template = "https://www.badatime.com/temp_past.jsp?idx=41&param=DT_0014&date1={year}-{month}"
        self.current_date = datetime.now()
        self.current_month = self.current_date.strftime("%m")
        self.current_day = self.current_date.day

    def process_table_rain(self, table):
        rows = table.find_all("tr")
        if len(rows) >= 6:
            row = rows[5]
            values = [value.strip() for value in row.text.strip().split()]
            total = sum(float(value) for value in values[1:] if value and value != 'null')
            return total
        else:
            return None

    def process_table_wind(self, table):
        rows = table.find_all("tr")
        if len(rows) >= 6:
            row = rows[6]
            values = [value.strip() for value in row.text.strip().split()]
            total = sum(float(value) for value in values[1:] if value and value != 'null')
            avg = total / 8
            return avg
        else:
            return None

    def fetch_rain_data(self):
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, "html.parser")

        predicted_rain = []
        for i in range(1, 11):
            table_id = f"t{i}"
            table = soup.find("table", {"id": table_id})
            if table:
                precipitation_sum = self.process_table_rain(table)
                if precipitation_sum is not None:
                    predicted_rain.append(precipitation_sum)
        return predicted_rain

    def fetch_wind_data(self):
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, "html.parser")

        wind_avg = []
        for i in range(1, 11):
            table_id = f"t{i}"
            table = soup.find("table", {"id": table_id})
            if table:
                wind = self.process_table_wind(table)
                if wind is not None:
                    wind_avg.append(wind)
        return wind_avg

    def fetch_temperature_data(self, year):
        temp_url = self.temp_url_template.format(year=year, month=self.current_month)
        response = requests.get(temp_url)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find('table', {'id': 'table1'})

        min_temps = []
        max_temps = []

        if (30 - self.current_day) >= 10:
            rows = table.find_all('tr')[self.current_day:self.current_day + 10]
        else:
            rows = table.find_all('tr')[self.current_day:31]
            next_month = (int(self.current_month) % 12) + 1
            next_month = f'{next_month:02d}'
            temp_url = self.temp_url_template.format(year=year, month=next_month)
            response = requests.get(temp_url)
            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find('table', {'id': 'table1'})
            rows.extend(table.find_all('tr')[1:31 - self.current_day])

        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 5:
                min_value = float(cells[2].text.strip().replace('℃', ''))
                max_value = float(cells[4].text.strip().replace('℃', ''))
                min_temps.append(min_value)
                max_temps.append(max_value)

        avg_temps = [round((min_temp + max_temp) / 2, 2) for min_temp, max_temp in zip(min_temps, max_temps)]
        return avg_temps

    def predict_temperature_change_rate(self):
        avg_2023 = self.fetch_temperature_data(2023)
        avg_2022 = self.fetch_temperature_data(2022)
        avg_2021 = self.fetch_temperature_data(2021)

        a = avg_2023[-1] - avg_2023[0]
        b = avg_2022[-1] - avg_2022[0]
        c = avg_2021[-1] - avg_2021[0]

        change_rate = (a + b + c) / 3 / len(avg_2023)
        return change_rate

    def get_real_time_temperature(self):
        temp_url = self.temp_url_template.format(year=2023, month=self.current_month)
        response = requests.get(temp_url)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find('table', {'id': 'table1'})

        row = table.find_all('tr')[1]
        if row:
            cells = row.find_all('td')
            if len(cells) >= 5:
                value_1 = float(cells[2].text.strip().replace(" ℃", ""))
                value_2 = float(cells[4].text.strip().replace(" ℃", ""))
                today_temp = (value_1 + value_2) / 2
                return round(today_temp, 2)
        return None

    def predict_future_temperatures(self):
        change_rate = self.predict_temperature_change_rate()
        real_time_temp = self.get_real_time_temperature()

        predicted_temp = []
        for _ in range(9):
            real_time_temp += change_rate
            predicted_temp.append(round(real_time_temp, 2))

        return predicted_temp

    def predict_algae_bloom(self):
        predicted_temp = self.predict_future_temperatures()
        predicted_rain = self.fetch_rain_data()
        wind_avg = self.fetch_wind_data()

        count = 0
        for i in range(len(predicted_temp)):
            if 20 <= predicted_temp[i] <= 30:
                if 24.4 <= predicted_rain[i] <= 54.5:
                    if 2.4 <= wind_avg[i] <= 4.6:
                        count += 1
                        if count == 3:
                            return f"{i + 1}일 후, 적조현상이 예상 됩니다."
                    else:
                        count = 0
                else:
                    count = 0
            else:
                count = 0
        if count == 0:
            return "적조 증상이 없습니다."
        
        
predictor = WeatherPredictor()
predicted_rain = predictor.fetch_rain_data()
print("Predicted Rain Data:", predicted_rain)

# Fetch wind data
wind_data = predictor.fetch_wind_data()
print("Wind Data:", wind_data)

# Fetch temperature data for a specific year, for example, 2023
temperature_data_2023 = predictor.fetch_temperature_data(2023)
print("Temperature Data for 2023:", temperature_data_2023)

# Predict temperature change rate
temperature_change_rate = predictor.predict_temperature_change_rate()
print("Temperature Change Rate:", temperature_change_rate)

# Get real-time temperature
real_time_temperature = predictor.get_real_time_temperature()
print("Real-Time Temperature:", real_time_temperature)

# Predict future temperatures
future_temperatures = predictor.predict_future_temperatures()
print("Predicted Future Temperatures:", future_temperatures)

# Predict algae bloom
algae_bloom_prediction = predictor.predict_algae_bloom()
print("Algae Bloom Prediction:", algae_bloom_prediction)

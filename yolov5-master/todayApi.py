import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from database import DatabaseConnection, WeatherDatabase

class WeatherInfo:
    def __init__(self, service_key, db_connection, base_time='0600', nx='88', ny='66'):
        self.base_url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
        self.service_key = service_key
        self.base_time = base_time
        self.nx = nx
        self.ny = ny
        self.db_connection = db_connection

    def get_description(self, category, value):
        if category == 'PTY':
            if value == '0':
                return '맑음'
            elif value == '1':
                return '비'
            elif value == '2':
                return '비/눈'
            elif value == '3':
                return '눈'
            elif value == '4':
                return '소나기'
            else:
                return '알 수 없음'
        elif category == 'REH':
            value = int(value)
            if value >= 70:
                return '습도: 높음'
            elif value >= 50:
                return '습도: 보통'
            else:
                return '습도: 낮음'
        elif category == 'RN1':
            value = float(value)
            if value > 0:
                return f"강수량 {value} %"
            else:
                return '강수량 없음'
        elif category == 'T1H':
            value = float(value)
            return f"{value} °C"
        elif category == 'VEC':
            value = int(value)
            if value >= 0 and value < 90:
                return "동풍"
            elif value >= 90 and value < 180:
                return "남풍"
            elif value >= 180 and value < 270:
                return "서풍"
            elif value >= 270 and value < 360:
                return "북풍"
            else:
                return "-"
        elif category == 'WSD':
            value = float(value)
            return f"풍속: {value} m/s"
        else:
            return "설명이 없습니다."

    def get_weather_info(self):
        current_date = datetime.now().strftime('%Y%m%d')
        params = {
            'serviceKey': self.service_key,
            'pageNo': '1',
            'numOfRows': '1000',
            'dataType': 'XML',
            'base_date': current_date,
            'base_time': self.base_time,
            'nx': self.nx,
            'ny': self.ny
        }

        response = requests.get(self.base_url, params=params)
        root = ET.fromstring(response.content)

        weather_info = {}

        for item in root.iter('item'):
            entry = {}
            for child in item:
                if child.tag == 'category':
                    category = child.text
                    if category in ['UUU', 'VVV']:  # uuu와 vvv 카테고리 제외
                        break
                    value = item.find('obsrValue').text
                    description = self.get_description(category, value)
                    entry[category] = description
            
            # 모든 정보를 한 줄에 저장
            weather_info.update(entry)
        
        # 데이터베이스에 삽입
        self.save_weather_info_to_database(weather_info)
    
    def save_weather_info_to_database(self, weather_info):
        self.db_connection.connect()
        insert_query = """
            INSERT INTO weather_info (time_stamp, weather_condition, humidity, precipitation, temperature, wind_direction, wind_speed) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        time_stamp = datetime.now().strftime('%Y-%m-%d')
        weather_condition = weather_info.get('PTY', None)
        humidity = weather_info.get('REH', None)
        precipitation = weather_info.get('RN1', None)
        temperature = weather_info.get('T1H', None)
        wind_direction = weather_info.get('VEC', None)
        wind_speed = weather_info.get('WSD', None)

        self.db_connection.cursor.execute(insert_query, (
            time_stamp, weather_condition, humidity, precipitation, temperature, wind_direction, wind_speed
        ))
        
        self.db_connection.connection.commit()
        self.db_connection.disconnect()

if __name__ == "__main__":
    service_key = 'ydXAJTzJQ6AUxNb/oy3RUfrpoh2wrn+YBB6cs9qU5r7XFPOinOY9sMidRRPtxEH+Qseoo3IZCpya3uK64puMng=='
    db_connection = DatabaseConnection(host="localhost", user="root", password="1234", database="mysql")
    weather_db = WeatherDatabase(db_connection)
    db_connection.connect()
    weather_db.create_table()

    weather_info = WeatherInfo(service_key, db_connection)
    weather_info.get_weather_info()
    db_connection.disconnect()

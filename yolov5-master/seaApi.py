import requests
from datetime import datetime
from database import DatabaseConnection, SeaDatabase

class SeaObservation:
    def __init__(self, auth_key, db_connection):
        self.base_url = 'https://apihub.kma.go.kr/api/typ01/url/sea_obs.php'
        self.auth_key = auth_key
        self.db_connection = db_connection
        
    def get_sea_observation(self, station_name):
        current_time = datetime.now().strftime('%Y%m%d%H%M')
        url = f'{self.base_url}?tm={current_time}&stn=0&help=1&authKey={self.auth_key}'
        response = requests.get(url)
        transformed_data = []
        
        # 필요한 정보만 추출하여 리스트에 추가
        lines = response.text.split('\n')
        for line in lines:
            if station_name in line:
                station_info = line.split(',')  # 쉼표로 구분된 각 필드를 분리하여 리스트로 저장
                try:
                    if float(station_info[5]) != -99.0 and float(station_info[7]) != -99.0:
                        # 풍속과 유의 파고를 10으로 나누어서 추가
                        transformed_data.append({
                            'TM': station_info[1][:9],
                            'WS': float(station_info[7]),  # 풍속 (m/s)
                            'WH': float(station_info[5])  # 유의 파고 (m)
                        })
                except (IndexError, ValueError):
                    pass
        print(station_info[1])
        return transformed_data

    def assess_departure_risk(self, transformed_data):
        if not transformed_data:
            return "Unknown", "위험도를 평가할 데이터가 없습니다."

        wind_speed_avg = (sum([entry['WS'] for entry in transformed_data]) / len(transformed_data)) / 10
        wave_height_avg = (sum([entry['WH'] for entry in transformed_data]) / len(transformed_data)) / 10

        if wind_speed_avg > 20.0 and wave_height_avg > 5.0:
            departure_risk = "높음"
        elif wind_speed_avg > 14.0 and wave_height_avg > 3.0:
            departure_risk = "보통"
        else:
            departure_risk = "낮음"
        
        self.save_sea_info_to_database(transformed_data, departure_risk)
        
    def save_sea_info_to_database(self, transformed_data, departure_risk):
        for entry in transformed_data:
            tm = entry['TM']  # 관측시각
            wind_speed_avg = entry['WS']
            wave_height_avg = entry['WH']
            insert_query = """
            INSERT INTO sea_info (time_stamp, wind_speed, wave_height, risk_level) 
            VALUES (%s, %s, %s, %s)
            """
            self.db_connection.connect()  # 데이터베이스 연결
            self.db_connection.cursor.execute(insert_query, (tm, wind_speed_avg, wave_height_avg, departure_risk))  # TM 값을 time_stamp 대신에 사용
            self.db_connection.connection.commit()

# 사용 예시
if __name__ == "__main__":
    auth_key = 'wIWBRsYVQjWFgUbGFVI1Wg'
    station_name = '통영'
    
    db_connection = DatabaseConnection(host="localhost", user="root", password="1234", database="mysql")
    sea_db = SeaDatabase(db_connection)
    db_connection.connect()
    sea_db.create_table()  
    
    sea_observation = SeaObservation(auth_key, db_connection)
    data = sea_observation.get_sea_observation(station_name)
    sea_observation.assess_departure_risk(data)

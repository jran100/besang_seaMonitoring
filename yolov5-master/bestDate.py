import torch
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from datetime import datetime, timedelta
from database import DatabaseConnection, BestdateDatabase, BuoyDatabase

class BestDate:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def best_date_predict(self, weight):
        days = np.array([
            [1, 5, 10, 15, 20, 30, 35, 40, 42, 44, 46, 48, 50, 52],
            [1, 5, 10, 15, 20, 25, 30, 36, 42, 46, 48, 50, 52, 54],
            [1, 5, 10, 15, 20, 25, 30, 37, 44, 51, 53, 55, 57, 59]
        ])

        base_dates = [
            datetime(2024, 1, 1),  # 1월 1일
            datetime(2024, 2, 1),  # 2월 1일
            datetime(2024, 3, 1)   # 3월 1일
        ]

        # 각 배열의 값을 날짜로 변환합니다.
        date_arrays = []
        for i, row in enumerate(days):
            base_date = base_dates[i]
            date_array = [base_date + timedelta(days=int(day)) for day in row]
            date_arrays.append(date_array)

        # 날짜 배열을 numpy 배열로 변환합니다.
        timestamp_arrays = [[date.strftime('%Y-%m-%d') for date in date_array] for date_array in date_arrays]

        weights = np.array([
            [5, 21, 28, 32, 40, 45, 50, 58, 70, 85, 92, 97, 99, 100],
            [7, 24, 31, 36, 40, 44, 50, 56, 75, 94, 96, 98, 99, 100],
            [6, 22, 31, 35, 37, 43, 50, 60, 85, 91, 95, 98, 99, 100]
        ])

        # 로그 함수 모델 생성
        def log_model(x, a, b, c):
            # 0 이하의 x 값은 로그 함수를 사용할 수 없으므로 1로 변경합니다.
            x = np.maximum(x, 1)
            return a * np.log(b * x) + c

        params = []
        for i in range(len(days)):
            p, _ = curve_fit(log_model, days[i], weights[i])
            params.append(p)
        
        growth_rates = self.calculate_growth_rates(days, params)

        def decline_rate(current_weight, final_weight, decline_rate_target):
            return 100 * (np.log(final_weight) - np.log(current_weight)) / decline_rate_target

        # 현재 무게와 목표 무게 입력
        current_weight = weight
        final_weight = 100  # 최종 무게 (가정)
        decline_rate_target = 1.25  # 가정한 비성장률

        # 성장 기간 동안의 무게 증가량 계산 함수
        def predict_growth_period(current_weight, final_weight, decline_rate_target):
            date = decline_rate(current_weight, final_weight, decline_rate_target)
            return np.round(date, 1)
        
        # 성장 예측
        growth_period = predict_growth_period(current_weight, final_weight, decline_rate_target)
        print("최적의 수확시기 예측: {}일 후".format(int(growth_period)))
        
        optimal_harvest_date = datetime.now() + timedelta(days=int(growth_period))
        print("최적의 수확시기 현재 날짜 변환:", optimal_harvest_date)

        self.save_to_database(timestamp_arrays, weights, growth_rates)

        return optimal_harvest_date

        # 예측 함수
    def calculate_growth_rates(self, days, params):
        growth_rates = []  # 각 날짜의 생장율을 저장할 리스트

        # 각 배열의 값을 날짜로 변환하고 생장율 계산
        for i, row in enumerate(days):
            params_set = params[i]  # 해당 데이터셋에 대한 파라미터 가져오기
            growth_rate_row = []  # 한 데이터셋의 날짜별 생장율을 저장할 리스트
            for day in row:
                try:
                    # 로그 함수를 사용하여 생장율 계산
                    growth_rate = ((self.log_model(day, *params_set) - self.log_model(day - 1, *params_set)) / self.log_model(day - 1, *params_set)) * 100
                    growth_rate_row.append(growth_rate)
                except RuntimeWarning:
                    break
            growth_rates.append(growth_rate_row)

        return growth_rates
    
    def log_model(self, x, a, b, c):
        x = np.maximum(x, 1)
        return a * np.log(b * x) + c

    def save_to_database(self, timestamp_arrays, weights, growth_rates):
        self.db_connection.connect()
        # timestamp_arrays, weights, growth_rates를 데이터베이스에 삽입
        for timestamp_array, weight_array, growth_rate_row in zip(timestamp_arrays, weights, growth_rates):
            for timestamp, weight, growth_rate in zip(timestamp_array, weight_array, growth_rate_row):
                if np.isnan(weight) or np.isnan(growth_rate):
                    weight = 0
                    growth_rate = 0
                insert_query = "INSERT INTO bestdate_info (time_stamp, weight, growth_rate) VALUES (%s, %s, %s)"
                self.db_connection.cursor.execute(insert_query, (timestamp, float(weight), float(growth_rate)))

        # 변경사항 저장
        self.db_connection.connection.commit()
        
class BuoyWeightPredictor:
    def __init__(self, model_path, image_path, save_dir, db_connection):
        self.model_path = model_path
        self.image_path = image_path
        self.save_dir = save_dir
        self.model = self.load_model()
        self.db_connection = db_connection

    def load_model(self):
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.model_path)
        return model

    def get_size(self):
        results = self.model(self.image_path)
        results.print()  # or .show(), .save(), .crop(), .pandas(), etc.
        results.save(save_dir=self.save_dir)

        box_areas = {}

        for i, detection in enumerate(results.xyxy[0]):
            class_name = results.names[int(detection[5])]
            confidence = detection[4]
            x_min, y_min, x_max, y_max = detection[:4]

            box_width = x_max - x_min
            box_height = y_max - y_min
            box_area = box_width * box_height

            box_areas[f"box_area_{i + 1}"] = box_area

        if box_areas['box_area_1'] > box_areas['box_area_2']:
            big = box_areas['box_area_1']
            small = box_areas['box_area_2']
        else:
            big = box_areas['box_area_2']
            small = box_areas['box_area_1']

        rate = small / big
        return rate

    def weight_predict(self, rate):
        buoy_data = {
            'rate': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
            'Weight': [100, 90, 80, 70, 60, 50, 60, 40, 30, 20]
        }
        buoy_df = pd.DataFrame(buoy_data)

        buoy_input = buoy_df[['rate']]
        buoy_target = buoy_df['Weight']

        lr_model = LinearRegression()
        lr_model.fit(buoy_input, buoy_target)

        width_to_predict = [[width] for width in range(10, 51)]
        predicted_weight = lr_model.predict(width_to_predict)

        plt.scatter(buoy_df['rate'], buoy_df['Weight'], color='blue', label='Data')
        plt.plot(range(10, 51), predicted_weight, color='red', linestyle='-', label='Linear Regression')

        new_width = rate
        predicted_value = lr_model.predict([[new_width]])

        plt.scatter(new_width, predicted_value, color='green', label='Predicted Value')
        plt.xlabel('Rate')
        plt.ylabel('Weight')
        plt.legend()
        plt.show()

        print(f"해당부표의 예측 무게 : {predicted_value[0]:.2f} kg")
        return predicted_value[0]
    
    def save_weight_to_database(self, predicted_weight, best_date_predictor):
        self.db_connection.connect()
        optimal_harvest_date = best_date_predictor.best_date_predict(predicted_weight)
        insert_query = "INSERT INTO buoy_info (predicted_weight, harvest_date) VALUES (%s, %s)"
        self.db_connection.cursor.execute(insert_query, (predicted_weight, optimal_harvest_date.strftime('%Y-%m-%d')))
        self.db_connection.connection.commit()
        
if __name__ == "__main__":
    model_path = 'weights/best.pt'
    image_path = r'C:\Users\BAEKJRAN\Downloads\yolov5-master (2)\yolov5-master\check\IMG_1261.JPEG'
    save_dir = r'C:\Users\BAEKJRAN\Downloads\yolov5-master (2)\yolov5-master\static\images\detect'

    db_connection = DatabaseConnection(host="localhost", user="root", password="1234", database="mysql")
    buoy_db = BuoyDatabase(db_connection)
    db_connection.connect()
    buoy_db.create_table()

    predictor = BuoyWeightPredictor(model_path, image_path, save_dir, db_connection)
    rate = predictor.get_size()
    predicted_weight = predictor.weight_predict(rate)

    best_date_predictor = BestDate(db_connection)
    predictor.save_weight_to_database(predicted_weight, best_date_predictor)

    db_connection.disconnect()

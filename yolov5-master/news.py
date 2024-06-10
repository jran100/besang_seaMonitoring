import re
import requests
import mysql.connector
from database import DatabaseConnection, NewsDatabase

def clean_title(title):
    clean_title = re.sub('<.*?>|&.*?;', '', title)
    return clean_title

def remove_pattern(title, pattern):
    clean_title = re.sub(pattern, '', title)
    return clean_title

class NaverNews:
    def __init__(self, client_id, client_secret, db_connection):
        self.client_id = client_id
        self.client_secret = client_secret
        self.db_connection = db_connection

    def get_news(self, query):
        headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }

        params = {
            'query': query,
            'display': 10,
            'start': 1,
            'sort': 'sim'
        }

        url = 'https://openapi.naver.com/v1/search/news.json'  # 뉴스 검색 API의 URL

        response = requests.get(url, headers=headers, params=params)
        news_list = response.json()['items'] if response.status_code == 200 else None

        if news_list:
            self.save_to_database(news_list)
        else:
            print("뉴스를 가져오는데 실패하였습니다.")

        return news_list

    def save_to_database(self, news_list):
        self.db_connection.connect()
        cursor = self.db_connection.connection.cursor()

        for news in news_list:
            title = news['title']
            link = news['link']

            title = clean_title(title)
            insert_query = "INSERT INTO news (title, link) VALUES (%s, %s)"
            cursor.execute(insert_query, (title, link))

        self.db_connection.connection.commit()
        cursor.close()
        self.db_connection.disconnect()

if __name__ == '__main__':
    client_id = '1ctTj_Bho6U2uzskrH25'
    client_secret = 'MZa6c6HJTK'
    query = '홍합'

    db_connection = DatabaseConnection(host="localhost", user="root", password="1234", database="mysql")
    news_db = NewsDatabase(db_connection)
    db_connection.connect()
    news_db.create_table()

    naver_news = NaverNews(client_id, client_secret, db_connection)
    news_list = naver_news.get_news(query)

    db_connection.disconnect()

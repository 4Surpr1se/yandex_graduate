import psycopg2
from pymongo import MongoClient
from faker import Faker
import random
import os
import csv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

pg_conn = psycopg2.connect(
    dbname="testdb", user="user", password="password", host="localhost", port="5432"
)
pg_cursor = pg_conn.cursor()

mongo_client = MongoClient("mongodb://user:password@localhost:27017/")
mongo_db = mongo_client["testdb"]

fake = Faker()

num_users = 100000 
num_movies = 10000  
num_reviews = 500000
num_likes = 10000000
num_bookmarks = 500000
batch_size = 100000    # Размер пакета вставки данных


def create_pg_tables():
    print(f"{datetime.now()}: Создание таблиц в PostgreSQL...")
    pg_cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id SERIAL PRIMARY KEY,
        user_id INT,
        movie_id INT,
        review_text TEXT,
        review_date TIMESTAMP,
        likes INT DEFAULT 0,
        dislikes INT DEFAULT 0,
        rating SMALLINT CHECK (rating BETWEEN 0 AND 10)
    );
    
    CREATE TABLE IF NOT EXISTS likes (
        id SERIAL PRIMARY KEY,
        user_id INT,
        movie_id INT,
        rating SMALLINT CHECK (rating BETWEEN 0 AND 10)
    );
    
    CREATE TABLE IF NOT EXISTS bookmarks (
        id SERIAL PRIMARY KEY,
        user_id INT,
        movie_id INT,
        bookmark_date TIMESTAMP
    );
    """)
    pg_conn.commit()
    print(f"{datetime.now()}: Таблицы PostgreSQL созданы.")


def generate_pg_likes():
    print(f"{datetime.now()}: Генерация данных для PostgreSQL лайков...")
    filename = "likes_data.csv"
    with open(filename, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        for _ in range(num_likes):
            writer.writerow([random.randint(1, num_users), random.randint(1, num_movies), random.randint(0, 10)])

    print(f"{datetime.now()}: Загрузка данных в PostgreSQL из файла...")
    with open(filename, "r") as f:
        pg_cursor.copy_expert("COPY likes (user_id, movie_id, rating) FROM STDIN WITH CSV", f)
    pg_conn.commit()
    os.remove(filename)
    print(f"{datetime.now()}: Лайки PostgreSQL загружены.")


def generate_mongo_likes():
    print(f"{datetime.now()}: Генерация данных для MongoDB лайков...")
    likes = [
        {"user_id": random.randint(1, num_users), "movie_id": random.randint(1, num_movies), "rating": random.randint(0, 10)}
        for _ in range(num_likes)
    ]
    mongo_db.likes.insert_many(likes)
    print(f"{datetime.now()}: Лайки MongoDB загружены.")

def generate_mongo_reviews():
    print(f"{datetime.now()}: Генерация данных для MongoDB рецензий...")
    reviews = [
        {
            "user_id": random.randint(1, num_users),
            "movie_id": random.randint(1, num_movies),
            "review_text": fake.text(),
            "review_date": fake.date_time(),
            "rating": random.randint(0, 10),
            "likes": random.randint(0, 100),
            "dislikes": random.randint(0, 100)
        }
        for _ in range(num_reviews)
    ]
    mongo_db.reviews.insert_many(reviews)
    print(f"{datetime.now()}: Рецензии MongoDB загружены.")

def generate_mongo_bookmarks():
    print(f"{datetime.now()}: Генерация данных для MongoDB закладок...")
    bookmarks = [
        {"user_id": random.randint(1, num_users), "movie_id": random.randint(1, num_movies), "bookmark_date": fake.date_time()}
        for _ in range(num_bookmarks)
    ]
    mongo_db.bookmarks.insert_many(bookmarks)
    print(f"{datetime.now()}: Закладки MongoDB загружены.")

create_pg_tables()
mongo_db.drop_collection("reviews")
mongo_db.drop_collection("likes")
mongo_db.drop_collection("bookmarks")
print(f"{datetime.now()}: Коллекции MongoDB удалены и подготовлены для новых данных.")

print(f"{datetime.now()}: Запуск параллельной генерации данных...")
with ThreadPoolExecutor() as executor:
    executor.submit(generate_pg_likes)
    executor.submit(generate_mongo_likes)
    executor.submit(generate_mongo_reviews)
    executor.submit(generate_mongo_bookmarks)

print(f"{datetime.now()}: Генерация данных завершена.")

pg_cursor.close()
pg_conn.close()
mongo_client.close()
print(f"{datetime.now()}: Соединения с PostgreSQL и MongoDB закрыты.")

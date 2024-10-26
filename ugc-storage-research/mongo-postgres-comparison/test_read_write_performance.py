import psycopg2
from pymongo import MongoClient
import random
import time
from datetime import datetime

pg_conn = psycopg2.connect(
    dbname="testdb", user="user", password="password", host="localhost", port="5432"
)
pg_cursor = pg_conn.cursor()

mongo_client = MongoClient("mongodb://user:password@localhost:27017/")
mongo_db = mongo_client["testdb"]

num_users = 100000
num_movies = 10000
num_tests = 100 

def print_postgres_data_counts():
    pg_cursor.execute("SELECT COUNT(*) FROM likes;")
    likes_count = pg_cursor.fetchone()[0]
    pg_cursor.execute("SELECT COUNT(*) FROM reviews;")
    reviews_count = pg_cursor.fetchone()[0]
    pg_cursor.execute("SELECT COUNT(*) FROM bookmarks;")
    bookmarks_count = pg_cursor.fetchone()[0]
    print(f"PostgreSQL данные:\n- Лайков: {likes_count}\n- Рецензий: {reviews_count}\n- Закладок: {bookmarks_count}")

def print_mongo_data_counts():
    likes_count = mongo_db.likes.count_documents({})
    reviews_count = mongo_db.reviews.count_documents({})
    bookmarks_count = mongo_db.bookmarks.count_documents({})
    print(f"MongoDB данные:\n- Лайков: {likes_count}\n- Рецензий: {reviews_count}\n- Закладок: {bookmarks_count}")

print("Проверка текущего количества записей в базах данных...")
print_postgres_data_counts()
print_mongo_data_counts()

def measure_time(func, *args):
    start_time = time.time()
    func(*args)
    return round((time.time() - start_time) * 1000, 2)  # Время в миллисекундах

def insert_like_pg():
    user_id = random.randint(1, num_users)
    movie_id = random.randint(1, num_movies)
    rating = random.randint(0, 10)
    pg_cursor.execute("INSERT INTO likes (user_id, movie_id, rating) VALUES (%s, %s, %s);", (user_id, movie_id, rating))
    pg_conn.commit()

def insert_review_pg():
    user_id = random.randint(1, num_users)
    movie_id = random.randint(1, num_movies)
    review_text = "Sample review text"
    review_date = datetime.now()
    rating = random.randint(0, 10)
    pg_cursor.execute("INSERT INTO reviews (user_id, movie_id, review_text, review_date, rating) VALUES (%s, %s, %s, %s, %s);", (user_id, movie_id, review_text, review_date, rating))
    pg_conn.commit()

def insert_bookmark_pg():
    user_id = random.randint(1, num_users)
    movie_id = random.randint(1, num_movies)
    bookmark_date = datetime.now()
    pg_cursor.execute("INSERT INTO bookmarks (user_id, movie_id, bookmark_date) VALUES (%s, %s, %s);", (user_id, movie_id, bookmark_date))
    pg_conn.commit()

def insert_like_mongo():
    mongo_db.likes.insert_one({"user_id": random.randint(1, num_users), "movie_id": random.randint(1, num_movies), "rating": random.randint(0, 10)})

def insert_review_mongo():
    mongo_db.reviews.insert_one({
        "user_id": random.randint(1, num_users),
        "movie_id": random.randint(1, num_movies),
        "review_text": "Sample review text",
        "review_date": datetime.now(),
        "rating": random.randint(0, 10)
    })

def insert_bookmark_mongo():
    mongo_db.bookmarks.insert_one({
        "user_id": random.randint(1, num_users),
        "movie_id": random.randint(1, num_movies),
        "bookmark_date": datetime.now()
    })

def get_likes_count_pg(movie_id):
    pg_cursor.execute("SELECT COUNT(*) FROM likes WHERE movie_id = %s;", (movie_id,))
    pg_cursor.fetchone()

def get_average_rating_pg(movie_id):
    pg_cursor.execute("SELECT AVG(rating) FROM likes WHERE movie_id = %s;", (movie_id,))
    pg_cursor.fetchone()

def get_reviews_pg(movie_id):
    pg_cursor.execute("SELECT review_text FROM reviews WHERE movie_id = %s ORDER BY review_date DESC LIMIT 10;", (movie_id,))
    pg_cursor.fetchall()

def get_likes_count_mongo(movie_id):
    mongo_db.likes.count_documents({"movie_id": movie_id})

def get_average_rating_mongo(movie_id):
    pipeline = [{"$match": {"movie_id": movie_id}}, {"$group": {"_id": None, "average_rating": {"$avg": "$rating"}}}]
    list(mongo_db.likes.aggregate(pipeline))

def get_reviews_mongo(movie_id):
    mongo_db.reviews.find({"movie_id": movie_id}).sort("review_date", -1).limit(10)

def run_tests():
    results = {
        "PostgreSQL": {"insert_like": [], "insert_review": [], "insert_bookmark": [], "get_likes_count": [], "get_average_rating": [], "get_reviews": []},
        "MongoDB": {"insert_like": [], "insert_review": [], "insert_bookmark": [], "get_likes_count": [], "get_average_rating": [], "get_reviews": []}
    }

    print("Запуск тестов записи данных")
    for i in range(num_tests):
        results["PostgreSQL"]["insert_like"].append(measure_time(insert_like_pg))
        results["PostgreSQL"]["insert_review"].append(measure_time(insert_review_pg))
        results["PostgreSQL"]["insert_bookmark"].append(measure_time(insert_bookmark_pg))
        results["MongoDB"]["insert_like"].append(measure_time(insert_like_mongo))
        results["MongoDB"]["insert_review"].append(measure_time(insert_review_mongo))
        results["MongoDB"]["insert_bookmark"].append(measure_time(insert_bookmark_mongo))

        if (i + 1) % 100 == 0 or i + 1 == num_tests:
            print(f"[{datetime.now()}] Запись данных: {i + 1}/{num_tests} завершено.")

    print("Запуск тестов чтения данных")
    for i in range(num_tests):
        movie_id = random.randint(1, num_movies)
        results["PostgreSQL"]["get_likes_count"].append(measure_time(get_likes_count_pg, movie_id))
        results["PostgreSQL"]["get_average_rating"].append(measure_time(get_average_rating_pg, movie_id))
        results["PostgreSQL"]["get_reviews"].append(measure_time(get_reviews_pg, movie_id))
        results["MongoDB"]["get_likes_count"].append(measure_time(get_likes_count_mongo, movie_id))
        results["MongoDB"]["get_average_rating"].append(measure_time(get_average_rating_mongo, movie_id))
        results["MongoDB"]["get_reviews"].append(measure_time(get_reviews_mongo, movie_id))

        if (i + 1) % 10 == 0 or i + 1 == num_tests:
            print(f"[{datetime.now()}] Чтение данных: {i + 1}/{num_tests} завершено.")

    for db, tests in results.items():
        print(f"\nРезультаты для {db}:")
        for test, times in tests.items():
            print(f"{test}: Среднее время выполнения: {sum(times) / len(times):.2f} мс")

run_tests()

pg_cursor.close()
pg_conn.close()
mongo_client.close()

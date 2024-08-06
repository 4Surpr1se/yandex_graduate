import time

from backoff_decorator import backoff
from constants import DEFAULT_DATE
from elasticsearch_client import (create_es_connection, create_index,
                                  upload_data)
from extract import (get_films_with_updated_genre,
                     get_films_with_updated_persons, get_updated_film_ids,
                     get_updated_genres_ids, get_updated_person_ids)
from indexes import body_genres, body_movies, body_persons
from logger import logger
from pg_connection import create_pg_connection
from psycopg2 import extras
from settings import settings
from state_manager import get_state, update_state
from transform import (transform_data, transform_genres_data,
                       transform_persons_data)


def get_last_update_dates():
    state_dict = get_state()
    return state_dict['last_film_date'], state_dict['last_genre_date'], state_dict['last_person_date'], state_dict['last_person_info_date'], state_dict['last_genre_info_date']

def update_last_update_dates(last_film_date=None, last_genre_date=None, last_person_date=None, last_person_info_date=None, last_genre_info_date=None):
    update_state(last_film_date=last_film_date, last_genre_date=last_genre_date, last_person_date=last_person_date, last_person_info_date=last_person_info_date, last_genre_info_date=last_genre_info_date)

def process_updates(index, body, get_updated_ids, transform_func, state_key):
    es = create_es_connection()
    conn = create_pg_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.DictCursor)

        if not es.indices.exists(index=index):
            create_index(es, index, body)

        state_dict = get_state()
        last_update_date = state_dict[state_key]

        while True:
            items = get_updated_ids(cursor, last_update_date, settings.batch_size)
            if items:
                last_update_date = max(item[1] for item in items)
                update_last_update_dates(**{state_key: last_update_date})
                logger.info(f"Processing {len(items)} updated {index}")
                ids_list = [item['id'] for item in items]
                unique_ids_list = list(set(ids_list))
                transformed_data = transform_func(cursor, unique_ids_list)
                upload_data(es, index, transformed_data)
            else:
                break
    finally:
        cursor.close()
        conn.close()

@backoff()
def process_updates_movies():
    try:
        state_dict = get_state()
        last_film_date = state_dict['last_film_date']
        last_genre_date = state_dict['last_genre_date']
        last_person_date = state_dict['last_person_date']

        es = create_es_connection()
        conn = create_pg_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)

        if not es.indices.exists(index='movies'):
            create_index(es, 'movies', body_movies)

        films = get_updated_film_ids(cursor, last_film_date, settings.batch_size)
        if films:
            last_film_date = max(film[1] for film in films)
            update_state(last_film_date=last_film_date)
            if last_genre_date == DEFAULT_DATE and last_person_date == DEFAULT_DATE:
                logger.info("Initial run complete")
                update_state(last_genre_date=last_film_date, last_person_date=last_film_date)
        else:
            films = get_films_with_updated_genre(cursor, last_genre_date, settings.batch_size)
            if films:
                last_genre_date = max(film[1] for film in films)
                update_state(last_genre_date=last_genre_date)
            else:
                films = get_films_with_updated_persons(cursor, last_person_date, settings.batch_size)
                if films:
                    last_person_date = max(film[1] for film in films)
                    update_state(last_person_date=last_person_date)

        if films:
            logger.info(f"Processing {len(films)} updated films")
            film_ids_list = [film['id'] for film in films]
            unique_film_ids_list = list(set(film_ids_list))
            transformed_data = transform_data(cursor, unique_film_ids_list)
            upload_data(create_es_connection(), 'movies', transformed_data)
    finally:
        cursor.close()
        conn.close()

@backoff()
def process_updates_persons():
    process_updates('persons', body_persons, get_updated_person_ids, transform_persons_data, 'last_person_info_date')

@backoff()
def process_updates_genres():
    process_updates('genres', body_genres, get_updated_genres_ids, transform_genres_data, 'last_genre_info_date')

def etl_pipeline():
    while True:
        try:
            process_updates_movies()
            process_updates_persons()
            process_updates_genres()
            time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Process interrupted by user")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            time.sleep(60)

if __name__ == "__main__":
    logger.info('Starting ELT service')
    etl_pipeline()

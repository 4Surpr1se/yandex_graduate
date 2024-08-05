import time

from backoff_decorator import backoff
from constants import DEFAULT_DATE
from elasticsearch_client import (create_es_connection, create_index,
                                  upload_data)
from extract import (get_films_with_updated_genre,
                     get_films_with_updated_persons, get_updated_film_ids,
                     get_updated_person_ids, get_updated_genres_ids)
from indexes import body_movies, body_persons, body_genres
from logger import logger
from pg_connection import create_pg_connection
from psycopg2 import extras
from settings import settings
from state_manager import get_state, update_state
from transform import transform_data, transform_persons_data, transform_genres_data


@backoff()
def process_updates_movies():
    try:
        es = create_es_connection()
        conn = create_pg_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)

        if not es.indices.exists(index='movies'):
            create_index(es, 'movies', body_movies)

        state_dict = get_state()
        last_film_date = state_dict['last_film_date']
        last_genre_date = state_dict['last_genre_date']
        last_person_date = state_dict['last_person_date']

        films = get_updated_film_ids(
            cursor, last_film_date, settings.batch_size)
        if films:
            last_film_date = max(film[1] for film in films)
            update_state(last_film_date=last_film_date)
            if (last_genre_date == DEFAULT_DATE) and (last_person_date == DEFAULT_DATE):
                # после первой обработки всех фильмов считаем все данные обработанными
                logger.info("Initial run complete")
                update_state(last_genre_date=last_film_date,
                             last_person_date=last_film_date)
        else:
            films = get_films_with_updated_genre(
                cursor, last_genre_date, settings.batch_size)
            if films:
                last_genre_date = max(film[1] for film in films)
                update_state(last_genre_date=last_genre_date)
            else:
                films = get_films_with_updated_persons(
                    cursor, last_person_date, settings.batch_size)
                if films:
                    last_person_date = max(film[1] for film in films)
                    update_state(last_person_date=last_person_date)

        if films:
            logger.info(f"Processing {len(films)} updated films")
            film_ids_list = [film['id'] for film in films]
            unique_film_ids_list = list(set(film_ids_list))
            transformed_data = transform_data(cursor, unique_film_ids_list)
            upload_data(es, 'movies', transformed_data)

    except Exception as e:
        cursor.close()


@backoff()
def process_updates_persons():
    try:
        while True:
            es = create_es_connection()
            conn = create_pg_connection()
            cursor = conn.cursor(cursor_factory=extras.DictCursor)

            if not es.indices.exists(index='persons'):
                create_index(es, 'persons', body_persons)

            state_dict = get_state()
            last_person_info_date = state_dict['last_person_info_date']

            persons = get_updated_person_ids(
                cursor, last_person_info_date, settings.batch_size)

            if persons:
                last_person_info_date = max(person[1] for person in persons)
                update_state(last_person_info_date=last_person_info_date)
                logger.info(f"Processing {len(persons)} updated persons")
                person_ids_list = [person['id'] for person in persons]
                unique_person_ids_list = list(set(person_ids_list))
                transformed_data = transform_persons_data(
                    cursor, unique_person_ids_list)
                upload_data(es, 'persons', transformed_data)

            else:
                break

    except Exception:
        cursor.close()


@backoff()
def process_updates_genres():
    try:
        while True:
            es = create_es_connection()
            conn = create_pg_connection()
            cursor = conn.cursor(cursor_factory=extras.DictCursor)

            if not es.indices.exists(index='genres'):
                create_index(es, 'genres', body_genres)

            state_dict = get_state()
            last_genre_info_date = state_dict['last_genre_info_date']

            genres = get_updated_genres_ids(
                cursor, last_genre_info_date, settings.batch_size)

            if genres:
                last_genre_info_date = max(genre[1] for genre in genres)
                update_state(last_genre_info_date=last_genre_info_date)
                logger.info(f"Processing {len(genres)} updated genres")
                genre_ids_list = [genre['id'] for genre in genres]
                unique_genre_ids_list = list(set(genre_ids_list))
                transformed_data = transform_genres_data(
                    cursor, unique_genre_ids_list)
                upload_data(es, 'genres', transformed_data)

            else:
                break

    except Exception:
        cursor.close()

def etl_pipeline():
    while True:
        try:
            process_updates_movies()
            process_updates_persons()
            process_updates_genres()

            # Sleep for a minute before checking again
            time.sleep(60)

        except KeyboardInterrupt:
            logger.info("Process interrupted by user")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            time.sleep(60)  # Sleep for a minute before retrying


if __name__ == "__main__":
    logger.info('Starting ELT service')
    etl_pipeline()

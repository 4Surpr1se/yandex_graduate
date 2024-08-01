from datetime import datetime
import time
from backoff_decorator import backoff
from transform import transform_data
from extract import get_updated_film_ids, get_films_with_updated_genre, get_films_with_updated_persons
from pg_connection import create_pg_connection
from elasticsearch_client import create_es_connection, upload_data, create_index
from state_manager import get_state, update_state
from psycopg2 import extras
from settings import settings
from logger import logger
from constants import DEFAULT_DATE

@backoff()
def process_updates():
    try:
        es = create_es_connection()
        conn = create_pg_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        
        if not es.indices.exists(index='movies'):
            create_index(es)
        
        state_dict = get_state()
        last_film_date = state_dict['last_film_date']
        last_genre_date = state_dict['last_genre_date']
        last_person_date = state_dict['last_person_date']
        
        films = get_updated_film_ids(cursor, last_film_date, settings.batch_size)
        if films:
            last_film_date = max(film[1] for film in films)
            update_state(last_film_date=last_film_date)
            if (last_genre_date == DEFAULT_DATE) and (last_person_date == DEFAULT_DATE):
                # после первой обработки всех фильмов считаем все данные обработанными
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
            upload_data(es, transformed_data)
    except Exception as e:
        cursor.close()

def etl_pipeline():
    while True:
        try:
            process_updates()
                
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
from datetime import datetime

import psycopg2
from backoff_decorator import backoff
from logger import logger
from psycopg2.extensions import cursor as PsycopgCursor


@backoff()
def get_updated_film_ids(cursor: PsycopgCursor, last_modified_date: datetime, batch_size: int):
    try:
        logger.info("Try get_updated_film_ids")
        query = """
                SELECT id, updated_at  FROM content.film_work 
                WHERE updated_at > %s 
                ORDER BY updated_at ASC 
                LIMIT %s
        """
        cursor.execute(query, (last_modified_date, str(batch_size),))
        rows = cursor.fetchall()
        logger.info('Fetched %d rows from PostgreSQL', len(rows))
        return rows
    except psycopg2.InterfaceError as e:
        logger.error('Curosor error: %s', e)
        raise psycopg2.InterfaceError
    except Exception as e:
        logger.error('Error fetching data: %s', e)
        return []


@backoff()
def get_films_with_updated_genre(cursor: PsycopgCursor, last_modified_date: datetime, batch_size: int):
    try:
        logger.info("Try get_films_with_updated_genre")
        query = """
                SELECT film_work_id, g.updated_at FROM content.genre as g
                INNER JOIN content.genre_film_work as f ON genre_id=g.id 
                WHERE updated_at > %s 
                ORDER BY updated_at ASC 
                LIMIT %s 
        """
        cursor.execute(query, (last_modified_date, batch_size))
        rows = cursor.fetchall()
        logger.info('Fetched %d rows from PostgreSQL', len(rows))
        return rows
    except psycopg2.InterfaceError as e:
        logger.error('Cursor error: %s', e)
        raise psycopg2.InterfaceError
    except Exception as e:
        logger.error('Error fetching data: %s', e)
        return []


@backoff()
def get_films_with_updated_persons(cursor: PsycopgCursor, last_modified_date: datetime, batch_size: int):
    try:
        logger.info("Try get_films_with_updated_persons")
        query = """
                SELECT film_work_id, p.updated_at FROM content.person as p
                INNER JOIN content.person_film_work as f ON person_id=p.id 
                WHERE updated_at > %s 
                ORDER BY updated_at ASC 
                LIMIT %s 
        """
        cursor.execute(query, (last_modified_date, batch_size))
        rows = cursor.fetchall()
        logger.info('Fetched %d rows from PostgreSQL', len(rows))
        return rows
    except psycopg2.InterfaceError as e:
        logger.error('Curosor error: %s', e)
        raise psycopg2.InterfaceError
    except Exception as e:
        logger.error('Error fetching data: %s', e)
        return []


@backoff()
def get_updated_person_ids(cursor: PsycopgCursor, last_modified_date: datetime, batch_size: int):
    try:
        logger.info("Try get_updated_person_ids")
        query = """
                SELECT id, updated_at FROM content.person 
                WHERE updated_at > %s 
                ORDER BY updated_at ASC 
                LIMIT %s
        """
        cursor.execute(query, (last_modified_date, str(batch_size),))
        rows = cursor.fetchall()
        logger.info('Fetched %d rows from PostgreSQL', len(rows))
        return rows
    except psycopg2.InterfaceError as e:
        logger.error('Curosor error: %s', e)
        raise psycopg2.InterfaceError
    except Exception as e:
        logger.error('Error fetching data: %s', e)
        return []

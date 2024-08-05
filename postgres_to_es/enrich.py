from logger import logger
from psycopg2.extensions import cursor as PsycopgCursor


def get_films_by_id(cursor: PsycopgCursor, film_ids: tuple):
    try:
        logger.info("Try get_films_by_id")
        ids_str = ','.join(f"'{id}'" for id in film_ids)

        query = f"""
                SELECT id, rating, title, description, updated_at 
                FROM content.film_work 
                WHERE id IN ({ids_str})
                ORDER BY updated_at ASC
                """
        cursor.execute(query)
        rows = cursor.fetchall()
        logger.info('Fetched %d rows from PostgreSQL', len(rows))
        return rows
    except Exception as e:
        logger.error('Error fetching data: %s', e)
        return []


def get_genres_by_filmid(cursor: PsycopgCursor, film_ids: tuple):
    try:
        logger.info("Try get_genres_by_filmid")
        ids_str = ','.join(f"'{id}'" for id in film_ids)
        query = f"""
                SELECT g.id,  name, description, film_work_id FROM content.genre as g
                INNER JOIN content.genre_film_work ON genre_id=g.id
                WHERE film_work_id IN ({ids_str})
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        logger.info('Fetched %d rows for genres from PostgreSQL', len(rows))
        return rows
    except Exception as e:
        logger.error('Error fetching data: %s', e)
        return []


def get_persons_by_filmid(cursor: PsycopgCursor, film_ids: tuple):
    try:
        logger.info("Try get_persons_by_filmid")
        ids_str = ','.join(f"'{id}'" for id in film_ids)
        query = f"""
                SELECT p.id, full_name, role, film_work_id FROM content.person as p
                INNER JOIN content.person_film_work ON person_id=p.id
                WHERE film_work_id IN ({ids_str})
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        logger.info('Fetched %d rows for persons from PostgreSQL', len(rows))
        return rows
    except Exception as e:
        logger.error('Error fetching data: %s', e)
        return []


def get_persons_by_personid(cursor: PsycopgCursor, person_ids: tuple):
    try:
        logger.info("Try get_persons_by_personid")
        ids_str = ','.join(f"'{id}'" for id in person_ids)
        query = f"""
                SELECT id, full_name
                FROM content.person
                WHERE id IN ({ids_str})
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        logger.info(
            'Fetched %d rows for persons info from PostgreSQL', len(rows))
        return rows
    except Exception as e:
        logger.error('Error fetching data: %s', e)
        return []


def get_films_by_personid(cursor: PsycopgCursor, person_ids: tuple):
    try:
        logger.info("Try get_persons_by_personid")
        ids_str = ','.join(f"'{id}'" for id in person_ids)
        query = f"""
                SELECT p.id, pfw.film_work_id, pfw.role
                FROM content.person_film_work as pfw
                INNER JOIN content.person as p ON p.id=pfw.person_id
                WHERE p.id IN ({ids_str})
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        logger.info(
            'Fetched %d rows for films by persons from PostgreSQL', len(rows))
        return rows
    except Exception as e:
        logger.error('Error fetching data: %s', e)
        return []
    
    
def get_genres_by_genresid(cursor: PsycopgCursor, genre_ids: tuple):
    try:
        logger.info("Try get_genres_by_genreid")
        ids_str = ','.join(f"'{id}'" for id in genre_ids)
        query = f"""
                SELECT id, name, description FROM content.genre
                WHERE id IN ({ids_str})
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        logger.info(
            'Fetched %d rows for films by genres from PostgreSQL', len(rows))
        return rows
    except Exception as e:
        logger.error('Error fetching data: %s', e)
        return []

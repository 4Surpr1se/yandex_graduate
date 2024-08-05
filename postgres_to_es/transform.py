from enrich import (get_films_by_id, get_films_by_personid,
                    get_genres_by_filmid, get_persons_by_filmid,
                    get_persons_by_personid, get_genres_by_genresid)
from logger import logger


def transform_data(cursor, film_ids_list):
    try:
        films = get_films_by_id(cursor, tuple(film_ids_list))
        genres = get_genres_by_filmid(cursor, tuple(film_ids_list))
        persons = get_persons_by_filmid(cursor, tuple(film_ids_list))

        # Organize genres by film ID
        genre_dict = {}
        for genre in genres:
            film_id = genre['film_work_id']
            if film_id not in genre_dict:
                genre_dict[film_id] = []
            genre_dict[film_id].append({
                'id': genre['id'],
                'name': genre['name']
            })

        # Organize persons by film ID and role
        person_dict = {'writer': {}, 'director': {}, 'actor': {}}
        for person in persons:
            film_id = person['film_work_id']
            role = person['role']
            if film_id not in person_dict[role]:
                person_dict[role][film_id] = []
            person_dict[role][film_id].append({
                'id': person['id'],
                'name': person['full_name']
            })

        transformed_data = []
        for film in films:
            film_id = film['id']
            film_data = {
                'id': film_id,
                'imdb_rating': film['rating'],
                'genres': genre_dict[film_id],
                'title': film['title'],
                'description': film['description'],
                'directors_names': [],
                'actors_names': [],
                'writers_names': [],
                'directors': [],
                'actors': [],
                'writers': []
            }

            if film_id in person_dict['writer']:
                film_data['writers_names'] = [p['name']
                                              for p in person_dict['writer'][film_id]]
                film_data['writers'] = person_dict['writer'][film_id]
            if film_id in person_dict['director']:
                film_data['directors_names'] = [p['name']
                                                for p in person_dict['director'][film_id]]
                film_data['directors'] = person_dict['director'][film_id]
            if film_id in person_dict['actor']:
                film_data['actors_names'] = [p['name']
                                             for p in person_dict['actor'][film_id]]
                film_data['actors'] = person_dict['actor'][film_id]

            transformed_data.append(film_data)
    except Exception as e:
        logger.error('Error transforming data: %s', e)
        transformed_data = []

    return transformed_data


def transform_persons_data(cursor, person_ids_list):
    try:
        persons = get_persons_by_personid(cursor, tuple(person_ids_list))
        films = get_films_by_personid(cursor, tuple(person_ids_list))

        films_dict = {}
        for film in films:
            person_id = film['id']
            film_work_id = film['film_work_id']
            if person_id not in films_dict:
                films_dict[person_id] = {}
            if film_work_id not in films_dict[person_id]:
                films_dict[person_id][film_work_id] = []
            films_dict[person_id][film_work_id].append(film['role'])

        transformed_data = []
        for person in persons:
            person_id = person['id']
            person_data = {
                'id': person_id,
                'full_name': person['full_name'],
                'films': [{'id': uuid, 'roles': roles}
                          for uuid, roles in films_dict[person_id].items()]
            }
            transformed_data.append(person_data)
    except Exception as e:
        logger.error('Error transforming data: %s', e)
        transformed_data = []

    return transformed_data


def transform_genres_data(cursor, genres_ids_list):
    try:
        genres = get_genres_by_genresid(cursor, tuple(genres_ids_list))
        
        transformed_data = []
        for genre in genres:
            genre_data = {
                'id': genre['id'],
                'name': genre['name'],
                'description': genre.get('description', '')
            }
            transformed_data.append(genre_data)
    except Exception as e:
        logger.error('Error transforming genre data: %s', e)
        transformed_data = []
    
    return transformed_data


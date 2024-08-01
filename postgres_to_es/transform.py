from enrich import get_genres_by_filmid, get_films_by_id, get_persons_by_filmid
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
                genre_dict[film_id] = set()
            genre_dict[film_id].add(genre['name'])
        
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
                'genres': list(genre_dict.get(film_id, [])),
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
                film_data['writers_names'] = [p['name'] for p in person_dict['writer'][film_id]]
                film_data['writers'] = person_dict['writer'][film_id]
            if film_id in person_dict['director']:
                film_data['directors_names'] = [p['name'] for p in person_dict['director'][film_id]]
                film_data['directors'] = person_dict['director'][film_id]
            if film_id in person_dict['actor']:
                film_data['actors_names'] = [p['name'] for p in person_dict['actor'][film_id]]
                film_data['actors'] = person_dict['actor'][film_id]
            
            transformed_data.append(film_data)
    except Exception as e:
        logger.error('Error transforming data: %s', e)
        transformed_data = []
    
    return transformed_data
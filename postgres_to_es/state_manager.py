import json
import os
from datetime import datetime

from constants import DEFAULT_DATE, STATE_FILE
from logger import logger


def get_state():
    state = {
        'last_film_date': DEFAULT_DATE,
        'last_genre_date': DEFAULT_DATE,
        'last_person_date': DEFAULT_DATE,
        'last_person_info_date': DEFAULT_DATE,
        'last_genre_info_date': DEFAULT_DATE
    }
    if not os.path.exists(STATE_FILE):
        return state

    try:
        with open(STATE_FILE, 'r') as file:
            file_content = file.read().strip()
            if not file_content:
                return state
            loaded_state = json.loads(file_content)

            if all(key in loaded_state for key in state):
                state.update(loaded_state)
            else:
                logger.warning('State file is missing expected keys.')
    except json.JSONDecodeError as e:
        logger.error('Error decoding JSON from state file: %s', e)
    except Exception as e:
        logger.error('Error reading state file: %s', e)

    return state


def serialize_date(date):
    if isinstance(date, datetime):
        return date.isoformat()
    elif isinstance(date, str):
        try:
            datetime.fromisoformat(date)
            return date
        except ValueError:
            logger.warning('Date string is not in valid ISO format: %s', date)
            return DEFAULT_DATE
    else:
        return DEFAULT_DATE


def update_state(last_film_date=None, last_genre_date=None,
                 last_person_date=None, last_person_info_date=None, last_genre_info_date=None):
    try:
        state = get_state()

        state['last_film_date'] = serialize_date(
            last_film_date) if last_film_date is not None else state['last_film_date']
        state['last_genre_date'] = serialize_date(
            last_genre_date) if last_genre_date is not None else state['last_genre_date']
        state['last_person_date'] = serialize_date(
            last_person_date) if last_person_date is not None else state['last_person_date']
        state['last_person_info_date'] = serialize_date(
            last_person_info_date) if last_person_info_date is not None else state['last_person_info_date']
        state['last_genre_info_date'] = serialize_date(
            last_genre_info_date) if last_genre_info_date is not None else state['last_genre_info_date']

        with open(STATE_FILE, 'w') as file:
            json.dump(state, file)

    except Exception as e:
        logger.error('Error writing state file: %s', e)

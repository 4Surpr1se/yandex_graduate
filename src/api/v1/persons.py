import logging
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4, BaseModel

from models.person import Person
from services.person import PersonService, get_person_service

router = APIRouter()


class Film(BaseModel):
    uuid: UUID4
    title: str
    imdb_rating: float


@router.get("/search", response_model=List[Person])
async def search_persons(
    query: str,
    page_number: int = 1,
    page_size: int = 50,
    person_service: PersonService = Depends(get_person_service)
) -> List[Person]:
    logging.info(f"API call: search_persons with query={query}, page_number={page_number}, page_size={page_size}")
    persons = await person_service.search_persons(query)
    start = (page_number - 1) * page_size
    end = start + page_size
    return persons[start:end]


@router.get("/{uuid}", response_model=Person)
async def get_person(uuid: str, person_service: PersonService = Depends(get_person_service)
                     ) -> Person:
    logging.info(f"API call: get_person with uuid={uuid}")
    person = await person_service.get_person_by_id(uuid)
    if person is None:
        logging.error(f"Person not found with uuid={uuid}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")
    return person


@router.get("/{uuid}/film", response_model=List[Film])
async def get_films_by_person(uuid: str, person_service: PersonService = Depends(get_person_service)) -> List[Film]:
    logging.info(f"API call: get_films_by_person with uuid={uuid}")
    films = await person_service.get_films_by_person_id(uuid)
    if not films:
        logging.error(f"Films not found for person with uuid={uuid}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Films not found")
    return films

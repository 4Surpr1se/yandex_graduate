import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request

from models.person import Person
from services.person import PersonService, get_person_service
from services.base_service import ItemsModel
from services.search_persons import search_persons_service, SearchPersonService

router = APIRouter()


@router.get("/search", response_model=ItemsModel)
async def search_persons(
    request: Request,
    search_service: SearchPersonService = Depends(search_persons_service)
) -> ItemsModel:
    query_params = request.query_params
    logging.info(
        f"API call: search_persons with specific query: {query_params}")
    persons = await search_service.get_items(query_params)
    return persons


@router.get("/{uuid}", response_model=Person)
async def get_person(uuid: str, person_service: PersonService = Depends(get_person_service)
                     ) -> Person:
    logging.info(f"API call: get_person with uuid={uuid}")
    person = await person_service.get_by_id(uuid)
    if person is None:
        logging.error(f"Person not found with uuid={uuid}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="Person not found")
    return person


@router.get("/{uuid}/film", response_model=ItemsModel)
async def get_films_by_person(uuid: str, request: Request,
                              person_service: PersonService = Depends(get_person_service)) -> ItemsModel:
    logging.info(f"API call: get_films_by_person with uuid={uuid}")
    query_params = request.query_params
    films = await person_service.get_films_by_person_id(query_params, uuid)
    if not films:
        logging.error(f"Films not found for person with uuid={uuid}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="Films not found")
    return films

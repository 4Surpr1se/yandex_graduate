import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from models.person import Person
from services.base_service import ItemsModel
from services.person import PersonService, get_person_service
from services.search_persons import SearchPersonService, search_persons_service

router = APIRouter()


@router.get("/search", response_model=ItemsModel)
async def search_persons(request: Request, response: Response,
                         search_service: SearchPersonService = Depends(search_persons_service)
                         ) -> ItemsModel:
    try:
        query_params = request.query_params
    except Exception as e:
        query_params = {}
        print(e)
    logging.info(
        f"API call: search_persons with specific query: {query_params}")
    persons = await search_service.get_items(request=request, response=response, query_params=query_params)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Persons not found')
    return persons


@router.get("/{uuid}", response_model=Person)
async def get_person(uuid: str, request: Request, response: Response,
                     person_service: PersonService = Depends(get_person_service)
                     ) -> Person:
    logging.info(f"API call: get_person with uuid={uuid}")
    person = await person_service.get_by_id(item_id=uuid, request=request, response=response)
    if person is None:
        logging.error(f"Person not found with uuid={uuid}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="Person not found")
    return person


@router.get("/{uuid}/film", response_model=ItemsModel)
async def get_films_by_person(uuid: str, request: Request, response: Response,
                              person_service: PersonService = Depends(get_person_service)
                              ) -> ItemsModel:
    logging.info(f"API call: get_films_by_person with uuid={uuid}")
    query_params = request.query_params
    films = await person_service.get_films_by_person_id(request=request, response=response,
                                                        query_params=query_params, person_id=uuid)
    if not films:
        logging.error(f"Films not found for person with uuid={uuid}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="Films not found")
    return films

from fastapi import APIRouter, Depends, HTTPException, Request
from services.persons import PersonService, get_person_service
from models.person import Person, PersonFilm
from typing import List
from http import HTTPStatus

router = APIRouter()

@router.get("/search", response_model=List[Person])
async def search_persons(request: Request, person_service: PersonService = Depends(get_person_service)):
    query_params = request.query_params
    persons = await person_service.search_persons(query_params)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Persons not found")
    return persons

@router.get("/{person_id}", response_model=Person)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)):
    person = await person_service.get_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Person not found")
    return person

@router.get("/{person_id}/film", response_model=List[PersonFilm])
async def person_films(person_id: str, person_service: PersonService = Depends(get_person_service)):
    films = await person_service.get_person_films(person_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Films not found for this person")
    return films

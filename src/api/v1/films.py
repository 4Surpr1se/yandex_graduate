from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from models.film import Film
from services.film import FilmService, get_film_service
from services.films import Films, FilmsService, get_films_service

router = APIRouter()


@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not found')
    return film


@router.get('', response_model=Films)
async def films_details(request: Request, film_service: FilmsService = Depends(get_films_service)) -> Films:
    query_params = request.query_params
    films = await film_service.get_films(query_params)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='films not found')
    return films

from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from models.genre import Genre
from services.base_service import ItemsModel
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get('', response_model=ItemsModel)
async def get_genres(request: Request, response: Response,
                     genre_service: GenreService = Depends(get_genre_service)) -> ItemsModel:
    query_params = request.query_params
    genres = await genre_service.get_items(request=request, response=response, query_params=query_params)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genres not found')
    return genres


@router.get('/{genre_id}', response_model=Genre)
async def get_genre(genre_id: str, request: Request, response: Response,
                    genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(item_id=genre_id, request=request, response=response)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genre not found')
    return genre

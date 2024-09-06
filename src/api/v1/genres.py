from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request

from models.genre import Genre
from services.genre import GenreService, get_genre_service
from services.base_service import ItemsModel

router = APIRouter()


@router.get('', response_model=ItemsModel)
async def get_genres(request: Request,
                     genre_service: GenreService = Depends(get_genre_service)) -> ItemsModel:
    query_params = request.query_params
    genres = await genre_service.get_items(request=request, query_params=query_params)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genres not found')
    return genres


@router.get('/{genre_id}', response_model=Genre)
async def get_genre(genre_id: str, request: Request,
                    genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(item_id=genre_id, request=request)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genre not found')
    return genre

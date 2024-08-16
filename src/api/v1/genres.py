from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.genre import Genre
from services.genre import GenreService, get_genre_service
from services.base_service import ItemsModel

router = APIRouter()


@router.get('', response_model=ItemsModel)
async def get_genres(genre_service: GenreService = Depends(get_genre_service)) -> ItemsModel:
    genres = await genre_service.get_items()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genres not found')
    return genres


@router.get('/{genre_id}', response_model=Genre)
async def get_genre(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genre not found')
    return genre

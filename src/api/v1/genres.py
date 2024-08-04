from fastapi import APIRouter, Depends, HTTPException
from services.genres import GenreService, get_genre_service
from models.genre import Genre
from typing import List
from http import HTTPStatus

router = APIRouter()

@router.get("/", response_model=List[Genre])
async def genres_list(genre_service: GenreService = Depends(get_genre_service)):
    genres = await genre_service.get_genres()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Genres not found")
    return genres

@router.get("/{genre_id}", response_model=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)):
    genre = await genre_service.get_genre_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Genre not found")
    return genre

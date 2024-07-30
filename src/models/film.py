from pydantic import BaseModel, Field, UUID4
from typing import List, Optional, Literal
from datetime import datetime


class Genre(BaseModel):
    """
    Represents a genre with an ID, name, and optional description.

    Attributes:
        id (UUID4): Unique identifier for the genre.
        name (str): Name of the genre.
        description (Optional[str]): Description of the genre, defaults to None.
    """
    id: UUID4
    name: str
    description: Optional[str] = None


class Person(BaseModel):
    """
    Represents a person with an ID and full name.

    Attributes:
        id (UUID4): Unique identifier for the person.
        full_name (str): Full name of the person.
    """
    id: UUID4
    full_name: str


class FilmPersonRole(BaseModel):
    """
    Represents a film-person role relationship with a film ID and list of roles.

    Attributes:
        film_id (UUID4): Unique identifier for the film.
        role (List[Literal['actor', 'writer', 'director']]): List of roles the person has in the film.
    """
    film_id: UUID4
    role: List[Literal['actor', 'writer', 'director']] = []


class PersonDetail(Person):
    """
    Represents detailed information about a person, including their films and roles in those films.

    Attributes:
        id (UUID4): Unique identifier for the person.
        full_name (str): Full name of the person.
        films (List[FilmPersonRole]): List of films and roles the person has in each film.
    """
    films: List[FilmPersonRole] = []


class Film(BaseModel):
    """
    Represents a film with various attributes including title, description, creation date, IMDb rating,
    file path, type, genres, and lists of actors, directors, and writers.

    Attributes:
        id (UUID4): Unique identifier for the film.
        title (str): Title of the film.
        description (Optional[str]): Description of the film, defaults to None.
        creation_date (Optional[datetime]): Creation date of the film, defaults to None.
        imdb_rating (Optional[float]): IMDb rating of the film, defaults to None. Must be between 0 and 10.
        file_path (Optional[str]): File path of the film, defaults to None.
        type (str): Type of the film (e.g., movie, series).
        genres (List[str]): List of genres associated with the film.
        actors (List[Person]): List of actors in the film.
        directors (List[Person]): List of directors of the film.
        writers (List[Person]): List of writers of the film.
    """
    id: UUID4
    title: str
    description: Optional[str] = None
    creation_date: Optional[datetime] = None
    imdb_rating: Optional[float] = Field(None, ge=0, le=10)
    file_path: Optional[str] = None
    type: str
    genres: List[str] = []
    actors: List[Person] = []
    directors: List[Person] = []
    writers: List[Person] = []

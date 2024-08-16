from pydantic import BaseModel, Field


class CacheConfig(BaseModel):
    film_cache_expire_in_seconds: int = Field(60 * 5, alias="FILM_CACHE_EXPIRE_IN_SECONDS")
    genres_cache_expire_in_seconds: int = Field(30, alias="GENRES_CACHE_EXPIRE_IN_SECONDS")
    films_cache_expire_in_seconds: int = Field(int(60 * 0.5), alias="FILMS_CACHE_EXPIRE_IN_SECONDS")
    persons_cache_expire_in_seconds: int = Field(60, alias="PERSONS_CACHE_EXPIRE_IN_SECONDS")

    def get_expiration_time(self, service_name: str) -> int:
        service_field = f"{service_name.lower()}_cache_expire_in_seconds"
        return getattr(self, service_field)


cache_config = CacheConfig()

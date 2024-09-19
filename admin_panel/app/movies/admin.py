from django.contrib import admin

from .custom_filters import RatingFilter
from .models import (Filmwork, FilmworkGenre, FilmworkPerson, Genre, Person,
                     User)


class GenreFilmworkInline(admin.TabularInline):
    model = FilmworkGenre


class PersonFilmworkInline(admin.TabularInline):
    model = FilmworkPerson


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'created_at', 'updated_at', 'get_filmworks')
    search_fields = ('full_name',)
    inlines = (PersonFilmworkInline,)

    def get_filmworks(self, obj):
        return ", ".join([fw.title for fw in obj.filmwork_set.all()])

    get_filmworks.short_description = 'Filmworks'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    inlines = (GenreFilmworkInline,)


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'type', 'creation_date', 'rating', 'created_at', 'updated_at'
    )
    list_filter = ('type', RatingFilter)
    search_fields = ('title', 'description', 'id')
    inlines = (GenreFilmworkInline, PersonFilmworkInline)

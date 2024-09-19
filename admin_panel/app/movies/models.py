import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import MyUserManager
from .mixin import TimeStampedMixin, UUIDMixin


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    # строка с именем поля модели, которая используется в качестве уникального идентификатора
    USERNAME_FIELD = 'email'

    # менеджер модели
    objects = MyUserManager()

    def __str__(self):
        return f'{self.email} {self.id}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')
        constraints = [
            models.UniqueConstraint(fields=['name'], name='idx_genre_name'),
        ]

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('full name'), max_length=255)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('Person')
        verbose_name_plural = _('People')
        constraints = [
            models.UniqueConstraint(
                fields=['full_name'],
                name='idx_person_full_name'
            ),
        ]

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    creation_date = models.DateField(
        _('creation date'), null=True, blank=True
    )
    rating = models.FloatField(
        _('rating'), null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    file_path = models.CharField(
        _('path'), max_length=255, null=True, blank=True
    )

    class WorkType(models.TextChoices):
        MOVIE = 'movie', _('Movie')
        TV_SHOW = 'tv_show', _('TV Show')

    type = models.CharField(
        _('type'),
        max_length=15,
        choices=WorkType.choices
    )

    genres_list = models.ManyToManyField(Genre, through='FilmworkGenre')
    persons = models.ManyToManyField(Person, through='FilmworkPerson')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('Movie')
        verbose_name_plural = _('Movies')
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'creation_date'],
                name='idx_film_work_title_creation_date'
            ),
        ]

    def __str__(self):
        return self.title


class FilmworkGenre(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = _('Movie genre')
        verbose_name_plural = _('Movie genres')
        constraints = [
            models.UniqueConstraint(
                fields=['genre', 'film_work'],
                name='idx_genre_film_work_genre_id_film_work_id'
            ),
        ]


class FilmworkPerson(UUIDMixin):

    class Roles(models.TextChoices):
        actor = 'actor', _('Actor')
        writer = 'writer', _('Writer')
        director = 'director', _('Director')

    role = models.CharField(
        _('role'),
        max_length=15,
        choices=Roles.choices
    )

    created_at = models.DateTimeField(_('created'), auto_now_add=True)
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = _('Person in movie')
        verbose_name_plural = _('People in movie')
        constraints = [
            models.UniqueConstraint(
                fields=['person', 'film_work', 'role'],
                name='idx_person_film_work_person_id_film_work_id_role'
            ),
        ]

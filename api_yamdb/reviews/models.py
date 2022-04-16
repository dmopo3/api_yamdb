from enum import Enum
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator
)
from django.db import models

from .validators import validate_year


class UserRole(Enum):
    user = 'user'
    moderator = 'moderator'
    admin = 'admin'

    @classmethod
    def choices(cls):
        return(tuple((i.name, i.value) for i in cls))


def username_not_me(value):
    return value != 'me'


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-+\\z]'
        ), username_not_me]
    )
    first_mane = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=254, unique=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=99,
        choices=UserRole.choices(),
        default=UserRole.user.value
    )
    confirmation_code = models.CharField(
        max_length=254, default='XXXX', null=True
    )

    @property
    def is_admin(self):
        return self.role == UserRole.admin.value or self.is_staff

    @property
    def is_moderator(self):
        return self.role == UserRole.moderator.value

    def __str__(self) -> str:
        return self.username


class Categories(models.Model):
    """Категории произведений (Фильмы, книги и тд)."""

    name = models.CharField('Категория', max_length=256)
    slug = models.SlugField('Слак', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категории'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.name


class Genres(models.Model):
    """Жанры произведений."""

    name = models.CharField('Жанр', max_length=256)
    slug = models.SlugField('Слак', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанры'
        verbose_name_plural = 'Жанры'

    def __str__(self) -> str:
        return self.name


class Title(models.Model):
    """Произведения."""

    name = models.TextField('Название произведения', db_index=True)
    year = models.IntegerField(
        'Дата выхода произведения', validators=[validate_year], blank=True
    )
    description = models.TextField('Описание')
    genre = models.ManyToManyField(
        Genres,
        related_name='titles',
        blank=True,
    )
    category = models.ForeignKey(
        Categories,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Произведении'
        verbose_name_plural = 'Произведении'
        ordering = ['-id']

    def __str__(self) -> str:
        return self.name


class Review(models.Model):
    """Отзывы на произведения."""

    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField(
        verbose_name='Текст отзыва',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор отзыва',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        default=1,
        validators=[
            MinValueValidator(1, 'Минимальное значение 1'),
            MaxValueValidator(10, 'максимальное значение 10'),
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации отзыва',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review',
            )
        ]

    def __str__(self):
        return self.text


class Comments(models.Model):
    """Коментарии к отзывам."""

    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации отзыва',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['pub_date']

    def __str__(self):
        return self.text

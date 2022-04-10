from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year


class User(AbstractUser):
    """Модель пользователя."""

    roles = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    )
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=99, choices=roles, default='user')
    confirmation_code = models.CharField(
        max_length=254, default='XXXX', null=True
    )

    def __str__(self) -> str:
        return self.username


class Categories(models.Model):
    """Категории произведений (Фильмы, книги и тд)."""

    name = models.CharField('Категория', max_length=30)
    slug = models.SlugField('Слак', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категории'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.name


class Genres(models.Model):
    """Жанры произведений."""

    name = models.CharField('Жанр', max_length=30)
    slug = models.SlugField('Слак', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанры'
        verbose_name_plural = 'Жанры'

    def __str__(self) -> str:
        return self.name


class Titles(models.Model):
    """Произведения."""

    name = models.CharField(
        'Название произведения', max_length=200, db_index=True
    )
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

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Произведении'
        verbose_name_plural = 'Произведении'
        ordering = ['-id']


class Reviews(models.Model):
    """Отзывы на произведения."""

    title = models.ForeignKey(
        Titles,
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
        blank=False,
        null=False,
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
        Reviews,
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

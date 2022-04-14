from django.contrib import admin

from .models import Comments, Review, User, Categories, Genres, Title


class UserAdmin(admin.ModelAdmin):
    list_display = [i.name for i in User._meta.fields if i != 'id']


class ReviewAdmin(admin.ModelAdmin):
    """Класс для отображения полей отзыва в админке."""

    list_display = (
        'pk',
        'text',
        'author',
        'score',
        'pub_date',
        'title',
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CommentsAdmin(admin.ModelAdmin):
    """Класс для отображения полей комментария в админке."""

    list_display = (
        'pk',
        'text',
        'author',
        'pub_date',
        'review',
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CategoriesAdmin(admin.ModelAdmin):
    """Класс для отображения категории в админке"""

    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class GenresAdmin(admin.ModelAdmin):
    """Класс для отображения жанра в админке"""

    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class TitleAdmin(admin.ModelAdmin):
    """Класс для отображения произведений в админке"""

    list_display = ('pk', 'name', 'year', 'description', 'category')
    search_fields = ('name',)
    list_filter = ('year', 'category', 'genre')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Genres, GenresAdmin)
admin.site.register(Title, TitleAdmin)

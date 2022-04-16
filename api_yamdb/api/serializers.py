from django.forms import ValidationError

from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from django.core.validators import RegexValidator

from reviews.models import Comments, Review, Title, User, Categories, Genres


class SendEmailSerializer(serializers.Serializer):
    """Сериализатор для функции регистрации"""

    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-+\\z]'
        )]
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, attr):
        if attr.get('username') == 'me':
            raise ValidationError('username ME не может быть использовано')
        return attr


class SendTokenSerializer(serializers.Serializer):
    """Сериализатор для функции предоставления токена."""

    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-+\\z]'
        )]
    )

    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор данных пользователя"""

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'bio',
            'email',
            'role',
        )


class UserNotAdminSerializer(serializers.ModelSerializer):
    """Сериализатор данных пользователя"""

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'bio',
            'email',
            'role',
        )
        read_only_fields = ('role',)


class ReviewSerializer(serializers.ModelSerializer):
    """Класс для преобразования данных отзыва."""

    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')

    def validate(self, attr):
        request = self.context['request']
        if request.method != 'POST':
            return attr
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if Review.objects.filter(title=title, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на данное произведение'
            )
        return attr


class CommentsSerializer(serializers.ModelSerializer):
    """Класс для преобразования данных комментария."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comments
        fields = ('id', 'text', 'author', 'pub_date')


class CategoriesSerializer(serializers.ModelSerializer):
    """Класс сериализатор категории."""

    class Meta:
        model = Categories
        fields = ('name', 'slug')


class GenresSerializer(serializers.ModelSerializer):
    """Класс сериализатор жанра."""

    class Meta:
        model = Genres
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField()

    genre = GenresSerializer(many=True, read_only=True)
    category = CategoriesSerializer(many=False, read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )
        read_only_fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )


class TitleCreateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genres.objects.all(), slug_field='slug', many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Categories.objects.all(), slug_field='slug'
    )

    class Meta:
        fields = '__all__'
        model = Title

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
)

from reviews.models import Review, Title, User, Categories, Genres
from api_yamdb.settings import EMAIL_FROM
from .permissions import (
    AdminOnly,
    IsAdminModeratorOwnerOrReadOnly,
    IsAdminOrReadOnly,
)
from .serializers import (
    SendEmailSerializer,
    UserSerializer,
    UserNotAdminSerializer,
    CommentsSerializer,
    ReviewSerializer,
    SendTokenSerializer,
    CategoriesSerializer,
    GenresSerializer,
    TitleCreateSerializer,
    TitleReadSerializer,
)
from .filters import TitleFilter


class CreateListDestroyViewSet(
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, AdminOnly)
    pagination_class = LimitOffsetPagination
    lookup_field = 'username'
    filter_backend = filters.SearchFilter
    search_fields = ('username',)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me',
    )
    def get_current_user_info(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UserSerializer(
                    request.user, data=request.data, partial=True
                )
# если пользователь не админ, то поле ROLE должно быть READ_ONLY
# как это реализовать в одном сериализаторе я не придумал
            else:
                serializer = UserNotAdminSerializer(
                    request.user, data=request.data, partial=True
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


class Registration(APIView):
    permission_classes = [AllowAny]
    pagination_class = LimitOffsetPagination

    def post(self, request):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if (not User.objects.filter(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email']
        ).exists()
            and User.objects.filter(
                email=serializer.validated_data['email']
        ).exists()):
            return Response('Email занят', status=status.HTTP_400_BAD_REQUEST)
        if (not User.objects.filter(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email']
        ).exists()
            and User.objects.filter(
            username=serializer.validated_data['username']
        ).exists()):
            return Response(
                'username занят', status=status.HTTP_400_BAD_REQUEST
            )
# Без этих двух ифов тесты валятся, как понимаю, try/except
# не может обработать случай, когда имеил пренадлежит другому пользователю
        try:
            user = User.objects.get_or_create(
                email=serializer.validated_data['email'],
                username=serializer.validated_data['username'],
                is_active=False,
            )[0]
        except Exception as ex:
            return Response(ex, stasus=status.HTTP_400_BAD_REQUEST)
        confirmation_code = PasswordResetTokenGenerator().make_token(user)
        email = serializer.validated_data['email']
        send_mail(
            'Welcome to yamdb',
            f'code: {confirmation_code}',
            EMAIL_FROM,
            [email],
            fail_silently=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendToken(APIView):
    permission_classes = [AllowAny]
    pagination_class = LimitOffsetPagination

    def post(self, request):
        serializer = SendTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        try:
            user = get_object_or_404(
                User,
                username=username,
            )
        except User.DoesNotExist:
            return Response('Ошибка в username',
                            status=status.HTTP_404_NOT_FOUND)
        if not PasswordResetTokenGenerator().check_token(user,
                                                         confirmation_code):
            return Response('Неверный код подтверждения',
                            status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken.for_user(user).access_token
        user.is_active = True
        user.save()
        return Response(f'token: {str(token)}', status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    """Класс для работы с оценками."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    """Класс для работы с комментариями."""

    serializer_class = CommentsSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)


class CategoriesViewSet(CreateListDestroyViewSet):
    """Вьюсет для категории."""

    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = LimitOffsetPagination
    search_fields = ('=name',)
    lookup_field = 'slug'


class GenresViewSet(CreateListDestroyViewSet):
    """Вьюсет для жанра."""

    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = LimitOffsetPagination
    search_fields = ('=name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений"""

    queryset = (
        Title.objects.all()
        .annotate(rating=Avg('reviews__score'))
        .order_by('id')
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TitleReadSerializer
        return TitleCreateSerializer

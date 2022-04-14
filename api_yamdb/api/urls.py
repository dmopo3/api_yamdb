from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CommentsViewSet,
    CategoriesViewSet,
    UserViewSet,
    GenresViewSet,
    TitleViewSet,
    Registration,
    ReviewViewSet,
    SendToken
)

router = DefaultRouter()
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router.register(
    'users', UserViewSet, basename='users'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)' r'/comments',
    CommentsViewSet,
    basename='comments',
)
router.register('categories', CategoriesViewSet, basename='categories')
router.register('genres', GenresViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', Registration.as_view()),
    path('v1/auth/token/', SendToken.as_view()),
]

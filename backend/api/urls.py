from django.urls import include, path
from rest_framework import routers

from api.views import IngredientViewSet, TagViewSet, UserViewSet

# from api.views import (
#     CategoryViewSet, CommentViewSet, GenreViewSet, GetTokenViewSet,
#     ReviewViewSet, SignUpViewSet, TitleViewSet, UserViewSet)


app_name = 'api'

router = routers.DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
# router_v1.register('auth/signup', SignUpViewSet, basename='signup')
# router_v1.register('auth/token', GetTokenViewSet, basename='token')
router.register('users', UserViewSet, basename='user')
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
#     'title-reviews')
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet, 'review-comments'
# )
# router_v1.register('genres', GenreViewSet)
# router_v1.register('categories', CategoryViewSet)
# router_v1.register('titles', TitleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

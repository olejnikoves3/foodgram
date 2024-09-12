from django.urls import include, path
from rest_framework import routers

# from api.views import (
#     CategoryViewSet, CommentViewSet, GenreViewSet, GetTokenViewSet,
#     ReviewViewSet, SignUpViewSet, TitleViewSet, UserViewSet)


app_name = 'api'

router_v1 = routers.DefaultRouter()
# router_v1.register('auth/signup', SignUpViewSet, basename='signup')
# router_v1.register('auth/token', GetTokenViewSet, basename='token')
# router_v1.register('users', UserViewSet, basename='user')
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

v1_endpoints = [
    path('', include(router_v1.urls)),
]
urlpatterns = [
    path('v1/', include(v1_endpoints)),
]

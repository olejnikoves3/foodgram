from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.pagination import LimitOffsetPagination

from api.serializers import IngredientSerializer, TagSerializer, UserSerializer
from recipes.models import (Ingredient, Follow, Recipe, RecipeIngredient,
                            Tag)


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # Разобраться с поиском
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('^name', 'name')
    search_fields = ('^name', 'name')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    #http_method_names = ['get', 'post', 'patch', 'delete']

    # @action(detail=False, methods=['get', 'patch'],
    #         #permission_classes=[IsAuthenticated],
    #         url_path='me')
    # def me(self, request):
    #     if request.method == 'GET':
    #         serializer = self.get_serializer(request.user)
    #         return Response(serializer.data)
    #     serializer = self.get_serializer(
    #         request.user, data=request.data,
    #         partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(role=request.user.role)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

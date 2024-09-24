from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers import (
    AvatarSerializer, IngredientSerializer, RecipeCreateUpdateSerializer,
    RecipeReadSerializer, TagSerializer,
    UserSerializer, UserRegisterSerializer
)
from recipes.models import (Cart, Ingredient, Recipe, Tag)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # Разобраться с поиском
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # filterset_fields = ('^name', 'name')
    search_fields = ('^name', 'name')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserRegisterSerializer
        return UserSerializer

    @action(detail=False, url_path='me')
    def me(self, request):
        user = self.request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'delete'],
            url_path='me/avatar')
    def avatar(self, request):
        user = self.request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.avatar = serializer.validated_data['avatar']
            user.save()
            avatar_url = request.build_absolute_uri(user.avatar.url)
            return Response({'avatar': avatar_url}, status=status.HTTP_200_OK)
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author',)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipeCreateUpdateSerializer
        return RecipeReadSerializer

    def get_queryset(self):
        queryset = Recipe.objects.prefetch_related(
            'tags', 'ingredients').select_related('author')

        # Фильтр по избранному
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1':
            queryset = queryset.filter(favorited_by__user=self.request.user)
        elif is_favorited == '0':
            queryset = queryset.exclude(favorited_by__user=self.request.user)

        # Фильтр по списку покупок
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart == '1':
            queryset = queryset.filter(
                in_shopping_cart__user=self.request.user)
        elif is_in_shopping_cart == '0':
            queryset = queryset.exclude(
                in_shopping_cart__user=self.request.user)

        # Фильтр по автору
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        # Фильтр по тегам (массив строк через запятую)
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

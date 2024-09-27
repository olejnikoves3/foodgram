from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientSearch
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer, IngredientSerializer, RecipeCreateSerializer,
    RecipeUpdateSerializer, RecipeReadSerializer, ShortRecipeSerializer,
    TagSerializer, UserSerializer, UserRegisterSerializer, UserWithRecipes
)
from recipes.models import (Cart, Follow, Ingredient, Recipe, Tag)


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [IngredientSearch]
    search_fields = ['name']


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserRegisterSerializer
        return UserSerializer

    @action(['post'], detail=False)
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.data["new_password"])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(['put', 'delete'], False,
            permission_classes=[IsAuthenticated],
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

    @action(['get'], False, permission_classes=[IsAuthenticated], )
    def subscriptions(self, request):
        user = request.user
        paginator = LimitOffsetPagination()
        queryset = User.objects.filter(followers__user=user).annotate(
            recipe_count=Count('recipes')).order_by('-id')
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = UserWithRecipes(paginated_queryset, many=True,
                                     context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @action(['post'], True, permission_classes=[IsAuthenticated],)
    def subscribe(self, request, pk=None):
        user = request.user
        user_to_follow = get_object_or_404(User, id=pk)
        if user == user_to_follow:
            return Response('Нельзя подписаться на самого себя',
                            status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=user, following=user_to_follow):
            return Response('Вы уже подписаны на этого пользователя',
                            status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.create(user=user, following=user_to_follow)
        obj = User.objects.annotate(recipes_count=Count('recipes')).get(id=pk)
        serializer = UserWithRecipes(obj, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscription(self, request, pk=None):
        user = request.user
        user_to_unfollow = get_object_or_404(User, id=pk)
        if Follow.objects.filter(
                user=user, following=user_to_unfollow).exists():
            Follow.objects.filter(
                user=user, following=user_to_unfollow).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Вы не подписаны на этого пользователя',
                        status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author',)
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecipeCreateSerializer
        elif self.request.method == 'PATCH':
            return RecipeUpdateSerializer
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
        self.object = serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        self.object = serializer.save()

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        serializer = RecipeReadSerializer(instance=self.object,
                                          context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        serializer = RecipeReadSerializer(instance=self.object,
                                          context={'request': request})
        return Response(serializer.data)

    @action(['post'], True, permission_classes=[IsAuthenticated],)
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if Cart.objects.filter(user=user, recipe=recipe).exists():
            return Response('Рецепт уже добавлен в корзину',
                            status=status.HTTP_400_BAD_REQUEST)
        Cart.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe,
                                           context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if Cart.objects.filter(user=user, recipe=recipe).exists():
            Cart.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('Рецепт не был добавлен в корзину',
                        status=status.HTTP_400_BAD_REQUEST)

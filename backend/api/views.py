from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect
from djoser.serializers import SetPasswordSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,)
from rest_framework.response import Response
import short_url

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer, IngredientSerializer, FollowSerializer,
    RecipeCreateSerializer, RecipeReadSerializer, RecipeUpdateSerializer,
    TagSerializer, UserRecipeRelationCreateSerializer,
    UserRegisterSerializer, UserSerializer, UserWithRecipes
)
from api.utils import generate_pdf
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from users.models import Follow


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


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
        request.user.set_password(serializer.data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'], False, permission_classes=[IsAuthenticated])
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
        paginator = CustomPagination()
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
        serializer = FollowSerializer(
            data={'user': user.id, 'following': user_to_follow.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
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
        return Response('Вы не подписаны на этого пользователя.',
                        status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.prefetch_related(
        'tags', 'ingredients').select_related('author')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecipeCreateSerializer
        elif self.request.method == 'PATCH':
            return RecipeUpdateSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        self.object = serializer.save(author=self.request.user)

    @action(['get'], False, permission_classes=[IsAuthenticated],)
    def download_shopping_cart(self, request):
        user = request.user
        ingredients_summary = user.cart_set.values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit'
        ).annotate(total_amount=Sum('recipe__recipe_ingredients__amount'))
        return generate_pdf(ingredients_summary)

    def create_user_recipe_relation(self, request, model, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = UserRecipeRelationCreateSerializer(
            data={'user': user.id, 'recipe': recipe.id},
            model_class=model, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_user_recipe_relation(self, request, model, pk, error_msg=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            model.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

    @action(['post'], True, permission_classes=[IsAuthenticated],)
    def shopping_cart(self, request, pk=None):
        return self.create_user_recipe_relation(request, Cart, pk)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk=None):
        error_msg = 'Рецепт не был добавлен в корзину.'
        return self.delete_user_recipe_relation(request, Cart, pk, error_msg)

    @action(['post'], True, permission_classes=[IsAuthenticated],)
    def favorite(self, request, pk=None):
        return self.create_user_recipe_relation(request, Favorite, pk)

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk=None):
        error_msg = 'Рецепт не был добавлен в избранное.'
        return self.delete_user_recipe_relation(request, Favorite, pk,
                                                error_msg)

    @action(['get'], True, permission_classes=[AllowAny],
            url_path='get-link')
    def get_link(self, request, pk=None):
        domain = request.get_host()
        s_url = short_url.encode_url(int(pk))
        url = f'https://{domain}/s/{s_url}'
        return Response({'short-link': url}, status=status.HTTP_200_OK)


def recipe_from_short_link(request, link):
    id = short_url.decode_url(link)
    recipe = get_object_or_404(Recipe, id=id)
    return redirect(f'/recipes/{recipe.id}')

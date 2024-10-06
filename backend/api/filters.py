from django.db.models import Case, When, Value, IntegerField
from rest_framework.filters import BaseFilterBackend


class IngredientSearch(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        name = request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
            queryset = queryset.annotate(
                starts_with=Case(
                    When(name__istartswith=name, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            ).order_by('starts_with', 'name')
        return queryset


class RecipeFilter (BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        author_id = request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author__id=author_id)
        tags = request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        is_favorited = request.query_params.get('is_favorited')
        if is_favorited == '1' and request.user.is_authenticated:
            queryset = queryset.filter(in_favorite__user=request.user)
        is_in_shopping_cart = request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart == '1' and request.user.is_authenticated:
            queryset = queryset.filter(in_users_carts__user=request.user)
        return queryset

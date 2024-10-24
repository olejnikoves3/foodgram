from django_filters.rest_framework import BooleanFilter, CharFilter, FilterSet

from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')
    is_favorited = BooleanFilter(method='filter_is_favorited')
    tags = CharFilter(method="filter_tags")

    class Meta:
        model = Recipe
        fields = ('is_in_shopping_cart', 'is_favorited', 'author',
                  'tags')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(cart__user=user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorite__user=user)
        return queryset

    def filter_tags(self, queryset, name, value):
        if value:
            tags = self.request.GET.getlist('tags')
            return queryset.filter(tags__slug__in=tags).distinct()
        return queryset

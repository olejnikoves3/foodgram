from django.contrib import admin
from django.contrib.auth.models import Group

from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = ('name', 'author', 'text', 'cooking_time',
              'image', 'favorite_count')
    list_display = ('name', 'author', 'in_favorite_count',)
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    readonly_fields = ('favorite_count',)

    @admin.display(description='В избранном')
    def in_favorite_count(self, obj):
        return obj.favorite_set.count()

    @admin.display(description='Количество добавлений в избранное')
    def favorite_count(self, obj):
        return obj.favorite_set.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    pass


admin.site.unregister(Group)

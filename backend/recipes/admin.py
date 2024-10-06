from django.contrib import admin

from recipes.models import (Cart, Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, Tag, User,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = ('name', 'author', 'text', 'cooking_time',
              'image', 'favorite_count')
    list_display = ('name', 'author', 'in_favorite_count',)
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    readonly_fields = ('favorite_count',)

    @admin.display(description='В избранном')
    def in_favorite_count(self, obj):
        return obj.in_favorite.count()

    @admin.display(description='Количество добавлений в избранное')
    def favorite_count(self, obj):
        return obj.in_favorite.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = (
        'username',
        'email'
    )
    ordering = ('username',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    pass

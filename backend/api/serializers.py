import re

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, Tag,)
from users.models import Follow


User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                'Недопустимые символы в имени пользователя.'
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.followers.filter(user=user).exists()
        return False


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following'],
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate_following(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError(
                'Нельзя подписываться на сомого себя')
        return value


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True, source='recipe_ingredients',
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        ]
        read_only_fields = ('author', 'tags', 'ingredients',)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.favorite_set.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.cart_set.filter(user=user).exists()
        return False


class ShortRecipeSerializer(RecipeReadSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True
    )
    ingredients = RecipeIngredientWriteSerializer(
        source='recipe_ingredients', many=True, required=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        recipe_ingredient_objs = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            ) for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredient_objs)
        return recipe

    def update(self, instance, validated_data):
        basic, many2us = self.split_validated_data(validated_data)
        return self.update_many2us(super().update(instance, basic), many2us)

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле не может быть пустым.'
            )
        unique_tags = {tag.id for tag in value}
        if len(value) != len(unique_tags):
            raise serializers.ValidationError(
                'В запросе содержатся повторяющиеся теги.'
            )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле не может быть пустым.'
            )
        unique_ingredients = {ing['id'].id for ing in value}
        if len(value) != len(unique_ingredients):
            raise serializers.ValidationError(
                'В запросе содержатся повторяющиеся ингридиенты.'
            )
        return value

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context=self.context
        ).data


class RecipeUpdateSerializer(RecipeCreateSerializer):
    image = Base64ImageField(required=False)

    def validate(self, data):
        required_fields = [
            'tags', 'recipe_ingredients', 'name', 'text', 'cooking_time'
        ]
        missing_fields = [
            field for field in required_fields if field not in data
        ]
        if missing_fields:
            raise serializers.ValidationError(
                f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
            )
        return data


class UserWithRecipes(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        try:
            limit = int(request.query_params.get('recipes_limit'))
            recipes = recipes[:limit]
        except TypeError:
            pass
        return ShortRecipeSerializer(recipes, many=True,
                                     context={'request': request}).data

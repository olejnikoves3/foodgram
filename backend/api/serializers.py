import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Cart, Ingredient, Favorite, Follow, Recipe, RecipeIngredient, RecipeTag,
    Tag
)

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
            return Follow.objects.filter(user=user, following=obj).exists()
        return False


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    default = serializers.CurrentUserDefault()

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
        fields = ['id', 'name', 'measurement_unit', 'amount']


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
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Cart.objects.filter(user=user, recipe=obj).exists()
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
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True,
    )
    ingredients = RecipeIngredientWriteSerializer(
        source='recipe_ingredients', many=True,
    )
    image = Base64ImageField()

    MANY_FIELDS = {'tags': 'update_tags',
                   'recipe_ingredients': 'update_ingredients'
                   }

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time')

    @classmethod
    def update_tags(cls, instance, data):
        old_tags_ids = set(instance.tags.values_list('id', flat=True))
        new_tags_ids = set([a.id for a in data])
        RecipeTag.objects.filter(
            recipe_id=instance.id, tag_id__in=old_tags_ids - new_tags_ids).delete()
        RecipeTag.objects.bulk_create([
            RecipeTag(recipe_id=instance.id, tag_id=tag_id) for tag_id in new_tags_ids - old_tags_ids
        ])

    @classmethod
    def update_ingredients(cls, instance, new_ingredients):
        old_ingredients_dict = {
            ri.ingredient_id: ri for ri in instance.recipe_ingredients.all()}
        new_ingredients_dict = {
            ri['id'].id: ri for ri in new_ingredients if ri['id'].id not in old_ingredients_dict}
        updated_ingredients_dict = {
            ri['id'].id: ri for ri in new_ingredients if ri['id'].id in old_ingredients_dict}
        old_ingredients_set = set(old_ingredients_dict.keys()) - \
            set(updated_ingredients_dict.keys())
        updated_ingredients_dict = dict(filter(
            lambda kv: kv[1]['amount'] != old_ingredients_dict[kv[0]].amount
            and (kv[1]['amount'] is not None or old_ingredients_dict[kv[0]].amount is not None),
            updated_ingredients_dict.items()
        ))
        RecipeIngredient.objects.filter(
            recipe_id=instance.id, ingredient_id__in=old_ingredients_set
        ).delete()
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(recipe_id=instance.id, ingredient_id=ri_id,
                             amount=ri['amount'])
            for ri_id, ri in new_ingredients_dict.items()
        ])
        RecipeIngredient.objects.bulk_update([
            RecipeIngredient(id=old_ingredients_dict[ri_id].id,
                             amount=ri['amount'])
            for ri_id, ri in updated_ingredients_dict.items()
        ], fields=['amount'])

    def split_validated_data(self, validated_data):
        return {
            key: value for key, value in validated_data.items()
            if key not in self.MANY_FIELDS
        }, {
            key: validated_data[key] for key in self.MANY_FIELDS
        }

    def update_many2us(self, instance, validated_data):
        for field, updater_name in self.MANY_FIELDS.items():
            data = validated_data.pop(field, None)
            updater = getattr(self, updater_name)
            if data is not None or not self.partial:
                updater(instance, data or [])
        return instance

    def create(self, validated_data):
        basic, many2us = self.split_validated_data(validated_data)
        return self.update_many2us(super().create(basic), many2us)

    def update(self, instance, validated_data):
        basic, many2us = self.split_validated_data(validated_data)
        return self.update_many2us(super().update(instance, basic), many2us)

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                "Обязательное поле."
            )
        unique_tags = {tag.id for tag in value}
        if len(value) != len(unique_tags):
            raise serializers.ValidationError(
                "В запросе содержатся повторяющиеся теги."
            )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                "Обязательное поле."
            )
        unique_ingredients = {ing['id'].id for ing in value}
        if len(value) != len(unique_ingredients):
            raise serializers.ValidationError(
                "В запросе содержатся повторяющиеся ингридиенты."
            )
        return value


class RecipeUpdateSerializer(RecipeCreateSerializer):
    image = Base64ImageField(required=False)


class UserWithRecipes(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipe_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipe_count', 'avatar')

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

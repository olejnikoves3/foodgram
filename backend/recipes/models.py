from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from foodgram_backend import constants


# User = get_user_model()


class User(AbstractUser):
    first_name = models.CharField('Имя',
                                  max_length=constants.FIRST_NAME_MAX_LEN)
    last_name = models.CharField('Фамилия',
                                 max_length=constants.LAST_NAME_MAX_LEN)
    avatar = models.ImageField('Аватар', upload_to='avatars/',
                               blank=True, default=None)

    class Meta(AbstractUser.Meta):
        ordering = ['username']
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class CommonInfo(models.Model):
    name = models.CharField('Название', max_length=constants.NAME_MAX_LENGTH)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(CommonInfo):
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=constants.MEASURMENT_MAX_LEN
    )

    class Meta(CommonInfo.Meta):
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(CommonInfo):
    slug = models.SlugField('Слаг', unique=True)

    class Meta(CommonInfo.Meta):
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'


class Recipe(CommonInfo):
    tags = models.ManyToManyField(Tag, verbose_name='Тег')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    text = models.TextField('Описание', help_text='Опишите действия')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления', help_text='в минутах',
        validators=[MinValueValidator(constants.MIN_COOKING_TIME),],
    )
    image = models.ImageField('Картинка', upload_to='recipes/images/',
                              null=True, default=None)

    class Meta(CommonInfo.Meta):
        default_related_name = 'recipes'
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент',
        related_name='ingredient_recipes'
    )
    amount = models.PositiveSmallIntegerField('Количество')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='unique_ingredient')
        ]


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='following', to_field='username')  # Проверить поле
    following = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='followers', to_field='username'  # Проверить поле
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'following'],
                                    name='unique_following'),
            models.CheckConstraint(check=~Q(
                user=models.F('following')), name='no self follow')
        ]

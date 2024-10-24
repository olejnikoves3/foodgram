from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from foodgram_backend import constants


User = get_user_model()


class CommonInfo(models.Model):
    name = models.CharField(
        'Название', max_length=constants.NAME_MAX_LENGTH, unique=True)

    class Meta:
        abstract = True
        ordering = ('name',)

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
    tags = models.ManyToManyField(Tag, through='RecipeTag', verbose_name='Тег')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    text = models.TextField('Описание', help_text='Опишите действия')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления', help_text='в минутах',
        validators=(MinValueValidator(constants.MIN_COOKING_TIME),
                    MaxValueValidator(constants.MAX_COOKING_TIME))
    )
    image = models.ImageField('Картинка', upload_to='recipes/images/',
                              null=True, default=None)
    pub_date = models.DateTimeField('Дата и время публикации',
                                    auto_now_add=True)

    class Meta(CommonInfo.Meta):
        ordering = ('-pub_date', 'name')
        default_related_name = 'recipes'
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
        related_name='recipe_tags'
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, verbose_name='Тег',
        related_name='tag_recipes'
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'теги рецептов'
        verbose_name_plural = 'Теги рецептов'
        constraints = [
            models.UniqueConstraint(fields=('recipe', 'tag'),
                                    name='unique_tag')
        ]

    def __str__(self):
        return f'У рецепта {self.recipe.name} тег {self.tag.name}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент',
        related_name='ingredient_recipes'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество', validators=(
            MinValueValidator(constants.MIN_AMOUNT),
            MaxValueValidator(constants.MAX_AMOUNT)
        )
    )

    class Meta:
        ordering = ('recipe', 'ingredient')
        verbose_name = 'ингридиенты в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'
        constraints = (
            models.UniqueConstraint(fields=('recipe', 'ingredient'),
                                    name='unique_ingredient'),
        )

    def __str__(self):
        return (
            f'{self.ingredient.name} в {self.recipe.name} в количестве '
            f'{self.amount} {self.ingredient.measurement_unit}'
        )


class UserReciperelations(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique recipe in %(class)s'),
        )


class Cart(UserReciperelations):

    class Meta(UserReciperelations.Meta):
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.recipe.name} в корзине у {self.user.username}'


class Favorite(UserReciperelations):

    class Meta(UserReciperelations.Meta):
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.recipe.name} в избранном у {self.user.username}'

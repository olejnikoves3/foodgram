from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from foodgram_backend import constants


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    email = models.EmailField('Электронная почта', unique=True)
    username = models.CharField(
        'Имя пользователя', unique=True,
        max_length=constants.USERNAME_MAX_LEN,
        validators=(UnicodeUsernameValidator,)
    )
    first_name = models.CharField('Имя',
                                  max_length=constants.FIRST_NAME_MAX_LEN)
    last_name = models.CharField('Фамилия',
                                 max_length=constants.LAST_NAME_MAX_LEN)
    avatar = models.ImageField('Аватар', upload_to='users/',
                               blank=True, default=None)

    class Meta(AbstractUser.Meta):
        ordering = ['username', 'last_name', 'id']
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class CommonInfo(models.Model):
    name = models.CharField(
        'Название', max_length=constants.NAME_MAX_LENGTH, unique=True)

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
    tags = models.ManyToManyField(Tag, through='RecipeTag', verbose_name='Тег')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    text = models.TextField('Описание', help_text='Опишите действия')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления', help_text='в минутах',
        validators=[MinValueValidator(constants.MIN_COOKING_TIME), ],
    )
    image = models.ImageField('Картинка', upload_to='recipes/images/',
                              null=True, default=None)
    pub_date = models.DateTimeField('Дата и время публикации',
                                    auto_now_add=True)

    class Meta(CommonInfo.Meta):
        ordering = ['-pub_date', 'name']
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
            models.UniqueConstraint(fields=['recipe', 'tag'],
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
        'Количество', validators=[
            MinValueValidator(constants.MIN_AMOUNT),
        ]
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'ингридиенты в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='unique_ingredient')
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} в {self.recipe.name} в количестве '
            f'{self.amount} {self.ingredient.measurement_unit}'
        )


class Cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='recipes_in_cart'
    )
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='in_users_carts'
                               )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique recipe in cart'),
        ]

    def __str__(self):
        return f'{self.recipe.name} в корзине у {self.user.username}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorited_recipes'
    )
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='in_favorite')

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique recipe in favorited'),
        ]

    def __str__(self):
        return f'{self.recipe.name} в избранном у {self.user.username}'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='followers')

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'following'],
                                    name='unique_following'),
            models.CheckConstraint(check=~Q(
                user=models.F('following')), name='no self follow')
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.following.username}'

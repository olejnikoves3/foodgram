from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram_backend import constants


User = get_user_model()


class CommonInfo(models.Model):
    name = models.CharField('Название', max_length=constants.NAME_MAX_LENGTH)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(CommonInfo):
    measurement_unit = models.CharField('Единица измерения')

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'Ингридиенты'


class Tag(CommonInfo):
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'


class Recipe(CommonInfo):
    tags = models.ManyToManyField(
        Tag, verbose_name='Рецепт', related_name='recipes',
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    text = models.TextField('Описание', help_text='Опишите действия')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления', validators=[
            MinValueValidator(constants.MIN_COOKING_TIME),
        ],
    )
    image = models.ImageField('Картинка', upload_to='recipes/images/',
                              null=True, default=None)

from django.db import models

from foodgram_backend import constants


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=constants.NAME_MAX_LENGTH)
    measurement_unit = models.CharField('Единица измерения')


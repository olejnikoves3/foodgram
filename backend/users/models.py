from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
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
        ordering = ('username', 'last_name', 'id')
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


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

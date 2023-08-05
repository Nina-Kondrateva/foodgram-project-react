from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from foodgram.settings import INT_150, INT_254


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        max_length=INT_150,
        verbose_name='Имя пользователя(username)',
        unique=True,
        db_index=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Имя пользователя содержит недопустимый символ'
        )]
    )
    first_name = models.CharField(
        max_length=INT_150,
        verbose_name='Имя',
        blank=True
    )
    last_name = models.CharField(
        max_length=INT_150,
        verbose_name='Фамилия',
        blank=True
    )
    email = models.EmailField(
        max_length=INT_254,
        verbose_name='email',
        unique=True
    )
    is_subscribed = models.BooleanField(default=False, )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

        constraints = [models.UniqueConstraint(
            fields=['username', 'email'],
            name='unique_user')]

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    """Подписки пользователя."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user',
        verbose_name='Пользователь'
    )
    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='subscribing'
    )

    class Meta:
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки на авторов'
        ordering = ('user',)

        constraints = [
            models.UniqueConstraint(fields=['user', 'subscribing'],
                                    name='unique_user_subscribing'),
            models.CheckConstraint(
                check=~models.Q(user=models.F('subscribing')),
                name='subscribe_to_myself')]

    def __str__(self):
        return f'{self.user} {self.subscribing}'

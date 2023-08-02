from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя(username)',
        unique=True,
        db_index=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Имя пользователя содержит недопустимый символ'
        )]
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        blank=True
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='email',
        unique=True
    )
    is_subscribed = models.BooleanField(default=False, )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username

    constraints = [models.UniqueConstraint(
                   fields=['username', 'email'],
                   name='unique_user')
                   ]


class Subscriptions(models.Model):
    """Подписки пользователя."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user'
    )
    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='subscribing'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'subscribing'],
                                    name='unique_user')
        ]

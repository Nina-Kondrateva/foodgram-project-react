from django.core.validators import (
    MaxValueValidator, MinValueValidator, RegexValidator)
from colorfield.fields import ColorField
from django.db import models

from foodgram.settings import INT_200
from users.models import User


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        max_length=INT_200,
        verbose_name='Название',
        blank=True,
        unique=True
    )
    color = ColorField(
        verbose_name='Цвет',
    )
    slug = models.SlugField(
        max_length=INT_200,
        verbose_name='slug',
        unique=True,
        blank=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Slug жанра содержит недопустимые символы'
        )])

    class Meta():
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=INT_200,
        verbose_name='Название ингредиента',
        blank=True
    )
    measurement_unit = models.CharField(
        max_length=INT_200,
        verbose_name='Единицы измерения',
        blank=True
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ('name',)

        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_ingredient')]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=INT_200,
        verbose_name='Название рецепта',
        blank=True
    )
    image = models.ImageField(
        upload_to='recipe/images/',
        verbose_name='Картинка',
        blank=True
    )
    text = models.TextField(
        verbose_name='Описание',
        blank=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        related_name='recipes',
        blank=True
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Тег',
        related_name='recipes',
        blank=True
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        blank=True,
        validators=(
            MinValueValidator(
                5, 'Время приготовления не меньше 5 минут'),
            MaxValueValidator(
                2880, 'Время приготовления не больше двух дней'))
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now=True,
        editable=False
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Дополнительная модель, связывающая рецепт и тег."""

    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)
    tags = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE)

    class Meta():
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        constraints = [models.UniqueConstraint(
            fields=['tags', 'recipes'],
            name='unique_recipe_tags'
        )]

    def __str__(self):
        return f'{self.recipes} {self.tags}'


class RecipeIngredient(models.Model):
    """Дополнительная модель, связывающая рецепт и ингредиент."""

    recipes = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE)
    ingredients = models.ForeignKey(
        Ingredient,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        blank=True,
        null=True,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(1000)
        )
    )

    class Meta():
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [models.UniqueConstraint(
            fields=['ingredients', 'recipes'],
            name='unique_recipe_ingredients'
        )]

    def __str__(self):
        return f'{self.recipes} {self.ingredients}'


class UserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user_%(class)s',
        verbose_name='Пользователь',
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_%(class)s',
        verbose_name='Рецепт',
        on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Favorite(UserRecipe):
    """Модель для избранных рецептов."""

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite'
        )]
        ordering = ('recipe',)
        verbose_name = 'Избранное'
        verbose_name_plural = "Избранное"

    def __str__(self):
        return f'{self.recipe} {self.user}'


class Shoppinglist(UserRecipe):
    """Модель для списка покупок."""

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping'
        )]
        ordering = ('recipe',)
        verbose_name = 'Список покупок'
        verbose_name_plural = "Список покупок"

    def __str__(self):
        return f'{self.recipe} {self.user}'

from django.core.validators import RegexValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        max_length=250,
        verbose_name='Название',
        blank=True,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет',
        blank=True,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        verbose_name='slug',
        unique=True,
        blank=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Slug жанра содержит недопустимые символы'
        )])

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=250,
        verbose_name='Название ингредиента',
        blank=True,
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единицы измерения',
        blank=True
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ('id',)

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
        max_length=200,
        verbose_name='Название рецепта',
        blank=True
    )
    image = models.ImageField(
        upload_to='recipes/images/',
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
        blank=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ('-id',)

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
        null=True
    )

    def __str__(self):
        return f'{self.recipes} {self.ingredients}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user_favorite',
        verbose_name='Пользователь',
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_favorite',
        verbose_name='Рецепт',
        on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite'
        )]
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = "Избранное"


class Shoppinglist(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        User,
        related_name='user_shopping',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_shopping',
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping'
        )]
        ordering = ('id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = "Список покупок"

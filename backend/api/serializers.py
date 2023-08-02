import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Shoppinglist, Tag)
from rest_framework import serializers
from users.models import Subscriptions, User


class CustomUserSerializer(UserSerializer):
    """Преобразование сериализатора djoser для получения пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, value):
        # получаем наличие/отсутсвие подписки на автора
        if self.context.get('request').user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=self.context['request'].user,
                                            subscribing=value).exists()

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if user.email != email:
                raise serializers.ValidationError(
                    'Данный username уже используется'
                )
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.username != username:
                raise serializers.ValidationError(
                    'Данный email уже используется'
                )
        return data


class RecipeLookSerializer(serializers.ModelSerializer):
    """Сериализатор для представления рецепта при создании
       и получении подписки."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsGETSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запроса подписки."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    id = serializers.ReadOnlyField(source='subscribing.id')
    email = serializers.ReadOnlyField(source='subscribing.email')
    username = serializers.ReadOnlyField(source='subscribing.username')
    first_name = serializers.ReadOnlyField(source='subscribing.first_name')
    last_name = serializers.ReadOnlyField(source='subscribing.last_name')
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, value):
        # получаем необходимый вид рецепта
        recipes = Recipe.objects.filter(author=value.subscribing.id)
        return RecipeLookSerializer(recipes, many=True).data

    def get_recipes_count(self, value):
        # подсчет колличества рецептов автора
        return Recipe.objects.filter(author=value.subscribing.id).count()

    def get_is_subscribed(self, value):
        # получаем наличие/отсутсвие подписки на автора
        return Subscriptions.objects.filter(
            user=value.user.id, subscribing=value.subscribing.id).exists()


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки пользователя."""

    class Meta:
        fields = ('user', 'subscribing')
        model = Subscriptions

    def to_representation(self, user):
        return SubscriptionsGETSerializer(
            user,
            context={'request': self.context.get('request')},
        ).data

    def validate(self, data):
        if self.context['request'].user == data['subscribing']:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя.')
        return data


class Base64ImageField(serializers.ImageField):
    """Сериализатор для изображений."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Дополнительный сериализатор для представления ингредиента в рецепте."""
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGETSerializer(serializers.ModelSerializer):
    """Сериализатор при GET запросах модели Recipe."""
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients')
    is_favorited = serializers.SerializerMethodField(read_only=True,)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_is_favorited(self, value):
        if self.context.get('request').user.is_anonymous:
            return False
        return Favorite.objects.filter(user=self.context['request'].user,
                                       recipe=value).exists()

    def get_is_in_shopping_cart(self, value):
        if self.context.get('request').user.is_anonymous:
            return False
        return Shoppinglist.objects.filter(user=self.context['request'].user,
                                           recipe=value).exists()


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Дополнительный сериализатор для ингредиента при создании рецепта."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time')

    def add_ingredient(self, recipes, ingredients):
        # создание связи инегредиент-рецепт
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            RecipeIngredient.objects.update_or_create(
                ingredients=ingredient_id, recipes=recipes, amount=amount)

    def create(self, validated_data):
        # создание рецепта
        ingredients = validated_data.pop('ingredients')
        tag = validated_data.pop('tags')
        recipes = Recipe.objects.create(**validated_data)
        self.add_ingredient(recipes, ingredients)
        recipes.tags.set(tag)
        return recipes

    def update(self, recipes, validated_data):
        # редактирование рецепта
        ingredients = validated_data.pop('ingredients')
        tag = validated_data.pop('tags')
        recipes.ingredients.clear()
        self.add_ingredient(recipes, ingredients)
        recipes.tags.set(tag)
        return super().update(recipes, validated_data)

    def to_representation(self, recipe):
        print(recipe)
        return RecipeGETSerializer(
            recipe,
            context={'request': self.context.get('request')},
        ).data

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше минуты')
        return value


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингедиента в избранное."""
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, recipe):
        return RecipeLookSerializer(
            recipe.recipe,
            context={'request': self.context.get('request')},
        ).data

    def validate(self, data):
        user = self.context['request'].user
        if Favorite.objects.filter(user=user,
                                   recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное')
        return data


class ShoppinglistSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = Shoppinglist
        fields = ('user', 'recipe')

    def to_representation(self, recipe):
        return RecipeLookSerializer(
            recipe.recipe,
            context={'request': self.context.get('request')},
        ).data

    def validate(self, data):
        user = self.context['request'].user
        if Shoppinglist.objects.filter(user=user,
                                       recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок')
        return data

from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Shoppinglist, Tag)
from users.models import Subscriptions, User


class CustomUserSerializer(UserSerializer):
    """Преобразование сериализатора djoser для получения пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, value):
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
        recipes = Recipe.objects.filter(author=value.subscribing.id)
        return RecipeLookSerializer(recipes, many=True).data

    def get_recipes_count(self, value):
        return Recipe.objects.filter(author=value.subscribing.id).count()

    def get_is_subscribed(self, value):
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


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


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
    is_favorited = serializers.SerializerMethodField()
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
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Количество должно быть больше 0.'
            )
        return value


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()
    name = serializers.RegexField(
        regex=r'^[а-яА-Яa-zA-Z0-9]+$',
        error_messages={
            'invalid': 'Для названия рецепта вы можете использовать '
                       'только буквы и цифры.'})

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time')

    def add_ingredient(self, recipes, ingredients):
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            RecipeIngredient.objects.update_or_create(
                ingredients=ingredient_id, recipes=recipes, amount=amount)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tag = validated_data.pop('tags')
        recipes = Recipe.objects.create(**validated_data)
        self.add_ingredient(recipes, ingredients)
        recipes.tags.set(tag)
        return recipes

    def update(self, recipes, validated_data):
        ingredients = validated_data.pop('ingredients')
        tag = validated_data.pop('tags')
        recipes.ingredients.clear()
        self.add_ingredient(recipes, ingredients)
        recipes.tags.set(tag)
        return super().update(recipes, validated_data)

    def to_representation(self, recipe):
        return RecipeGETSerializer(
            recipe,
            context={'request': self.context.get('request')},
        ).data

    def validate_cooking_time(self, value):
        if value < 5:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше 5 минут')
        return value

    def validate_ingredients(self, data):
        list = []
        if not data:
            raise serializers.ValidationError(
                'Необходимо выбрать хоть один ингредиент')
        for ingredient in data:
            if ingredient['id'] in list:
                raise serializers.ValidationError(
                    'Ингредиент может быть выбран только один раз.')
            else:
                list.append(ingredient['id'])
        return data

    def validate_tags(self, data):
        list = []
        if not data:
            raise serializers.ValidationError(
                'Необходимо выбрать хоть один тег')
        for tag in data:
            if tag in list:
                raise serializers.ValidationError(
                    'Тег может быть выбран только один раз.')
            else:
                list.append(tag)
        return data

    def validate_name(self, value):
        if value.isdigit():
            raise serializers.ValidationError(
                'Название не может состоять только из цифр.')
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

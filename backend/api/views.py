from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngregientFilter, RecipeFilter
from api.mixins import ListRetrieveViewSet
from api.pagination import Pagination
from api.permissions import AuthorOrReadOnly
from api.serializers import (CreateRecipeSerializer,
                             CustomUserSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeGETSerializer,
                             ShoppinglistSerializer,
                             SubscriptionsGETSerializer,
                             SubscriptionsSerializer, TagSerializer)
from api.utils import download
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Shoppinglist, Tag)
from users.models import Subscriptions, User


class CustomUserViewSet(UserViewSet):
    """Преобразование функции djoser для получения пользователя"""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)
    pagination_class = Pagination

    def get_queryset(self):
        if self.request.method == 'GET':
            return User.objects.all()

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, id=None):
        user = request.user
        subscribing = get_object_or_404(User, id=id)
        if self.request.method == 'POST':
            data = {
                'user': user.id,
                'subscribing': subscribing.id
            }
            serializer = SubscriptionsSerializer(
                data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if self.request.method == 'DELETE':
            subscription = Subscriptions.objects.filter(
                user=user, subscribing=subscribing)
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class SubcriptionsList(mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    """Получение списка подписок пользователя."""
    serializer_class = SubscriptionsGETSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination

    def get_queryset(self):
        return Subscriptions.objects.filter(user=self.request.user.id)


class IngredientViewSet(ListRetrieveViewSet):
    """Получение списка или конкретного ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngregientFilter
    search_fields = ('^name',)


class TagViewSet(ListRetrieveViewSet):
    """Получение списка или конкретного тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Обрабатывает запросы о рецептах."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeGETSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    search_fields = ('^name',)

    def get_serializer_class(self):
        if self.request.method == 'PATCH' or 'POST':
            return CreateRecipeSerializer
        return RecipeGETSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsAuthenticatedOrReadOnly(),)
        if self.request.method == 'PATCH':
            return (AuthorOrReadOnly(),)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def creation_and_deletion(self, request, models, pk):
        user = request.user.id
        recipe = get_object_or_404(Recipe, id=pk).id
        if self.request.method == 'POST':
            data = {
                'user': user,
                'recipe': recipe
            }
            serializer = self.serializer_class(
                data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if self.request.method == 'DELETE':
            shopping_list = models.objects.filter(
                user=user, recipe=recipe)
            if shopping_list.exists():
                shopping_list.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'], url_path='favorite',
            serializer_class=FavoriteSerializer)
    def favorite(self, request, pk=None):
        models = Favorite
        return self.creation_and_deletion(request, models, pk)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart',
            serializer_class=ShoppinglistSerializer)
    def shopping_cart(self, request, pk=None):
        models = Shoppinglist
        return self.creation_and_deletion(request, models, pk)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients_list = RecipeIngredient.objects.filter(
            recipes__recipe_shoppinglist__user=request.user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return download(ingredients_list)


class FavoritesList(mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """Получение списка избранных рецептов."""
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user.id)

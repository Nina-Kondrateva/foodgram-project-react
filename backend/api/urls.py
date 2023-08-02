from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CustomUserViewSet, FavoritesList, IngredientViewSet,
                       RecipeViewSet, SubcriptionsList, TagViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet)
router.register('users/subscriptions', SubcriptionsList,
                basename='users/subscriptions')
router.register('users', CustomUserViewSet)
router.register('favorites', FavoritesList, basename='favorites')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

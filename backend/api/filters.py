import django_filters

from recipes.models import Ingredient, Recipe


class IngregientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.CharFilter(
        method='get_is_favorited'
    )
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr="iexact"
    )
    is_in_shopping_cart = django_filters.CharFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'tags',
            'author',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(recipe_favorite__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(recipe_shoppinglist__user=self.request.user)

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
    is_favorited = django_filters.BooleanFilter(
        method='get_favorite',
        label='Favorited'
    )
    tags = django_filters.CharFilter(
        field_name='tags__slug',
        lookup_expr="iexact",
        label='Tags'
    )

    is_in_shopping_cart = django_filters.BooleanFilter(
        method='get_shopping',
        label='Is in shopping list',
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'tags',
            'author',
            'is_in_shopping_cart',
        )

    def get_favorite(self, queryset, name, item_value):
        if self.request.user.is_authenticated and item_value:
            return queryset.filter(recipe_Favorite__user=self.request.user)

    def get_shopping(self, queryset, name, item_value):
        if self.request.user.is_authenticated and item_value:
            return queryset.filter(recipe_shoppinglist__user=self.request.user)

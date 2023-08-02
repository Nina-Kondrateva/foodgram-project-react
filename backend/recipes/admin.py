from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     Shoppinglist, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('slug',)
    list_filter = ('slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'text', 'is_favorited')
    search_fields = ('name',)
    list_filter = ('name', 'author')
    inlines = (RecipeIngredientInline, RecipeTagInline)

    def is_favorited(self, obj):
        return obj.recipe_favorite.all().count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(Shoppinglist)
class ShoppinglistAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')

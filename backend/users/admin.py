from django.contrib import admin

from users.models import Subscriptions, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name',
                    'email', 'recipes', 'subscriptions')
    search_fields = ('username',)
    list_filter = ('first_name', 'email')

    def recipes(self, obj):
        return obj.recipes.all().count()

    def subscriptions(self, obj):
        return obj.subscribing.all().count()


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscribing')

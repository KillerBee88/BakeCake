from django.contrib import admin
from .models import Cake, Order, Client, Levels, Shape, Topping, Berries, Decor

class CakeParamAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'is_available']
    list_filter = ['is_available']
    search_fields = ['title']
    ordering = ['title']
from bot.models import (Client, Order, Cake, Level, Shape, Topping, Berries,
                        Decor, Complaint, PromoCode, Link)


class ClientOrdersInline(admin.TabularInline):
    model = Order
    fields = ['id', 'cake']

@admin.register(Shape)
class ShapeAdmin(CakeParamAdmin):
    pass

@admin.register(Topping)
class ToppingAdmin(CakeParamAdmin):
    pass

@admin.register(Berries)
class BerriesAdmin(CakeParamAdmin):
    pass

@admin.register(Decor)
class DecorAdmin(CakeParamAdmin):
    pass


@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_original', 'get_price']
    list_filter = ['is_original', 'levels__title', 'shape__title', 'topping__title', 'berries__title']
    search_fields = ['title', 'description']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'cake', 'client', 'order_dt', 'delivery_dt', 'promo_code', 'get_price']
    list_filter = ['cake', 'client', 'promo_code']
    search_fields = ['id', 'cake__title', 'client__name']
    date_hierarchy = 'order_dt'
    ordering = ['-order_dt']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'id_telegram', 'address', 'consent_to_pdProc']
    list_filter = ['consent_to_pdProc']
    search_fields = ['name', 'id_telegram']
    list_display = ['name', 'id_telegram', 'consent_to_pdProc']
    inlines = [ClientOrdersInline]


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'shorten_link', 'place_of_use', 'clicks_count')

    def clicks_count(self, instance):
        return instance.clicks


admin.site.register(Order)
admin.site.register(Cake)
admin.site.register(Level)
admin.site.register(Shape)
admin.site.register(Topping)
admin.site.register(Berries)
admin.site.register(Decor)
admin.site.register(Complaint)
admin.site.register(PromoCode)





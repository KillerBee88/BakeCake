from django.contrib import admin
from bot.models import Client, Order, Cake, Level, Shape, Topping, Berries, Decor


class ClientOrdersInline(admin.TabularInline):
    model = Order
    fields = ['id', 'cake']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'id_telegram', 'consent_to_pdProc']
    inlines = [ClientOrdersInline]


admin.site.register(Order)
admin.site.register(Cake)
admin.site.register(Level)
admin.site.register(Shape)
admin.site.register(Topping)
admin.site.register(Berries)
admin.site.register(Decor)

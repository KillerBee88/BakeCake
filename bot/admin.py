from django.contrib import admin
from bot.models import Client, Order, Cake, Levels, Shape


class ClientOrdersInline(admin.TabularInline):
    model = Order
    fields = ['id', 'cake']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'id_telegram', 'consent_to_pdProc']
    inlines = [ClientOrdersInline]


admin.site.register(Order)
admin.site.register(Cake)
admin.site.register(Levels)
admin.site.register(Shape)


from django.contrib import admin
from .models import Inventory

# Register your models here.
class InventoryAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(Inventory, InventoryAdmin)
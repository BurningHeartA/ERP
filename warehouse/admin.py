from django.contrib import admin
from .models import Material, InventoryRecord


@admin.register(InventoryRecord)
class InventoryRecordAdmin(admin.ModelAdmin):
    list_display = ('material', 'movement_type', 'quantity', 'date', 'order')
    list_filter = ('movement_type', 'date')
from django.contrib import admin
from .models import Order, Request


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'desired_deadline')
    list_filter = ('status',)
    search_fields = ('description', 'product_name', 'customer__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product', 'quantity', 'status', 'accepted_date', 'planned_completion_date')
    list_filter = ('status', 'material_source')
    search_fields = ('customer__name', 'product__name')


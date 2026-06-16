from django.contrib import admin
from .models import Operation

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'operation_type', 'employee', 'start_time', 'end_time', 'order')
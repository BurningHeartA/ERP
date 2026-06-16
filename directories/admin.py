from django.contrib import admin, messages

# Register your models here.
from .models import (
    Position, WorkSchedule, Competence,
    WorkCategory, OperationType, ExpenseCategory,
    Product, Equipment, Material
)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'coefficient')

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except ValueError as e:
            messages.error(request, str(e))

@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'coefficient')

@admin.register(Competence)
class CompetenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'coefficient')

@admin.register(WorkCategory)
class WorkCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(OperationType)
class OperationTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'processing_type', 'status', 'purchase_date')
    list_filter = ('status', 'processing_type')


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'material_type', 'unit_price')
    list_filter = ('material_type',)

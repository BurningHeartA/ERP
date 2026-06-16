from django.contrib import admin
from .models import Income, Expense


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'payment_type', 'date')
    list_filter = ('payment_type', 'date')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('expense_category', 'amount', 'date', 'order')
    list_filter = ('expense_category', 'date')
from rest_framework import serializers
from finance.models import Income, Expense


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    expense_category_name = serializers.CharField(source='expense_category.name', read_only=True)

    class Meta:
        model = Expense
        fields = '__all__'
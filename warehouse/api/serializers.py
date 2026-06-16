from rest_framework import serializers
from warehouse.models import InventoryRecord

class InventoryRecordSerializer(serializers.ModelSerializer):
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    material_name = serializers.CharField(source='material.name', read_only=True)

    class Meta:
        model = InventoryRecord
        fields = '__all__'
from rest_framework import serializers
from operations.models import Operation

class OperationSerializer(serializers.ModelSerializer):
    duration_hours = serializers.FloatField(read_only=True)
    energy_consumption = serializers.FloatField(read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    operation_type_name = serializers.CharField(source='operation_type.name', read_only=True)

    class Meta:
        model = Operation
        fields = '__all__'
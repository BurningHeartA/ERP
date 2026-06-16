from rest_framework import serializers
from worklog.models import WorkLog, WorkEntry


class WorkEntrySerializer(serializers.ModelSerializer):
    duration_hours = serializers.FloatField(read_only=True)
    work_category_name = serializers.CharField(source='work_category.name', read_only=True)

    class Meta:
        model = WorkEntry
        fields = ['id', 'work_log', 'order', 'work_category', 'start_time', 'end_time',
                  'duration_hours', 'work_category_name']
        extra_kwargs = {'work_log': {'required': False}}


class WorkLogSerializer(serializers.ModelSerializer):
    entries = WorkEntrySerializer(many=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = WorkLog
        fields = '__all__'

    def create(self, validated_data):
        entries_data = validated_data.pop('entries')
        work_log = WorkLog.objects.create(**validated_data)
        for entry_data in entries_data:
            WorkEntry.objects.create(work_log=work_log, **entry_data)
        return work_log

    def update(self, instance, validated_data):
        entries_data = validated_data.pop('entries', None)
        instance = super().update(instance, validated_data)
        if entries_data is not None:
            instance.entries.all().delete()
            for entry_data in entries_data:
                WorkEntry.objects.create(work_log=instance, **entry_data)
        return instance
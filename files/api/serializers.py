from rest_framework import serializers
from files.models import File


class FileSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)

    class Meta:
        model = File
        fields = '__all__'
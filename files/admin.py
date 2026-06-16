from django.contrib import admin
from .models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'file_category', 'content_type', 'object_id', 'uploaded_by', 'uploaded_at')
    list_filter = ('file_category', 'uploaded_at')
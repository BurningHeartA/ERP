from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class File(models.Model):
    class FileCategory(models.TextChoices):
        DRAWING = 'drawing', 'Чертёж'
        CONTRACT = 'contract', 'Договор'
        MODEL_3D = 'model', '3D-модель'
        PROGRAM = 'program', 'Управляющая программа'
        REPORT = 'report', 'Отчёт'
        PAYMENT = 'payment', 'Платёжный документ'
        HR = 'hr', 'Кадровый документ'
        EQUIPMENT_DOC = 'equipment', 'Паспорт оборудования'
        OTHER = 'other', 'Прочее'

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='Тип сущности')
    object_id = models.PositiveIntegerField(verbose_name='ID сущности')
    content_object = GenericForeignKey('content_type', 'object_id')
    file = models.FileField(upload_to='uploads/%Y/%m/', verbose_name='Файл')
    original_name = models.CharField(max_length=255, verbose_name='Оригинальное имя')
    file_category = models.CharField(max_length=50, choices=FileCategory.choices, verbose_name='Категория')
    description = models.CharField(max_length=255, blank=True, verbose_name='Описание')
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='uploaded_files', verbose_name='Загрузил')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return self.original_name
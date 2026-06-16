from django.db import models

# Create your models here.
class Position(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Наименование')
    coefficient = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Тарифный коэффициент')

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def save(self, *args, **kwargs):
        if self.name == 'Директор':
            # Проверяем, есть ли уже Директор (кроме текущей записи)
            existing = Position.objects.filter(name='Директор')
            if self.pk is not None:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValueError('Нельзя создать вторую должность Директора')
        # Если это существующая должность и её имя было "Директор" — не даём переименовать
        if self.pk is not None:
            old = Position.objects.get(pk=self.pk)
            if old.name == 'Директор' and self.name != 'Директор':
                raise ValueError('Нельзя переименовать должность Директора')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.name == 'Директор':
            raise ValueError('Нельзя удалить должность Директора')
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name
    

class WorkSchedule(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Наименование')
    coefficient = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='Коэффициент')

    class Meta:
        verbose_name = 'График работы'
        verbose_name_plural = 'Графики работы'

    def __str__(self):
        return self.name


class Competence(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Наименование')
    coefficient = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='Коэффициент премии')

    class Meta:
        verbose_name = 'Компетенция'
        verbose_name_plural = 'Компетенции'

    def __str__(self):
        return self.name


class WorkCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Наименование')

    class Meta:
        verbose_name = 'Категория работ'
        verbose_name_plural = 'Категории работ'

    def __str__(self):
        return self.name


class OperationType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Наименование')

    class Meta:
        verbose_name = 'Тип операции'
        verbose_name_plural = 'Типы операций'

    def __str__(self):
        return self.name


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Наименование')

    class Meta:
        verbose_name = 'Категория расходов'
        verbose_name_plural = 'Категории расходов'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Наименование')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Изделие'
        verbose_name_plural = 'Изделия'

    def __str__(self):
        return self.name
    
class Equipment(models.Model):
    class ProcessingType(models.TextChoices):
        MILLING = 'milling', 'Фрезерная'
        TURNING = 'turning', 'Токарная'
        DRILLING = 'drilling', 'Сверление'
        GRINDING = 'grinding', 'Шлифование'
        EROSION = 'erosion', 'Электроэрозия'
        WELDING = 'welding', 'Сварка'

    class Status(models.TextChoices):
        OPERATIONAL = 'operational', 'В работе'
        MAINTENANCE = 'maintenance', 'На обслуживании'
        DECOMMISSIONED = 'decommissioned', 'Списано'

    name = models.CharField(max_length=255, unique=True, verbose_name='Наименование')
    processing_type = models.CharField(max_length=50, choices=ProcessingType.choices, verbose_name='Тип обработки')
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Стоимость приобретения')
    purchase_date = models.DateField(verbose_name='Дата приобретения')
    power_rating = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Установочная мощность (кВт)')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPERATIONAL, verbose_name='Статус')
    notes = models.TextField(blank=True, verbose_name='Примечания')

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'

    def __str__(self):
        return self.name


class Material(models.Model):
    class MaterialType(models.TextChoices):
        RAW = 'raw', 'Сырьё'
        CONSUMABLE = 'consumable', 'Расходный материал'

    name = models.CharField(max_length=255, unique=True, verbose_name='Наименование')
    material_type = models.CharField(max_length=50, choices=MaterialType.choices, verbose_name='Тип материала')
    material_kind = models.CharField(max_length=255, blank=True, verbose_name='Вид материала')
    stock_form = models.CharField(max_length=255, blank=True, verbose_name='Тип проката')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за единицу')

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'

    def __str__(self):
        return self.name
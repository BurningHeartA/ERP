from django.db import models
from orders.models import Order
from directories.models import Material


class InventoryRecord(models.Model):
    class MovementType(models.TextChoices):
        RECEIPT = 'receipt', 'Поступление'
        ISSUE = 'issue', 'Выдача'

    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='inventory_records', verbose_name='Материал')
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=True, related_name='inventory_records', verbose_name='Заказ')
    movement_type = models.CharField(max_length=20, choices=MovementType.choices, verbose_name='Тип движения')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Количество')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за единицу')
    date = models.DateField(verbose_name='Дата операции')

    class Meta:
        verbose_name = 'Запись складского учёта'
        verbose_name_plural = 'Записи складского учёта'

    def __str__(self):
        return f'{self.get_movement_type_display()}: {self.material.name} ({self.quantity})'

    @property
    def total_cost(self):
        return self.quantity * self.unit_price
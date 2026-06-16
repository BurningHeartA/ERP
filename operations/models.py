from django.db import models
from employees.models import Employee
from orders.models import Order
from directories.models import Equipment, OperationType


class Operation(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, related_name='operations', verbose_name='Оборудование')
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=True, related_name='operations', verbose_name='Заказ')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='operations', verbose_name='Сотрудник')
    operation_type = models.ForeignKey(OperationType, on_delete=models.PROTECT, related_name='operations', verbose_name='Тип операции')
    start_time = models.DateTimeField(verbose_name='Время начала')
    end_time = models.DateTimeField(verbose_name='Время окончания')
    meter_reading = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Показания счётчика')

    class Meta:
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'

    def __str__(self):
        return f'{self.equipment.name} — {self.operation_type.name}'

    @property
    def duration_hours(self):
        delta = self.end_time - self.start_time
        return round(delta.total_seconds() / 3600, 1)

    @property
    def energy_consumption(self):
        if self.equipment.power_rating:
            return round(float(self.equipment.power_rating) * self.duration_hours, 2)
        return None
from django.db import models
from employees.models import Employee
from orders.models import Order
from directories.models import WorkCategory


class WorkLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='work_logs', verbose_name='Сотрудник')
    shift_date = models.DateField(verbose_name='Дата смены')
    efficiency_score = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='Оценка эффективности')
    comment = models.TextField(blank=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Табель смены'
        verbose_name_plural = 'Табели смен'
        unique_together = ['employee', 'shift_date']

    def __str__(self):
        return f'{self.employee.full_name} — {self.shift_date}'


class WorkEntry(models.Model):
    work_log = models.ForeignKey(WorkLog, on_delete=models.CASCADE, related_name='entries', verbose_name='Табель')
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=True, related_name='work_entries', verbose_name='Заказ')
    work_category = models.ForeignKey(WorkCategory, on_delete=models.PROTECT, related_name='work_entries', verbose_name='Категория работ')
    start_time = models.DateTimeField(verbose_name='Время начала')
    end_time = models.DateTimeField(verbose_name='Время окончания')

    class Meta:
        verbose_name = 'Запись работы'
        verbose_name_plural = 'Записи работ'

    def __str__(self):
        return f'{self.work_category.name} — {self.start_time:%H:%M}–{self.end_time:%H:%M}'

    @property
    def duration_hours(self):
        delta = self.end_time - self.start_time
        return round(delta.total_seconds() / 3600, 1)
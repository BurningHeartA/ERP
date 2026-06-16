from django.db import models
from orders.models import Order
from directories.models import ExpenseCategory


class Income(models.Model):
    class PaymentType(models.TextChoices):
        PREPAYMENT = 'prepayment', 'Предоплата'
        FINAL_PAYMENT = 'final_payment', 'Итоговая оплата'
        OTHER = 'other', 'Прочее'

    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=True, related_name='incomes', verbose_name='Заказ')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Сумма')
    payment_type = models.CharField(max_length=20, choices=PaymentType.choices, verbose_name='Тип платежа')
    date = models.DateField(verbose_name='Дата')
    description = models.CharField(max_length=255, blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Доход'
        verbose_name_plural = 'Доходы'

    def __str__(self):
        return f'Доход {self.amount} руб. от {self.date}'


class Expense(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=True, related_name='expenses', verbose_name='Заказ')
    expense_category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses', verbose_name='Категория расходов')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Сумма')
    date = models.DateField(verbose_name='Дата')
    description = models.CharField(max_length=255, blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Расход'
        verbose_name_plural = 'Расходы'

    def __str__(self):
        return f'Расход {self.amount} руб. от {self.date}'
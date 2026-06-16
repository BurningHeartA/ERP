from django.db import models
from clients.models import Customer
from directories.models import Product


class Request(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новая'
        IN_REVIEW = 'in_review', 'На согласовании'
        APPROVED = 'approved', 'Согласована'
        REJECTED = 'rejected', 'Отклонена'
        DELETED = 'deleted', 'Удалена'

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='requests', verbose_name='Клиент')
    description = models.TextField(verbose_name='Описание')
    product_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Наименование изделия')
    quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name='Количество')
    desired_deadline = models.DateField(null=True, blank=True, verbose_name='Желаемый срок')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, verbose_name='Статус')

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f'Заявка №{self.id} от {self.customer.name}'


class Order(models.Model):
    class MaterialSource(models.TextChoices):
        CUSTOMER = 'customer', 'Заказчик'
        WASTE = 'waste', 'Отходы'
        PURCHASE = 'purchase', 'Закупка'

    class Status(models.TextChoices):
        PENDING = 'pending', 'В очереди'
        IN_PROGRESS = 'in_progress', 'В производстве'
        COMPLETED = 'completed', 'Завершён'
        CLOSED = 'closed', 'Закрыт'
        CANCELLED = 'cancelled', 'Отменён'

    request = models.ForeignKey(Request, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name='Заявка')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders', verbose_name='Клиент')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders', verbose_name='Изделие')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость за единицу')
    material_source = models.CharField(max_length=50, choices=MaterialSource.choices, verbose_name='Источник материала')
    accepted_date = models.DateField(verbose_name='Дата принятия')
    planned_completion_date = models.DateField(verbose_name='Плановая дата сдачи')
    launch_date = models.DateField(null=True, blank=True, verbose_name='Дата запуска')
    completion_date = models.DateField(null=True, blank=True, verbose_name='Дата завершения')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='Статус')
    notes = models.TextField(blank=True, verbose_name='Примечания')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ №{self.id} — {self.product.name}'

    @property
    def total_price(self):
        return self.quantity * self.price_per_unit
    

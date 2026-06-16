from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    class Source(models.TextChoices):
        PERSONAL = 'personal_referral', 'Личное знакомство'
        FARPOST = 'farpost', 'Farpost'
        AVITO = 'avito', 'Avito'
        PARTNER = 'partner_company', 'Компания-партнёр'
        WEBSITE = 'company_website', 'Сайт компании'

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer', verbose_name='Пользователь')
    name = models.CharField(max_length=255, verbose_name='Наименование')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    source = models.CharField(max_length=50, choices=Source.choices, verbose_name='Источник привлечения')

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.name
from django.contrib.auth.models import User
from django.db import models
from directories.models import Position, WorkSchedule, Competence


class Employee(models.Model):
    class Status(models.TextChoices):
        HIRED = 'hired', 'Нанят'
        DISMISSED = 'dismissed', 'Уволен'

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee', verbose_name='Пользователь')
    position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name='employees', verbose_name='Должность')
    work_schedule = models.ForeignKey(WorkSchedule, on_delete=models.PROTECT, related_name='employees', verbose_name='График работы')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    middle_name = models.CharField(max_length=100, blank=True, verbose_name='Отчество')
    birth_date = models.DateField(verbose_name='Дата рождения')
    passport_number = models.CharField(max_length=10, unique=True, verbose_name='Номер паспорта')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    contract_number = models.CharField(max_length=8, unique=True, verbose_name='Номер трудового договора')
    hire_date = models.DateField(verbose_name='Дата приёма')
    dismissal_date = models.DateField(null=True, blank=True, verbose_name='Дата увольнения')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.HIRED, verbose_name='Статус')

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name or ""}'

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(p for p in parts if p)

    @property
    def tariff_rate(self):
        competence_sum = sum(
            ec.competence.coefficient for ec in self.competence_links.all()
        )
        return self.position.coefficient * self.work_schedule.coefficient * (1 + competence_sum)


class EmployeeCompetence(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='competence_links', verbose_name='Сотрудник')
    competence = models.ForeignKey(Competence, on_delete=models.PROTECT, related_name='employee_links', verbose_name='Компетенция')

    class Meta:
        verbose_name = 'Компетенция сотрудника'
        verbose_name_plural = 'Компетенции сотрудников'
        unique_together = ['employee', 'competence']

    def __str__(self):
        return f'{self.employee.full_name} — {self.competence.name}'
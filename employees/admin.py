from django.contrib import admin
from .models import Employee, EmployeeCompetence


class EmployeeCompetenceInline(admin.TabularInline):
    model = EmployeeCompetence
    extra = 1
    verbose_name = 'Компетенция'
    verbose_name_plural = 'Компетенции'


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'position', 'status', 'hire_date')
    list_filter = ('status', 'position')
    search_fields = ('last_name', 'first_name')
    inlines = [EmployeeCompetenceInline]


@admin.register(EmployeeCompetence)
class EmployeeCompetenceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'competence')
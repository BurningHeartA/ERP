from django.contrib import admin
from .models import WorkLog, WorkEntry


class WorkEntryInline(admin.TabularInline):
    model = WorkEntry
    extra = 1
    verbose_name = 'Работа'
    verbose_name_plural = 'Работы в смену'


@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ('employee', 'shift_date', 'efficiency_score')
    list_filter = ('shift_date', 'employee')
    inlines = [WorkEntryInline]


@admin.register(WorkEntry)
class WorkEntryAdmin(admin.ModelAdmin):
    list_display = ('work_log', 'work_category', 'order', 'start_time', 'end_time') 
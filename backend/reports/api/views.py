from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.db.models import Sum, Count
from users.permissions import IsDirector, IsEmployee
from clients.models import Customer
from orders.models import Order
from employees.models import Employee
from worklog.models import WorkEntry, WorkLog
from operations.models import Operation
from warehouse.models import InventoryRecord
from finance.models import Income, Expense
from directories.models import WorkCategory, Equipment, Material
from django.db.models import Sum, Count, F, Q


class BaseReportView(views.APIView):
    """Базовый класс для отчётов. По умолчанию — только сотрудникам и директору."""
    permission_classes = [permissions.IsAuthenticated, IsEmployee]


# class CustomerChannelReportView(BaseReportView):
#     """Отчёт об эффективности каналов привлечения клиентов."""
#     def get(self, request):
#         data = Customer.objects.values('source').annotate(
#             client_count=Count('id'),
#             order_count=Count('orders'),
#         )
#         return Response(data)

class CustomerChannelReportView(BaseReportView):
    """Отчёт об эффективности каналов привлечения клиентов."""
    def get(self, request):
        from django.db.models import Sum, Count, F, Q
        from orders.models import Order

        # Общая сумма всех заказов для процентов
        total_sum = Order.objects.aggregate(total=Sum(F('quantity') * F('price_per_unit')))['total'] or 0
        total_orders = Order.objects.count()

        # Группировка по источникам клиентов
        data = Customer.objects.values('source').annotate(
            client_count=Count('id', distinct=True),
            order_count=Count('orders', distinct=True),
            total_sum=Sum(F('orders__quantity') * F('orders__price_per_unit')),
        )

        result = []
        for item in data:
            order_count = item['order_count'] or 0
            total_sum_item = item['total_sum'] or 0
            result.append({
                'source': item['source'],
                'client_count': item['client_count'],
                'order_count': order_count,
                'total_sum': float(total_sum_item),
                'order_percent': round(order_count / total_orders * 100, 1) if total_orders > 0 else 0,
                'sum_percent': round(float(total_sum_item) / float(total_sum) * 100, 1) if total_sum > 0 else 0,
            })

        return Response(result)


class OrderProfitabilityReportView(BaseReportView):
    """Отчёт о рентабельности заказа."""
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=404)

        incomes = Income.objects.filter(order=order).aggregate(sum=Sum('amount'))['sum'] or 0
        expenses = Expense.objects.filter(order=order).aggregate(sum=Sum('amount'))['sum'] or 0

        return Response({
            'order_id': order.id,
            'total_price': order.total_price,
            'incomes': incomes,
            'expenses': expenses,
            'profit': incomes - expenses,
        })


class SalaryReportView(BaseReportView):
    """Отчёт о заработной плате сотрудника за период."""
    def get(self, request):
        employee_id = request.query_params.get('employee_id')
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        if not all([employee_id, year, month]):
            return Response({'error': 'Укажите employee_id, year, month'}, status=400)

        employee_id = int(employee_id)
        year = int(year)
        month = int(month)

        # Сотрудник может смотреть только свою зарплату
        user = request.user
        is_director = hasattr(user, 'profile') and user.profile.is_director
        if not is_director:
            if hasattr(user, 'employee') and str(user.employee.id) != str(employee_id):
                return Response({'error': 'Можно смотреть только свою зарплату'}, status=403)

        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Сотрудник не найден'}, status=404)

        entries = WorkEntry.objects.filter(
            work_log__employee=employee,
            start_time__year=year,
            start_time__month=month
        )

        total_hours = sum(e.duration_hours for e in entries)
        tariff = employee.tariff_rate
        salary = round(float(tariff) * total_hours, 2)

        return Response({
            'employee': employee.full_name,
            'period': f'{month:02d}.{year}',
            'total_hours': round(total_hours, 1),
            'salary': salary,
        })


class WorkCategoriesReportView(BaseReportView):
    """Отчёт о распределении работ по категориям."""
    def get(self, request):
        data = WorkCategory.objects.annotate(
            entry_count=Count('work_entries')
        )
        return Response([{'name': c.name, 'entries': c.entry_count} for c in data])


class EquipmentLoadReportView(BaseReportView):
    """Отчёт о загрузке оборудования."""
    def get(self, request):
        data = Equipment.objects.filter(status='operational').annotate(
            operation_count=Count('operations')
        )
        return Response([{'name': e.name, 'operations': e.operation_count} for e in data])


class WarehouseBalanceReportView(BaseReportView):
    """Отчёт об остатках на складе."""
    def get(self, request):
        data = []
        for m in Material.objects.all():
            received = InventoryRecord.objects.filter(
                material=m, movement_type='receipt'
            ).aggregate(sum=Sum('quantity'))['sum'] or 0
            issued = InventoryRecord.objects.filter(
                material=m, movement_type='issue'
            ).aggregate(sum=Sum('quantity'))['sum'] or 0
            balance = received - issued
            if balance > 0:
                data.append({
                    'material': m.name,
                    'balance': balance,
                    'total_cost': round(float(balance) * float(m.unit_price), 2),
                })
        return Response(data)


class ProfitLossReportView(BaseReportView):
    """Отчёт о прибылях и убытках за период."""
    def get(self, request):
        total_income = Income.objects.aggregate(sum=Sum('amount'))['sum'] or 0
        total_expense = Expense.objects.aggregate(sum=Sum('amount'))['sum'] or 0
        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'profit': total_income - total_expense,
        })


class CustomerProfitabilityReportView(BaseReportView):
    """Отчёт о рентабельности клиента."""
    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response({'error': 'Укажите customer_id'}, status=400)
        # Упрощённый вариант
        return Response({'customer_id': customer_id, 'profit': 0})


class EmployeeLaborReportView(BaseReportView):
    """Отчёт о трудозатратах по сотрудникам за период."""
    def get(self, request):
        data = Employee.objects.filter(status='hired').annotate(
            total_entries=Count('work_logs__entries')
        )
        return Response([{'name': e.full_name, 'entries': e.total_entries} for e in data])


class OrderInflowReportView(BaseReportView):
    """Отчёт о поступлении заказов за период."""
    def get(self, request):
        data = Order.objects.values('status').annotate(
            count=Count('id'),
        )
        return Response(data)


class WorkDistributionByOrdersReportView(BaseReportView):
    """Отчёт о распределении работ по заказам."""
    def get(self, request):
        data = Order.objects.annotate(
            entry_count=Count('work_entries')
        )
        return Response([{'order_id': o.id, 'entries': o.entry_count} for o in data])


class WorkDistributionByCustomersReportView(BaseReportView):
    """Отчёт о распределении работ по клиентам."""
    def get(self, request):
        data = Customer.objects.annotate(
            entry_count=Count('orders__work_entries')
        )
        return Response([{'customer': c.name, 'entries': c.entry_count} for c in data])
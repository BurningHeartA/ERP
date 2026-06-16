from django.urls import path
from .views import (
    CustomerChannelReportView,
    OrderProfitabilityReportView,
    SalaryReportView,
    WorkCategoriesReportView,
    EquipmentLoadReportView,
    WarehouseBalanceReportView,
    ProfitLossReportView,
    CustomerProfitabilityReportView,
    EmployeeLaborReportView,
    OrderInflowReportView,
    WorkDistributionByOrdersReportView,
    WorkDistributionByCustomersReportView,
)

urlpatterns = [
    path('reports/customer-channels/', CustomerChannelReportView.as_view()),
    path('reports/order-profitability/<int:order_id>/', OrderProfitabilityReportView.as_view()),
    path('reports/salary/', SalaryReportView.as_view()),
    path('reports/work-categories/', WorkCategoriesReportView.as_view()),
    path('reports/equipment-load/', EquipmentLoadReportView.as_view()),
    path('reports/warehouse-balance/', WarehouseBalanceReportView.as_view()),
    path('reports/profit-loss/', ProfitLossReportView.as_view()),
    path('reports/customer-profitability/', CustomerProfitabilityReportView.as_view()),
    path('reports/employee-labor/', EmployeeLaborReportView.as_view()),
    path('reports/order-inflow/', OrderInflowReportView.as_view()),
    path('reports/work-distribution-orders/', WorkDistributionByOrdersReportView.as_view()),
    path('reports/work-distribution-customers/', WorkDistributionByCustomersReportView.as_view()),
]
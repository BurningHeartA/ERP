from rest_framework.routers import DefaultRouter
from .views import IncomeViewSet, ExpenseViewSet

router = DefaultRouter()
router.register(r'incomes', IncomeViewSet)
router.register(r'expenses', ExpenseViewSet)

urlpatterns = router.urls
from rest_framework.routers import DefaultRouter
from .views import (
    PositionViewSet, WorkScheduleViewSet, CompetenceViewSet,
    WorkCategoryViewSet, OperationTypeViewSet, ExpenseCategoryViewSet,
    ProductViewSet, EquipmentViewSet, MaterialViewSet
)

router = DefaultRouter()
router.register(r'positions', PositionViewSet, basename='position')
router.register(r'work-schedules', WorkScheduleViewSet, basename='workschedule')
router.register(r'competences', CompetenceViewSet, basename='competence')
router.register(r'work-categories', WorkCategoryViewSet, basename='workcategory')
router.register(r'operation-types', OperationTypeViewSet, basename='operationtype')
router.register(r'expense-categories', ExpenseCategoryViewSet, basename='expensecategory')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'materials', MaterialViewSet, basename='material')

urlpatterns = router.urls
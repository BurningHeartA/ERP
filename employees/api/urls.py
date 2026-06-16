from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, EmployeeCompetenceViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'employee-competences', EmployeeCompetenceViewSet)

urlpatterns = router.urls
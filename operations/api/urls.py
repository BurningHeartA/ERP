from rest_framework.routers import DefaultRouter
from .views import OperationViewSet

router = DefaultRouter()
router.register(r'operations', OperationViewSet)

urlpatterns = router.urls
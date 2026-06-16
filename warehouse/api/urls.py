from rest_framework.routers import DefaultRouter
from .views import InventoryRecordViewSet

router = DefaultRouter()
router.register(r'inventory-records', InventoryRecordViewSet)

urlpatterns = router.urls
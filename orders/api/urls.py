from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, RequestViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'requests', RequestViewSet, basename='request')

urlpatterns = router.urls
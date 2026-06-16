from rest_framework.routers import DefaultRouter
from .views import WorkLogViewSet, WorkEntryViewSet

router = DefaultRouter()
router.register(r'work-logs', WorkLogViewSet)
router.register(r'work-entries', WorkEntryViewSet)

urlpatterns = router.urls
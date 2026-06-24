from django.urls import path
from .views import RegisterView

from rest_framework.routers import DefaultRouter
from .views import UserViewSet

urlpatterns = [
    path('register/', RegisterView.as_view()),
]



router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
urlpatterns = router.urls
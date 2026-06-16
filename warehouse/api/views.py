from rest_framework import viewsets, permissions
from users.permissions import IsDirector
from warehouse.models import InventoryRecord
from .serializers import InventoryRecordSerializer


class InventoryRecordViewSet(viewsets.ModelViewSet):
    queryset = InventoryRecord.objects.all()
    serializer_class = InventoryRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirector]
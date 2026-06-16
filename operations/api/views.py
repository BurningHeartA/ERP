from rest_framework import viewsets, permissions
from users.permissions import IsDirector
from operations.models import Operation
from .serializers import OperationSerializer


class OperationViewSet(viewsets.ModelViewSet):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirector]
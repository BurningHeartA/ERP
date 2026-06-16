from rest_framework import viewsets, permissions
from users.permissions import IsDirector
from worklog.models import WorkLog, WorkEntry
from .serializers import WorkLogSerializer, WorkEntrySerializer


class WorkLogViewSet(viewsets.ModelViewSet):
    queryset = WorkLog.objects.all()
    serializer_class = WorkLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirector]


class WorkEntryViewSet(viewsets.ModelViewSet):
    queryset = WorkEntry.objects.all()
    serializer_class = WorkEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsDirector]
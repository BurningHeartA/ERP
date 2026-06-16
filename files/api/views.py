from rest_framework import viewsets, permissions
from files.models import File
from .serializers import FileSerializer
from users.permissions import IsDirector


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirector]
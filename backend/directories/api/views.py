from rest_framework import viewsets, permissions
from directories.models import Position
from .serializers import PositionSerializer
from users.permissions import IsDirector
from rest_framework.response import Response
from rest_framework import status

from directories.models import WorkSchedule, Competence, WorkCategory, OperationType, ExpenseCategory, Product
from .serializers import (
    WorkScheduleSerializer, CompetenceSerializer, WorkCategorySerializer,
    OperationTypeSerializer, ExpenseCategorySerializer, ProductSerializer,
    MaterialSerializer
)
from directories.models import Equipment, Material
from .serializers import EquipmentSerializer

class PositionViewSet(viewsets.ModelViewSet):
    #queryset = Position.objects.all()
    serializer_class = PositionSerializer
    # permission_classes = [permissions.IsAuthenticated, IsDirector]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsDirector()]

    def get_queryset(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Position.objects.exclude(name='Директор')
        return Position.objects.all()

    def perform_destroy(self, instance):
        if instance.name == 'Директор':
            return Response(
                {'error': 'Нельзя удалить должность Директора'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
    
class WorkScheduleViewSet(viewsets.ModelViewSet):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    # permission_classes = [permissions.IsAuthenticated, IsDirector]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsDirector()]

class CompetenceViewSet(viewsets.ModelViewSet):
    queryset = Competence.objects.all()
    serializer_class = CompetenceSerializer
    # permission_classes = [permissions.IsAuthenticated, IsDirector]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsDirector()]

class WorkCategoryViewSet(viewsets.ModelViewSet):
    queryset = WorkCategory.objects.all()
    serializer_class = WorkCategorySerializer
    # permission_classes = [permissions.IsAuthenticated, IsDirector]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsDirector()]

class OperationTypeViewSet(viewsets.ModelViewSet):
    queryset = OperationType.objects.all()
    serializer_class = OperationTypeSerializer
    # permission_classes = [permissions.IsAuthenticated, IsDirector]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsDirector()]

class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    # permission_classes = [permissions.IsAuthenticated, IsDirector]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsDirector()]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [permissions.IsAuthenticated, IsDirector]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsDirector()]
    
class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    # permission_classes = [permissions.IsAuthenticated, IsDirector]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsDirector()]
    

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    # permission_classes = [permissions.IsAuthenticated, IsDirector]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsDirector()]
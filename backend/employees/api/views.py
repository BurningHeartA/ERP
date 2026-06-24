from rest_framework import viewsets, permissions
from users.permissions import IsDirector
from employees.models import Employee, EmployeeCompetence
from .serializers import EmployeeSerializer, EmployeeCompetenceSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirector]


# class EmployeeCompetenceViewSet(viewsets.ModelViewSet):
#     queryset = EmployeeCompetence.objects.all()
#     serializer_class = EmployeeCompetenceSerializer
#     permission_classes = [permissions.IsAuthenticated, IsDirector]

class EmployeeCompetenceViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeCompetenceSerializer
    permission_classes = [permissions.IsAuthenticated, IsDirector]

    def get_queryset(self):
        qs = EmployeeCompetence.objects.all()
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        return qs
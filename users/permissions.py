from rest_framework import permissions


class IsDirector(permissions.BasePermission):
    """Полный доступ только директору."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.is_director
        )


class IsEmployee(permissions.BasePermission):
    """Доступ сотрудникам и директору."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.is_employee
        )


class IsClient(permissions.BasePermission):
    """Доступ клиентам, сотрудникам и директору."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Директор или сотрудник
        if hasattr(request.user, 'profile') and request.user.profile.is_employee:
            return True
        # Клиент
        return hasattr(request.user, 'customer')


class IsOwnerOrDirector(permissions.BasePermission):
    """Объектный доступ: владелец или директор."""
    def has_object_permission(self, request, view, obj):
        # Директор — доступ ко всему
        if hasattr(request.user, 'profile') and request.user.profile.is_director:
            return True
        # Клиент — доступ к своим заявкам и заказам
        if hasattr(request.user, 'customer'):
            if hasattr(obj, 'customer') and obj.customer == request.user.customer:
                return True
        # Сотрудник — доступ к своему табелю
        if hasattr(request.user, 'employee'):
            if hasattr(obj, 'employee') and obj.employee == request.user.employee:
                return True
        return False
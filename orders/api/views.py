from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from users.permissions import IsDirector
from orders.models import Request, Order
from .serializers import RequestSerializer, OrderSerializer
from rest_framework.decorators import action

class RequestViewSet(viewsets.ModelViewSet):
    serializer_class = RequestSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.is_director:
            return Request.objects.exclude(status=Request.Status.DELETED)
        if hasattr(user, 'customer'):
            return Request.objects.filter(customer=user.customer).exclude(status=Request.Status.DELETED)
        return Request.objects.none()

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsDirector()]

    def _can_modify(self, request_obj, user):
        """Проверяет, можно ли редактировать/удалить заявку."""
        is_director = hasattr(user, 'profile') and user.profile.is_director
        if is_director:
            return True
        blocked_statuses = [Request.Status.APPROVED, Request.Status.REJECTED, Request.Status.DELETED]
        return request_obj.status not in blocked_statuses

    def perform_update(self, serializer):
        if not self._can_modify(self.get_object(), self.request.user):
            return Response(
                {'error': 'Нельзя редактировать заявку в этом статусе'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()

    def perform_destroy(self, instance):
        if not self._can_modify(instance, self.request.user):
            return Response(
                {'error': 'Нельзя удалить заявку в этом статусе'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.status = Request.Status.DELETED
        instance.save()

    @action(detail=True, methods=['delete'], url_path='files/(?P<file_id>[^/.]+)')
    def remove_file(self, request, pk=None, file_id=None):
        """Удалить файл из заявки."""
        request_obj = self.get_object()
        from files.models import File
        from django.contrib.contenttypes.models import ContentType

        try:
            ct = ContentType.objects.get_for_model(Request)
            file = File.objects.get(id=file_id, content_type=ct, object_id=request_obj.id)
        except File.DoesNotExist:
            return Response({'error': 'Файл не найден'}, status=404)

        # Проверка прав: клиент может удалять файлы только из своих заявок в допустимом статусе
        user = self.request.user
        is_director = hasattr(user, 'profile') and user.profile.is_director
        if not is_director:
            if request_obj.status not in [Request.Status.NEW, Request.Status.IN_REVIEW]:
                return Response({'error': 'Заявка недоступна для редактирования'}, status=400)

        file.delete()
        return Response(status=204)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.is_director:
            return Order.objects.all()
        if hasattr(user, 'customer'):
            return Order.objects.filter(customer=user.customer)
        return Order.objects.none()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsDirector()]

    def _can_modify(self, order_obj, user):
        """Проверяет, можно ли редактировать/удалить заказ."""
        is_director = hasattr(user, 'profile') and user.profile.is_director
        if is_director:
            return True
        blocked_statuses = [Order.Status.COMPLETED, Order.Status.CLOSED]
        return order_obj.status not in blocked_statuses

    def perform_update(self, serializer):
        if not self._can_modify(self.get_object(), self.request.user):
            return Response(
                {'error': 'Нельзя редактировать заказ в статусе Завершён или Закрыт'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()

    def perform_destroy(self, instance):
        if not self._can_modify(instance, self.request.user):
            return Response(
                {'error': 'Нельзя удалить заказ в статусе Завершён или Закрыт'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.status = Order.Status.CANCELLED
        instance.save()
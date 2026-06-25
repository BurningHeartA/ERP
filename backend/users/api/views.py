from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from clients.models import Customer

from rest_framework import viewsets
from rest_framework import serializers


class RegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        name = request.data.get('name')
        phone = request.data.get('phone', '')
        email = request.data.get('email', '')
        source = request.data.get('source', 'company_website')

        if not username or not password or not name:
            return Response({'error': 'username, password и name обязательны'}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Пользователь с таким логином уже существует'}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email)
        Customer.objects.create(
            user=user,
            name=name,
            phone=phone,
            email=email,
            source=source
        )

        from users.models import UserProfile
        UserProfile.objects.update_or_create(user=user)

        return Response({'message': 'Регистрация успешна'}, status=201)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]



class UserProfileSerializer(serializers.ModelSerializer):
    is_employee = serializers.SerializerMethodField()
    is_director = serializers.SerializerMethodField()
    is_client = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_director', 'is_client']

    def get_is_employee(self, obj):
        return hasattr(obj, 'profile') and obj.profile.is_employee
    
    def get_is_director(self, obj):
        return hasattr(obj, 'profile') and obj.profile.is_director

    def get_is_client(self, obj):
        return hasattr(obj, 'customer')


class MeView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        is_employee = hasattr(user, 'employee')
        is_director = is_employee and user.employee.position.name == 'Директор'
        is_client = hasattr(user, 'customer')
        customer_id = user.customer.id if hasattr(user, 'customer') else None

        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_employee': is_employee,
            'is_director': is_director,
            'is_client': is_client,
            'customer_id': customer_id,
        })
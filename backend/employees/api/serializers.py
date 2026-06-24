from rest_framework import serializers
from employees.models import Employee, EmployeeCompetence
import transliterate
from django.contrib.auth.models import User


class EmployeeCompetenceSerializer(serializers.ModelSerializer):
    competence_name = serializers.CharField(source='competence.name', read_only=True)
    competence_coefficient = serializers.DecimalField(source='competence.coefficient', max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = EmployeeCompetence
        fields = ['id', 'employee', 'competence', 'competence_name', 'competence_coefficient']


class EmployeeSerializer(serializers.ModelSerializer):
    competencies = EmployeeCompetenceSerializer(source='competence_links', many=True, read_only=True)
    full_name = serializers.CharField(read_only=True)
    tariff_rate = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    work_schedule_name = serializers.CharField(source='work_schedule.name', read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'

    def create(self, validated_data):
        # Генерируем логин: фамилия + инициалы латиницей
        last_name = validated_data.get('last_name')
        first_name = validated_data.get('first_name', '')
        middle_name = validated_data.get('middle_name', '')

        # Транслитерация (нужен пакет transliterate: pip install transliterate)
        login_base = transliterate.translit(last_name.lower(), reversed=True)
        initials = ''
        if first_name:
            initials += transliterate.translit(first_name[0].lower(), reversed=True)
        if middle_name:
            initials += transliterate.translit(middle_name[0].lower(), reversed=True)
        username = f"{login_base}_{initials}"

        # Уникальность логина
        counter = 1
        base_username = username
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Создаём пользователя
        user = User.objects.create_user(
            username=username,
            password=User.objects.make_random_password(),
            first_name=first_name,
            last_name=last_name
        )

        # Создаём сотрудника
        employee = Employee.objects.create(user=user, **validated_data)

        # Создаём или обновляем UserProfile
        from users.models import UserProfile
        UserProfile.objects.update_or_create(
            user=user,
            defaults={'is_employee': True}
        )

        return employee
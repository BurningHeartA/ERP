from rest_framework import serializers
from orders.models import Order, Request
from django.contrib.contenttypes.models import ContentType
from files.models import File


# class RequestSerializer(serializers.ModelSerializer):
#     customer_name = serializers.CharField(source='customer.name', read_only=True)

#     class Meta:
#         model = Request
#         fields = '__all__'

class RequestSerializer(serializers.ModelSerializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    files_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Request
        fields = ['id', 'customer', 'description', 'product_name', 'quantity',
                  'desired_deadline', 'status', 'files', 'files_info']

    def get_files_info(self, obj):
        from files.models import File
        ct = ContentType.objects.get_for_model(Request)
        return [{
            'id': f.id,
            'name': f.original_name,
            'category': f.file_category,
            'size': f.file.size,
        } for f in File.objects.filter(content_type=ct, object_id=obj.id)]

    def validate_files(self, value):
        total_size = sum(f.size for f in value)
        if total_size > 50 * 1024 * 1024:  # 50 МБ
            raise serializers.ValidationError('Общий размер файлов превышает 50 МБ')
        return value

    def create(self, validated_data):
        files_data = validated_data.pop('files', [])
        user = self.context['request'].user

        # Если customer не передан — пытаемся определить автоматически
        if 'customer' not in validated_data or validated_data.get('customer') is None:
            if hasattr(user, 'customer'):
                validated_data['customer'] = user.customer
            elif hasattr(user, 'profile') and user.profile.is_employee:
                employee = user.employee
                from clients.models import Customer
                customer = Customer.objects.create(
                    user=user,
                    name=employee.full_name,
                    phone=employee.phone or '',
                    email=employee.email or '',
                    source=Customer.Source.PERSONAL
                )
                validated_data['customer'] = customer
            else:
                raise serializers.ValidationError({'customer': 'Не удалось определить клиента'})

        request = super().create(validated_data)
        self._save_files(request, files_data)
        return request

    def update(self, instance, validated_data):
        files_data = validated_data.pop('files', None)
        request = super().update(instance, validated_data)
        if files_data is not None:
            ct = ContentType.objects.get_for_model(Request)
            existing_size = sum(f.file.size for f in File.objects.filter(content_type=ct, object_id=request.id))
            new_size = sum(f.size for f in files_data)
            if existing_size + new_size > 50 * 1024 * 1024:
                raise serializers.ValidationError('Общий размер файлов заявки превысит 50 МБ')
            self._save_files(request, files_data)
        return request

    def _save_files(self, request, files_data):
        ct = ContentType.objects.get_for_model(Request)
        for file in files_data:
            from files.models import File
            File.objects.create(
                content_type=ct,
                object_id=request.id,
                file=file,
                original_name=file.name,
                file_category='other',
                uploaded_by=self.context['request'].user
            )


class OrderSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
from rest_framework import serializers

from apps.core.account.models import User


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    tenant_current = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
            'username',
            'email',
            'phone',
            'tenant_current'
        )

    def get_full_name(self, obj):
        return User.get_full_name(obj, 2)

    def get_tenant_current(self, obj):
		 if obj.tenant_current:
            return {
                'id': obj.tenant_current_id,
                'title': obj.tenant_current.title,
                'code': obj.tenant_current.code
            }
        return {}


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'password')


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password', 'phone', 'email', 'tenant_current')


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
       

from rest_framework import serializers

from apps.core.account.models import User
from apps.core.company.models import Company


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    # tenant_current = serializers.SerializerMethodField()

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
            # 'tenant_current'
        )

    def get_full_name(self, obj):
        return User.get_full_name(obj, 2)

    # def get_tenant_current(self, obj):
    #     if obj.tenant_current:
    #         return {
    #             'id': obj.tenant_current_id,
    #             'title': obj.tenant_current.title,
    #             'code': obj.tenant_current.code
    #         }
    #     return {}


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone',
            'company_current'
        )


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'password',
            'phone',
            'company_current',
            'email'
        )

    def create(self, validated_data):
        if validated_data.get('tenant_current', None):
            obj = User.objects.create(**validated_data)
            # company - user
            # tenant - user
            # space - user
            return obj
        raise serializers.ValidationError({'tenant_current': 'Tenant not found.'})


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
            'company', 'email',
            'username',
            'company_current_id',
            'phone'
        )

    def get_full_name(self, obj):
        return User.get_full_name(obj, 2)

    def get_company(self, obj):
        companies = []
        company = Company.object_normal.filter(pk=obj.company_current_id)
        for item in company:
            companies.append({
                'code': item.code,
                'title': item.title,
                'representative': item.representative_fullname,
                'license': ['Sale', 'Hr'],
            })
        return companies

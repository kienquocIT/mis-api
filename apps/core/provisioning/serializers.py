import json

from rest_framework import serializers
from apps.core.account.models import User
from apps.core.hr.models import Employee, SpaceEmployee
from apps.core.tenant.models import Tenant
from apps.core.space.models import Space
from apps.core.company.models import Company
from apps.shared import CustomizeEncoder, ProvisioningMsg


# UTILS PROVISIONING
class TenantCreateSerializer(serializers.ModelSerializer):
    plan = serializers.JSONField(required=False)

    class Meta:
        model = Tenant
        fields = '__all__'


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class SpaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = '__all__'


class EmployeeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class EmployeeSpaceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceEmployee
        fields = '__all__'


# VIEW PROVISIONING
class UserRequestCreateSerializer(serializers.Serializer):  # noqa
    id = serializers.UUIDField()
    full_name = serializers.CharField()
    email = serializers.CharField(allow_null=True, allow_blank=True)
    phone = serializers.CharField(allow_null=True, allow_blank=True)

    def validate(self, attrs):
        return json.dumps(attrs, cls=CustomizeEncoder)


class ProvisioningTenantData(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    user_request_created = UserRequestCreateSerializer()
    auto_create_company = serializers.BooleanField()
    company_quality_max = serializers.IntegerField()
    plan = serializers.JSONField(required=False)

    class Meta:
        model = Tenant
        fields = (
            'title', 'code', 'sub_domain',
            'representative_fullname', 'representative_phone_number',
            'auto_create_company', 'company_quality_max',
            'user_request_created',
            'plan'
        )


class ProvisioningUserData(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=80)
    last_name = serializers.CharField(max_length=150)
    email = serializers.CharField(max_length=150)
    phone = serializers.CharField(
        max_length=50,
        allow_null=True
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'username', 'password')


class ProvisioningCreateNewTenant(serializers.Serializer):  # noqa
    tenant_data = ProvisioningTenantData()
    user_data = ProvisioningUserData(required=False)
    create_admin = serializers.BooleanField()
    create_employee = serializers.BooleanField()
    plan_data = serializers.JSONField(required=False)

    def validate(self, data):
        if data['create_employee'] is False or data['create_admin'] is False:
            raise serializers.ValidationError({'create_employee': ProvisioningMsg.EMPLOYEE_DEPENDENCIES_ON_COMPANY})
        if not data.get('user_data', None):
            raise serializers.ValidationError({'user_data': ProvisioningMsg.SYNC_REQUIRED_USER_DATA})
        return data


class TenantListSerializer(serializers.ModelSerializer):
    admin_info = serializers.JSONField()
    user_request_created = serializers.JSONField()

    class Meta:
        model = Tenant
        fields = '__all__'


class TenantListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ('title', 'code')

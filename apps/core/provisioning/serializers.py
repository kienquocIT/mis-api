import json

from rest_framework import serializers
from apps.core.account.models import User
from apps.core.hr.models import Employee, SpaceEmployee
from apps.core.tenant.models import Tenant, Company, Space
from apps.shared import UUIDEncoder, APIMsg, ProvisioningMsg


# UTILS PROVISIONING
class TenantCreateSerializer(serializers.ModelSerializer):
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
    email = serializers.CharField()
    phone = serializers.CharField()

    def validate(self, attrs):
        return json.dumps(attrs, cls=UUIDEncoder)


class ProvisioningTenantData(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    user_request_created = UserRequestCreateSerializer()
    auto_create_company = serializers.BooleanField()
    company_quality_max = serializers.IntegerField()

    class Meta:
        model = Tenant
        fields = (
            'title', 'code', 'sub_domain',
            'representative_fullname', 'representative_phone_number',
            'auto_create_company', 'company_quality_max',
            'user_request_created',
        )


class ProvisioningUserData(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=80)
    last_name = serializers.CharField(max_length=150)
    email = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=50)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'username', 'password')


class ProvisioningCreateNewTenant(serializers.Serializer):  # noqa
    tenant_data = ProvisioningTenantData()
    user_data = ProvisioningUserData(required=False)
    create_admin = serializers.BooleanField()
    create_employee = serializers.BooleanField()

    def validate(self, data):
        if data['create_admin'] is True:
            if not data.get('user_data', None):
                raise serializers.ValidationError({'user_data': APIMsg.FIELD_REQUIRED})
        else:
            data.pop('user_data', None)

        if data['create_employee'] is True and (
                not data['tenant_data']['auto_create_company'] or not data['create_admin'] is True
        ):
            raise serializers.ValidationError({'create_employee': ProvisioningMsg.EMPLOYEE_DEPENDENCIES_ON_COMPANY})
        return data


class TenantListSerializer(serializers.ModelSerializer):
    admin_info = serializers.JSONField()
    user_request_created = serializers.JSONField()

    class Meta:
        model = Tenant
        fields = '__all__'

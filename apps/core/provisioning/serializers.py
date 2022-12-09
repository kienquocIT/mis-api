import json

from rest_framework import serializers
from apps.core.account.models import User
from apps.core.hr.models import Employee, SpaceEmployee
from apps.core.tenant.models import Tenant, Company, Space
from apps.shared import UUIDEncoder


# UTILS PROVISIONING
class TenantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        # fields = (
        #     'tenant',
        #     'license_usage',
        #     'user_count',
        # )


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
    user_request_created = UserRequestCreateSerializer()

    class Meta:
        model = Tenant
        fields = (
            'title', 'code', 'sub_domain',
            'representative_fullname', 'representative_phone_number',
            'user_request_created'
        )


class ProvisioningEmployeeData(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('first_name', 'last_name', 'email', 'phone')


class ProvisioningUserData(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')


class ProvisioningCreateNewTenant(serializers.Serializer):  # noqa
    tenant_data = ProvisioningTenantData()
    employee_data = ProvisioningEmployeeData()
    user_data = ProvisioningUserData()
    user_request_created = UserRequestCreateSerializer()

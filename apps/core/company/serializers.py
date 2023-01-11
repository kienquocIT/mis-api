from rest_framework import serializers
from apps.core.company.models import Company
from apps.core.tenant.models import Tenant
from apps.core.hr.models import Employee


# Company Serializer
class CompanyListSerializer(serializers.ModelSerializer):
    tenant_auto_create_company = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            'id',
            'title',
            'code',
            'date_created',
            'representative_fullname',
            'tenant_auto_create_company',
        )

    def get_tenant_auto_create_company(self, obj):
        try:
            return Tenant.object_normal.filter(id=obj.tenant_id).first().auto_create_company
        except Exception as e:
            raise serializers.ValidationError("Tenant_auto_create_company fields does not exist.")


class CompanyDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = (
            'id',
            'title',
            'code',
            'representative_fullname',
            'email',
            'address',
            'phone'
        )


class CompanyCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'representative_fullname',
            'address',
            'email',
            'phone',
        )


class CompanyUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'representative_fullname',
            'address',
            'email',
            'phone',
        )


class TenantInformationSerializer(serializers.ModelSerializer):
    license_used = serializers.SerializerMethodField()
    power_user = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()
    employee_linked_user = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            'id',
            'title',
            'code',
            'date_created',
            'representative_fullname',
            'total_user',
            'license_used',
            'power_user',
            'employee',
            'employee_linked_user'
        )

    def get_license_used(self, obj):
        try:
            return [
                {'key': 'Hrm', 'quantity': 10},
                {'key': 'Sale', 'quantity': 10}
            ]
        except Exception as e:
            raise serializers.ValidationError("License used does not exist.")

    def get_power_user(self, obj):
        try:
            return 2
        except Exception as e:
            raise serializers.ValidationError("Power user used does not exist.")

    def get_employee(self, obj):
        try:
            return 18
        except Exception as e:
            raise serializers.ValidationError("Employee used does not exist.")

    def get_employee_linked_user(self, obj):
        try:
            return 4
        except Exception as e:
            raise serializers.ValidationError("Employee linked user used does not exist.")
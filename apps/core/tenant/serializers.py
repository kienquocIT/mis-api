from rest_framework import serializers
from apps.core.company.models import Company
from apps.core.tenant.models import Tenant
from apps.core.hr.models import Employee


class TenantDetailSerializer(serializers.ModelSerializer):
    license_used = serializers.SerializerMethodField()
    power_user = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()
    employee_connect_to_user = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            'id',
            'title',
            'code',
            'tenant_id',
            'date_created',
            'representative_fullname',
            'total_user',
            'license_used',
            'power_user',
            'employee',
            'employee_connect_to_user'
        )

    def validate_tenant_id(self, attrs):
        try:
            return Tenant.objects.get(id=attrs).id
        except Exception as e:
            raise serializers.ValidationError("Tenant does not exist.")

    def get_license_used(self, obj):
        return 25

    def get_power_user(self, obj):
        return 2

    def get_employee(self, obj):
        return Employee.objects.filter(company_id=obj.id).count()

    def get_employee_connect_to_user(self, obj):
        return Employee.objects.filter(company_id=obj.id).count()

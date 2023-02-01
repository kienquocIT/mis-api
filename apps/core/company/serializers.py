import random
from rest_framework import serializers
from apps.core.company.models import Company, CompanyUserEmployee
from apps.core.account.models import User
# from apps.core.tenant.models import Tenant
from apps.core.hr.models import Employee
from apps.shared import DisperseModel


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

    @classmethod
    def get_tenant_auto_create_company(cls, obj):
        return obj.tenant.auto_create_company


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


class CompanyOverviewSerializer(serializers.ModelSerializer):
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
            'license_used',
            'total_user',
            'power_user',
            'employee',
            'employee_linked_user'
        )

    @classmethod
    def get_license_used(cls, obj):
        return [
                {'key': 'Hrm', 'quantity': random.randrange(20, 50, 3)},
                {'key': 'Sale', 'quantity': random.randrange(20, 50, 3)},
                {'key': 'Personal', 'quantity': random.randrange(20, 50, 3)},
                {'key': 'E-office', 'quantity': random.randrange(20, 50, 3)},
        ]

    @classmethod
    def get_power_user(cls, obj):
        return User.objects.filter(company_current=obj.id).filter(is_superuser=1).count()

    @classmethod
    def get_employee(cls, obj):
        return Employee.objects.filter(company=obj.id).count()

    @classmethod
    def get_employee_linked_user(cls, obj):
        return Employee.objects.filter(company=obj.id).exclude(user_id__isnull=True).count()


# Company Map User Employee
class CompanyUserNotMapEmployeeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = CompanyUserEmployee
        fields = (
            'id',
            'user'
        )

    def get_user(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
                'email': obj.user.email,
                'phone': obj.user.phone,
                'full_name': User.get_full_name(obj.user, 2),
            }
        return {}


class CompanyUserDetailSerializer(serializers.ModelSerializer):
    companies = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'company_current',
            'companies',
        )

    @classmethod
    def get_companies(cls, obj):
        company_user = CompanyUserEmployee.object_normal.filter(user_id=obj.id)
        companies = []
        for item in company_user:
            try:
                company = Company.object_normal.get(id=item.company_id)
                companies.append({
                    'id': company.id,
                    'name': company.title,
                })
            except Exception as err:
                raise serializers.ValidationError("Company does not exist.")
        return companies


class CompanyUserUpdateSerializer(serializers.ModelSerializer):
    companies = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False,
    )

    class Meta:
        model = User
        fields = (
            'companies',
        )

    def update(self, instance, validated_data):
        if 'companies' in validated_data:
            user_companies = CompanyUserEmployee.object_normal.filter(user_id=instance)
            user_companies = [i.company_id for i in user_companies]
            data_bulk = validated_data.pop('companies')
            if data_bulk:
                bulk_info = []
                for company in data_bulk:
                    if company in user_companies:
                        user_companies.remove(company)
                    else:
                        bulk_info.append(CompanyUserEmployee(company_id=company, user_id=instance.id))
                if bulk_info:
                    CompanyUserEmployee.object_normal.bulk_create(bulk_info)
                for co in user_companies:
                    if User.objects.filter(company_current=co).exists():
                        print("Can not delete current")
                        raise serializers.ValidationError('Can not delete company_current')
                    else:
                        co_old = CompanyUserEmployee.object_normal.get(company_id=co, user_id=instance.id)
                        if co_old.employee_id is None:
                            co_old.delete()
                        else:
                            co_old = CompanyUserEmployee.user_id = None
                            co_old.save()
            return instance

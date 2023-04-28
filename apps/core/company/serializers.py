from crum import get_current_user
from django.conf import settings
from django.db.models import Count, Subquery
from rest_framework import serializers

from apps.core.company.models import Company, CompanyUserEmployee, CompanyConfig
from apps.core.account.models import User
from apps.core.hr.models import Employee, PlanEmployee
from apps.shared import DisperseModel
from apps.shared.translations.company import CompanyMsg


# Company Config
class CompanyConfigDetailSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()

    @classmethod
    def get_currency(cls, obj):
        return {
            "id": obj.currency.id,
            "title": obj.currency.title,
            "code": obj.currency.code,
            "symbol": obj.currency.symbol
        } if obj.currency else {}

    class Meta:
        model = CompanyConfig
        fields = ('language', 'currency', 'currency_rule',)


class CompanyConfigUpdateSerializer(serializers.ModelSerializer):
    currency = serializers.CharField()

    @classmethod
    def validate_currency(cls, attrs):
        currency_cls = DisperseModel(app_model='base.currency').get_model()
        try:
            # valid currency allow use in company after add foreign key currency to sale-data.currency model
            return currency_cls.objects.get(code=attrs)
        except currency_cls.DoesNotExist:
            pass
        raise serializers.ValidationError({'currency': CompanyMsg.CURRENCY_NOT_EXIST})

    @classmethod
    def validate_language(cls, attrs):
        if attrs in [x[0] for x in settings.LANGUAGE_CHOICE]:
            return attrs
        raise serializers.ValidationError({'language': CompanyMsg.LANGUAGE_NOT_SUPPORT})

    class Meta:
        model = CompanyConfig
        fields = ('language', 'currency', 'currency_rule',)

    def update(self, instance, validated_data):
        currency_rule = validated_data.pop('currency_rule', {})
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.currency_rule.update(currency_rule)
        instance.save(update_fields=['language', 'currency', 'currency_rule'])
        return instance


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

    def validate(self, attrs):
        user_obj = get_current_user()
        if user_obj and hasattr(user_obj, 'tenant_current'):
            company_quantity_max = user_obj.tenant_current.company_quality_max
            current_company_quantity = Company.objects.filter(tenant=user_obj.tenant_current).count()
            if current_company_quantity <= company_quantity_max:
                return attrs
            raise serializers.ValidationError(
                {'detail': CompanyMsg.MAXIMUM_COMPANY_LIMITED.format(str(company_quantity_max))}
            )
        raise serializers.ValidationError({'detail': CompanyMsg.VALID_NEED_TENANT_DATA})


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
            'employee_linked_user',
        )

    @classmethod
    def get_license_used(cls, obj):
        result = []
        data_dict = {}
        company_employee_plan = PlanEmployee.objects.select_related(
            'plan'
        ).filter(
            employee__company=obj
        )
        if company_employee_plan:
            for employee_plan in company_employee_plan:
                if employee_plan.plan.code not in data_dict:
                    data_dict.update({employee_plan.plan.code: 1})
                else:
                    data_dict[employee_plan.plan.code] += 1
        if data_dict:
            for key, value in data_dict.items():
                result.append(
                    {
                        'key': key,
                        'quantity': value
                    }
                )

        return result

    @classmethod
    def get_power_user(cls, obj):
        objs = CompanyUserEmployee.objects.filter(
            user_id__in=Subquery(
                CompanyUserEmployee.objects.filter(company_id=obj.id).values_list('user_id', flat=True)
            )
        ).values('user_id').annotate(
            num_companies=Count('company_id', distinct=True)
        ).filter(num_companies__gte=2)
        return objs.count()

    @classmethod
    def get_employee(cls, obj):
        return obj.hr_employee_belong_to_company.count()

    @classmethod
    def get_employee_linked_user(cls, obj):
        return CompanyUserEmployee.objects.filter(
            company=obj,
            user_id__isnull=False,
            employee_id__isnull=False
        ).count()


# Company Map User Employee
class CompanyUserNotMapEmployeeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = CompanyUserEmployee
        fields = (
            'id',
            'user'
        )

    @classmethod
    def get_user(cls, obj):
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


# Company Overview All
class CompanyOverviewDetailDataSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = CompanyUserEmployee
        fields = (
            "employee",
            "user",
        )

    @classmethod
    def get_employee(cls, obj):
        license_list = []
        if obj.employee:
            plan_list = obj.employee.plan.all()
            if plan_list:
                for plan in plan_list:
                    license_list.append(
                        {
                            'id': plan.id,
                            'title': plan.title,
                            'code': plan.code
                        }
                    )
            return {
                'id': obj.employee.id,
                'full_name': Employee.get_full_name(obj.employee, 2),
                'code': obj.employee.code,
                'license_list': license_list
            }
        return {}

    @classmethod
    def get_user(cls, obj):
        company_list = []
        if obj.user:
            company_user_list = CompanyUserEmployee.objects.select_related('company').filter(
                user=obj.user
            )
            if company_user_list:
                for company_user in company_user_list:
                    company_list.append(
                        {
                            'id': company_user.company.id,
                            'title': company_user.company.title,
                            'code': company_user.company.code,
                            'is_created_company': company_user.is_created_company
                        }
                    )
            return {
                'id': obj.user.id,
                'full_name': User.get_full_name(obj.user, 2),
                'username': obj.user.username,
                'company_list': company_list
            }
        return {}


class CompanyOverviewDetailSerializer(serializers.ModelSerializer):
    company_data = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            "id",
            "title",
            "company_data",
        )

    @classmethod
    def get_company_data(cls, obj):
        return CompanyOverviewDetailDataSerializer(
            CompanyUserEmployee.objects.select_related(
                'user',
                'employee'
            ).filter(company=obj),
            many=True
        ).data


# Company Overview Employee Connected
class CompanyOverviewConnectedSerializer(serializers.ModelSerializer):
    company_data = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            "id",
            "title",
            "company_data",
        )

    @classmethod
    def get_company_data(cls, obj):
        return CompanyOverviewDetailDataSerializer(
            CompanyUserEmployee.objects.select_related(
                'user',
                'employee'
            ).filter(
                company=obj,
                employee__isnull=False
            ),
            many=True
        ).data

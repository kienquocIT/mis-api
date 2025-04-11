import datetime
from crum import get_current_user
from rest_framework import serializers
from django.conf import settings
from django.db.models import Count, Subquery
from apps.core.account.models import User
from apps.core.company.models import (
    Company, CompanyConfig, CompanyFunctionNumber, CompanyUserEmployee,
)
from apps.core.hr.models import Employee, PlanEmployee
from apps.masterdata.saledata.models import Periods
from apps.sales.report.models import ReportStockLog
from apps.shared import DisperseModel, AttMsg, FORMATTING, BaseMsg
from apps.shared.translations.company import CompanyMsg


# Company Config
class CurrencyRuleDetail(serializers.Serializer):  # noqa
    prefix = serializers.CharField()
    suffix = serializers.CharField()
    decimal = serializers.CharField()
    thousands = serializers.CharField()
    allowZero = serializers.CharField()
    precision = serializers.CharField()
    affixesStay = serializers.CharField()
    allowNegative = serializers.CharField()


class CompanyConfigDetailSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()
    currency_rule = CurrencyRuleDetail()
    sub_domain = serializers.SerializerMethodField()

    @classmethod
    def get_currency(cls, obj):
        return {
            "id": obj.currency.id,
            "title": obj.currency.title,
            "code": obj.currency.code,
            "symbol": obj.currency.symbol
        } if obj.currency else {}

    @classmethod
    def get_sub_domain(cls, obj):
        return obj.company.sub_domain if obj.company else ''

    class Meta:
        model = CompanyConfig
        fields = (
            'language',
            'currency',
            'currency_rule',
            'sub_domain',
            'definition_inventory_valuation',
            'default_inventory_value_method',
            'cost_per_warehouse',
            'cost_per_lot',
            'cost_per_project',
            'accounting_policies',
            'applicable_circular'
        )


class CompanyConfigUpdateSerializer(serializers.ModelSerializer):
    currency = serializers.CharField()
    sub_domain = serializers.CharField(max_length=35, required=False)
    definition_inventory_valuation = serializers.BooleanField(default=False)
    default_inventory_value_method = serializers.IntegerField(default=1)

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

    def validate_sub_domain(self, attrs):
        if Company.objects.filter(sub_domain=attrs).exclude(pk=self.instance.company_id).exists():
            raise serializers.ValidationError({'sub_domain': CompanyMsg.SUB_DOMAIN_EXIST})
        return attrs

    @classmethod
    def validate_definition_inventory_valuation(cls, attrs):
        if attrs in [0, 1]:
            return attrs
        raise serializers.ValidationError({'definition_inventory_valuation': CompanyMsg.DIV_NOT_VALID})

    @classmethod
    def validate_default_inventory_value_method(cls, attrs):
        if attrs in [0, 1, 2]:
            return attrs
        raise serializers.ValidationError({'default_inventory_value_method': CompanyMsg.DIV_METHOD_NOT_VALID})

    def validate(self, validate_data):
        tenant_obj = self.instance.company.tenant
        company_obj = self.instance.company
        this_period = Periods.get_current_period(tenant_obj.id, company_obj.id)
        if this_period:
            has_trans = ReportStockLog.objects.filter(
                tenant=tenant_obj, company=company_obj, report_stock__period_mapped=this_period
            ).exists()
            old_div_config = company_obj.company_config.definition_inventory_valuation
            if has_trans and validate_data['definition_inventory_valuation'] != old_div_config:
                raise serializers.ValidationError({
                    'definition_inventory_valuation':
                        "Can't update Definition inventory valuation because there are transactions in this Period."
                })
            validate_data['this_period'] = this_period

            old_cost_setting = [
                self.instance.cost_per_warehouse,
                self.instance.cost_per_lot,
                self.instance.cost_per_project
            ]
            new_cost_setting = [
                validate_data.get('cost_per_warehouse'),
                validate_data.get('cost_per_lot'),
                validate_data.get('cost_per_project')
            ]
            if has_trans and new_cost_setting != old_cost_setting:
                raise serializers.ValidationError({'error': "Can't change cost setting in same period year."})
            return validate_data
        # chỗ này không được sửa key lỗi trả về - fiscal_year_not_found
        # (vì trên UI dựa vào key lỗi này để check đã có năm tài chính hay chưa)
        raise serializers.ValidationError({"fiscal_year_not_found": 'This period is not found.'})

    def update(self, instance, validated_data):
        this_period = validated_data.pop('this_period')
        sub_domain = validated_data.pop('sub_domain', None)
        currency_rule = validated_data.pop('currency_rule', {})

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save(update_fields=[
            'language',
            'currency',
            'currency_rule',
            'definition_inventory_valuation',
            'default_inventory_value_method',
            'cost_per_warehouse',
            'cost_per_lot',
            'cost_per_project'
        ])

        this_period.definition_inventory_valuation = instance.definition_inventory_valuation
        this_period.default_inventory_value_method = instance.default_inventory_value_method
        this_period.cost_per_warehouse = instance.cost_per_warehouse
        this_period.cost_per_lot = instance.cost_per_lot
        this_period.cost_per_project = instance.cost_per_project
        this_period.save(update_fields=[
            'definition_inventory_valuation',
            'default_inventory_value_method',
            'cost_per_warehouse',
            'cost_per_lot',
            'cost_per_project'
        ])

        if currency_rule and all(
            key in currency_rule for key in ['prefix', 'suffix', 'thousands', 'decimal', 'precision']
        ):
            currency_rule['allowZero'] = True
            currency_rule['affixesStay'] = True
            currency_rule['allowNegative'] = False
            instance.currency_rule = currency_rule
            instance.save(update_fields=['currency_rule'])
        if sub_domain:
            instance.company.sub_domain = sub_domain
            instance.company.save(update_fields=['sub_domain'])

        return instance

    class Meta:
        model = CompanyConfig
        fields = (
            'language',
            'currency',
            'currency_rule',
            'sub_domain',
            'definition_inventory_valuation',
            'default_inventory_value_method',
            'cost_per_warehouse',
            'cost_per_lot',
            'cost_per_project'
        )


class AccountingPoliciesUpdateSerializer(serializers.ModelSerializer):
    def validate(self, validate_data):
        tenant_obj = self.instance.company.tenant
        company_obj = self.instance.company
        this_period = Periods.get_current_period(tenant_obj.id, company_obj.id)
        if this_period:
            validate_data['this_period'] = this_period
        else:
            # chỗ này không được sửa key lỗi trả về - fiscal_year_not_found
            # (vì trên UI company dựa vào key lỗi này để check đã có năm tài chính hay chưa)
            raise serializers.ValidationError(
                {'fiscal_year_not_found': f"Can't find fiscal year {datetime.datetime.now().year}."}
            )
        return validate_data

    def update(self, instance, validated_data):
        this_period = validated_data.pop('this_period')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save(update_fields=['accounting_policies', 'applicable_circular'])

        this_period.accounting_policies = instance.accounting_policies
        this_period.applicable_circular = instance.applicable_circular
        this_period.save(update_fields=['accounting_policies', 'applicable_circular'])

        return instance

    class Meta:
        model = CompanyConfig
        fields = (
            'accounting_policies',
            'applicable_circular',
        )


# Company Serializer
class CompanyListSerializer(serializers.ModelSerializer):
    tenant_auto_create_company = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()

    @classmethod
    def get_logo(cls, obj):
        if obj.logo:
            return obj.logo.url
        return None

    class Meta:
        model = Company
        fields = (
            'id',
            'title',
            'code',
            'date_created',
            'representative_fullname',
            'tenant_auto_create_company',
            'sub_domain',
            'logo',
        )

    @classmethod
    def get_tenant_auto_create_company(cls, obj):
        return obj.tenant.auto_create_company


class CompanyDetailSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    cost_cfg = serializers.SerializerMethodField()
    company_function_number = serializers.SerializerMethodField()

    @classmethod
    def get_logo(cls, obj):
        return obj.logo.url if obj.logo else None

    @classmethod
    def get_icon(cls, obj):
        return obj.icon.url if obj.icon else None

    class Meta:
        model = Company
        fields = (
            'id',
            'title',
            'code',
            'representative_fullname',
            'email',
            'address',
            'phone',
            'fax',
            'company_function_number',
            'sub_domain',
            'logo',
            'icon',
            'cost_cfg'
        )

    @classmethod
    def get_company_function_number(cls, obj):
        company_function_number = []
        for item in obj.company_function_number.all():
            company_function_number.append({
                'function': item.function,
                'numbering_by': item.numbering_by,
                'schema_text': item.schema_text,
                'schema': item.schema,
                'first_number': item.first_number,
                'last_number': item.last_number,
                'reset_frequency': item.reset_frequency,
                'min_number_char': item.min_number_char
            })
        return company_function_number

    @classmethod
    def get_cost_cfg(cls, obj):
        return {
            'cost_per_warehouse': obj.company_config.cost_per_warehouse,
            'cost_per_lot': obj.company_config.cost_per_lot,
            'cost_per_project': obj.company_config.cost_per_project,
        }


def create_company_function_number(company_obj, company_function_number_data):
    date_now = datetime.datetime.now()
    data_calendar = datetime.date.today().isocalendar()
    updated_function = []
    for item in company_function_number_data:
        function_name = item.get('function')
        obj = CompanyFunctionNumber.objects.filter(company=company_obj, function=function_name)
        if obj.count() == 1:
            updated_function.append(function_name)
            updated_fields = {
                **item,
                'latest_number': int(item.get('last_number', None)) - 1,
                'year_reset': date_now.year,
                'month_reset': int(f"{date_now.year}{date_now.month:02}"),
                'week_reset': int(f"{data_calendar[0]}{data_calendar[1]:02}"),
                'day_reset': int(f"{data_calendar[0]}{data_calendar[1]:02}{data_calendar[2]}")
            } if obj.first().latest_number is None else {**item}
            obj.update(**updated_fields)

    CompanyFunctionNumber.objects.filter_current(company=company_obj).exclude(function__in=updated_function).update(
        numbering_by=0, schema=None, schema_text=None, first_number=None, last_number=None, reset_frequency=None,
        min_number_char=None, latest_number=None, year_reset=None, month_reset=None, week_reset=None, day_reset=None
    )
    return True


class CompanyCreateSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=150, required=True)
    address = serializers.CharField(max_length=150, required=True)
    phone = serializers.CharField(max_length=25, required=True)

    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'representative_fullname',
            'address',
            'email',
            'phone',
            'fax'
        )

    @classmethod
    def validate_code(cls, attrs):
        attrs = attrs.lower()
        if Company.objects.filter(code=attrs).exists():
            raise serializers.ValidationError({
                'code': BaseMsg.CODE_IS_EXISTS,
            })
        return attrs

    def validate(self, validate_data):
        for item in self.initial_data.get('company_function_number_data', []):
            if item.get('numbering_by', None) == 0 and item.get('schema', None) and item.get('schema_text', None):
                raise serializers.ValidationError({'detail': CompanyMsg.INVALID_COMPANY_FUNCTION_NUMBER_DATA})
        user_obj = get_current_user()
        if user_obj and hasattr(user_obj, 'tenant_current'):
            company_quantity_max = user_obj.tenant_current.company_quality_max
            current_company_quantity = Company.objects.filter(tenant=user_obj.tenant_current).count()
            if current_company_quantity <= company_quantity_max:
                return validate_data
            raise serializers.ValidationError({
                'detail': CompanyMsg.MAXIMUM_COMPANY_LIMITED.format(str(company_quantity_max))
            })
        raise serializers.ValidationError({'detail': CompanyMsg.VALID_NEED_TENANT_DATA})

    def create(self, validated_data):
        company_obj = Company.objects.create(**validated_data)
        create_company_function_number(company_obj, self.initial_data.get('company_function_number_data', []))
        return company_obj


class CompanyUpdateSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=150, required=True)
    address = serializers.CharField(max_length=150, required=True)
    phone = serializers.CharField(max_length=25, required=True)

    class Meta:
        model = Company
        fields = (
            'title',
            'representative_fullname',
            'address',
            'email',
            'phone',
            'fax'
        )

    def validate(self, validate_data):
        for item in self.initial_data.get('company_function_number_data', []):
            if item.get('numbering_by', None) == 0 and item.get('schema', None) and item.get('schema_text', None):
                raise serializers.ValidationError({'detail': CompanyMsg.INVALID_COMPANY_FUNCTION_NUMBER_DATA})
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        create_company_function_number(instance, self.initial_data.get('company_function_number_data', []))
        return instance


class CompanyUploadLogoSerializer(serializers.ModelSerializer):
    @classmethod
    def validate_logo(cls, attrs):
        if attrs and hasattr(attrs, 'size'):
            if isinstance(attrs.size, int) and attrs.size < settings.FILE_SIZE_COMPANY_LOGO:
                return attrs
            file_size_limit = AttMsg.FILE_SIZE_SHOULD_BE_LESS_THAN_X.format(
                FORMATTING.size_to_text(settings.FILE_SIZE_COMPANY_LOGO)
            )
            raise serializers.ValidationError({'file': file_size_limit})
        raise serializers.ValidationError({'file': AttMsg.FILE_NO_DETECT_SIZE})

    @classmethod
    def validate_icon(cls, attrs):
        if attrs and hasattr(attrs, 'size'):
            if isinstance(attrs.size, int) and attrs.size < settings.FILE_SIZE_COMPANY_ICON:
                return attrs
            file_size_limit = AttMsg.FILE_SIZE_SHOULD_BE_LESS_THAN_X.format(
                FORMATTING.size_to_text(settings.FILE_SIZE_COMPANY_LOGO)
            )
            raise serializers.ValidationError({'file': file_size_limit})
        raise serializers.ValidationError({'file': AttMsg.FILE_NO_DETECT_SIZE})

    def update(self, instance, validated_data):
        logo = validated_data.get('logo', None)
        icon = validated_data.get('icon', None)
        if logo or icon:
            if logo:
                if instance.logo:
                    instance.logo.storage.delete(instance.logo.name)
                instance.logo = logo
            if icon:
                if instance.icon:
                    instance.icon.storage.delete(instance.icon.name)
                instance.icon = icon
            instance.save()
        return instance

    class Meta:
        model = Company
        fields = ('logo', 'icon',)


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

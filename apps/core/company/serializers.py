import datetime
from crum import get_current_user
from django.conf import settings
from django.db.models import Count, Subquery
from rest_framework import serializers

from apps.core.company.models import Company, CompanyUserEmployee, CompanyConfig, CompanyFunctionNumber
from apps.core.account.models import User
from apps.core.base.models import Currency as BaseCurrency
from apps.core.hr.models import Employee, PlanEmployee
from apps.sales.opportunity.models import StageCondition, OpportunityConfigStage
from apps.shared import DisperseModel
from apps.shared.extends.signals import ConfigDefaultData
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
        fields = ('language', 'currency', 'currency_rule', 'sub_domain')


class CompanyConfigUpdateSerializer(serializers.ModelSerializer):
    currency = serializers.CharField()
    sub_domain = serializers.CharField(max_length=35, required=False)

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

    class Meta:
        model = CompanyConfig
        fields = ('language', 'currency', 'currency_rule', 'sub_domain')

    def update(self, instance, validated_data):
        sub_domain = validated_data.pop('sub_domain', None)
        currency_rule = validated_data.pop('currency_rule', {})
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.currency_rule.update(currency_rule)
        instance.save(update_fields=['language', 'currency', 'currency_rule'])

        if sub_domain:
            instance.company.sub_domain = sub_domain
            instance.company.save(update_fields=['sub_domain'])

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
            'sub_domain'
        )

    @classmethod
    def get_tenant_auto_create_company(cls, obj):
        return obj.tenant.auto_create_company


class CompanyDetailSerializer(serializers.ModelSerializer):
    company_setting = serializers.SerializerMethodField()
    company_function_number = serializers.SerializerMethodField()

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
            'company_setting',
            'company_function_number',
			'sub_domain'
        )

    @classmethod
    def get_company_setting(cls, obj):
        company_setting = obj.company_setting.all()
        if company_setting.count() > 0:
            company_setting = company_setting.first()
            return {
                'primary_currency': {
                    'id': company_setting.primary_currency_id,
                    'title': company_setting.primary_currency.title,
                    'abbreviation': company_setting.primary_currency.code,
                } if company_setting.primary_currency else {},
                'definition_inventory_valuation': company_setting.definition_inventory_valuation,
                'default_inventory_value_method': company_setting.default_inventory_value_method,
                'cost_per_warehouse': company_setting.cost_per_warehouse,
                'cost_per_lot_batch': company_setting.cost_per_lot_batch
            }
        return {}

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
                'reset_frequency': item.reset_frequency
            })
        return company_function_number


def create_company_function_number(company_obj, company_function_number_data):
    date_now = datetime.datetime.now()
    data_calendar = datetime.date.today().isocalendar()
    updated_function = []
    for item in company_function_number_data:
        obj = CompanyFunctionNumber.objects.filter(
            company=company_obj,
            function=item.get('function', None)
        )
        if obj.count() == 1:
            updated_function.append(item.get('function', None))
            updated_fields = {
                **item,
                'latest_number': int(item.get('last_number', None)) - 1,
                'year_reset': date_now.year,
                'month_reset': int(f"{date_now.year}{date_now.month:02}"),
                'week_reset': int(f"{data_calendar[0]}{data_calendar[1]:02}"),
                'day_reset': int(f"{data_calendar[0]}{data_calendar[1]:02}{data_calendar[2]}")
            }
            obj.update(**updated_fields)

    CompanyFunctionNumber.objects.filter_current(company=company_obj).exclude(
        function__in=updated_function
    ).update(
        numbering_by=0,
        schema=None,
        schema_text=None,
        first_number=None,
        last_number=None,
        reset_frequency=None,
        latest_number=None,
        year_reset=None,
        month_reset=None,
        week_reset=None,
        day_reset=None
    )
    return True


class CompanyCreateSerializer(serializers.ModelSerializer):
    primary_currency_id = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'representative_fullname',
            'address',
            'email',
            'phone',
            'fax',
            'primary_currency_id',
            'definition_inventory_valuation',
            'default_inventory_value_method',
            'cost_per_warehouse',
            'cost_per_lot_batch'
        )

    @classmethod
    def validate_primary_currency_id(cls, attrs):
        if attrs:
            if not BaseCurrency.objects.filter(id=attrs).exists():
                raise serializers.ValidationError({'primary currency': CompanyMsg.INVALID_BASE_CURRENCY})
            return attrs
        raise serializers.ValidationError({'primary currency': CompanyMsg.PRIMARY_CURRENCY_IS_NOT_NULL})

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
    primary_currency_id = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            'title',
            'code',
            'representative_fullname',
            'address',
            'email',
            'phone',
            'fax',
            'primary_currency_id',
            'definition_inventory_valuation',
            'default_inventory_value_method',
            'cost_per_warehouse',
            'cost_per_lot_batch'
        )

    @classmethod
    def validate_primary_currency_id(cls, attrs):
        if attrs:
            if not BaseCurrency.objects.filter(id=attrs).exists():
                raise serializers.ValidationError({'primary currency': CompanyMsg.INVALID_BASE_CURRENCY})
            return attrs
        raise serializers.ValidationError({'primary currency': CompanyMsg.PRIMARY_CURRENCY_IS_NOT_NULL})

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


class RestoreDefaultOpportunityConfigStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = []

    @classmethod
    def update_stage_default(cls, list_stage_update, dict_data, bulk_data):
        for stage in list_stage_update:
            stage_data = dict_data[stage.indicator]
            if stage.indicator == stage_data['indicator']:
                obj = stage
                is_changed = False

                # Check data changed
                if obj.description != stage_data['description']:
                    obj.description = stage_data['description']
                    is_changed = True

                if obj.win_rate != stage_data['win_rate']:
                    obj.win_rate = stage_data['win_rate']
                    is_changed = True

                if obj.condition_datas != stage_data['condition_datas']:
                    obj.condition_datas = stage_data['condition_datas']
                    is_changed = True

                # Save if has changed
                if is_changed:
                    obj.save()
                for condition in stage_data['condition_datas']:
                    bulk_data.append(
                        StageCondition(
                            stage=obj,
                            condition_property_id=condition['condition_property']['id'],
                            comparison_operator=condition['comparison_operator'],
                            compare_data=condition['compare_data']
                        )
                    )
                del dict_data[stage.indicator]
        return bulk_data

    def update(self, instance, validated_data):
        # data default
        data = ConfigDefaultData.opportunity_config_stage_data
        dict_data = {item['indicator']: item for item in data}

        # stage need delete
        list_stage_delete = OpportunityConfigStage.objects.filter(company=instance, is_default=False)
        list_stage_delete.delete()

        # delete all condition of stage of company
        StageCondition.objects.filter(stage__company=instance).delete()

        # stage need update
        list_stage_update = OpportunityConfigStage.objects.filter(company=instance, is_default=True)
        bulk_data = []

        # update stage need update
        bulk_data = self.update_stage_default(list_stage_update, dict_data, bulk_data)

        bulk_data_stage = []

        # add again deleted default stage
        for _, value in dict_data.items():
            stage = OpportunityConfigStage(**value, company=instance)
            bulk_data_stage.append(stage)
            for condition in value['condition_datas']:
                bulk_data.append(
                    StageCondition(
                        stage=stage,
                        condition_property_id=condition['condition_property']['id'],
                        comparison_operator=condition['comparison_operator'],
                        compare_data=condition['compare_data']
                    )
                )

        OpportunityConfigStage.objects.bulk_create(bulk_data_stage)
        StageCondition.objects.bulk_create(bulk_data)
        return True

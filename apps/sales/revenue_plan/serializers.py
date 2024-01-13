from datetime import datetime
from rest_framework import serializers

from apps.masterdata.saledata.models import Periods
from apps.sales.revenue_plan.models import (
    RevenuePlanGroup, RevenuePlanGroupEmployee, RevenuePlan
)
from apps.shared import SaleMsg


class RevenuePlanListSerializer(serializers.ModelSerializer):
    period_mapped = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = RevenuePlan
        fields = (
            'id',
            'code',
            'title',
            'period_mapped',
            'employee_created',
            'date_created',
            'company_month_target',
            'company_quarter_target',
            'company_year_target',
        )

    @classmethod
    def get_period_mapped(cls, obj):
        return {
            'id': obj.period_mapped_id,
            'code': obj.period_mapped.code,
            'title': obj.period_mapped.title,
            'start_date': obj.period_mapped.start_date
        } if obj.period_mapped else {}

    @classmethod
    def get_employee_created(cls, obj):
        return {
            'id': obj.employee_created_id,
            'code': obj.employee_created.code,
            'full_name': obj.employee_created.get_full_name(2),
        } if obj.employee_created else {}


def create_revenue_plan_group(revenue_plan, revenue_plan_group_data):
    bulk_data = []
    for data in revenue_plan_group_data:
        bulk_data.append(RevenuePlanGroup(revenue_plan_mapped=revenue_plan, **data))
    RevenuePlanGroup.objects.filter(revenue_plan_mapped=revenue_plan).delete()
    RevenuePlanGroup.objects.bulk_create(bulk_data)
    return True


def create_revenue_plan_group_employee(revenue_plan, revenue_plan_group_employee_data):
    bulk_data = []
    for data in revenue_plan_group_employee_data:
        bulk_data.append(RevenuePlanGroupEmployee(
            revenue_plan_mapped=revenue_plan,
            **data
        ))
    RevenuePlanGroupEmployee.objects.filter(revenue_plan_mapped=revenue_plan).delete()
    RevenuePlanGroupEmployee.objects.bulk_create(bulk_data)
    return True


class RevenuePlanCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = RevenuePlan
        fields = (
            'title',
            'period_mapped',
            'group_mapped_list',
            'monthly',
            'quarterly',
            'auto_sum_target',
            'company_month_target',
            'company_quarter_target',
            'company_year_target'
        )

    def validate(self, validate_data):
        return validate_data

    def create(self, validated_data):
        period = validated_data.get('period_mapped')
        period_year = RevenuePlan.objects.all().count() + 1
        if period:
            period_year = datetime.strptime(str(period.start_date), "%Y-%m-%d").year
        revenue_plan = RevenuePlan.objects.create(**validated_data, code=f'RP{period_year}')
        create_revenue_plan_group(revenue_plan, self.initial_data.get('RevenuePlanGroup_data', []))
        create_revenue_plan_group_employee(revenue_plan, self.initial_data.get('RevenuePlanGroupEmployee_data', []))
        if period.planned is False:
            period.planned = True
            period.save(update_fields=['planned'])
        else:
            raise serializers.ValidationError({'Period': SaleMsg.PERIOD_HAS_PLAN})
        return revenue_plan


class RevenuePlanDetailSerializer(serializers.ModelSerializer):
    period_mapped = serializers.SerializerMethodField()
    revenue_plan_group_data = serializers.SerializerMethodField()

    class Meta:
        model = RevenuePlan
        fields = (
            'id',
            'code',
            'title',
            'period_mapped',
            'group_mapped_list',
            'monthly',
            'quarterly',
            'auto_sum_target',
            'company_month_target',
            'company_quarter_target',
            'company_year_target',
            'revenue_plan_group_data'
        )

    @classmethod
    def get_period_mapped(cls, obj):
        return {
            'id': obj.period_mapped_id,
            'code': obj.period_mapped.code,
            'title': obj.period_mapped.title,
            'start_date': obj.period_mapped.start_date
        } if obj.period_mapped else {}

    @classmethod
    def get_revenue_plan_group_data(cls, obj):
        revenue_plan_data = []
        group_data = obj.revenue_plan_mapped_group.all()
        employee_data = obj.revenue_plan_mapped_group_employee.all()
        for item in group_data:
            employee_data_filter_by_group = employee_data.filter(revenue_plan_group_mapped_id=item.group_mapped_id)
            revenue_plan_data.append({
                'group_mapped': {
                    'id': item.group_mapped_id,
                    'code': item.group_mapped.code,
                    'title': item.group_mapped.title
                } if item.group_mapped else {},
                'group_month_target': item.group_month_target,
                'group_quarter_target': item.group_quarter_target,
                'group_year_target': item.group_year_target,
                'employee_target_data': [{
                    'emp_month_target': data.emp_month_target,
                    'emp_quarter_target': data.emp_quarter_target,
                    'emp_year_target': data.emp_year_target,
                    'id': data.employee_mapped_id,
                    'code': data.employee_mapped.code,
                    'full_name': data.employee_mapped.get_full_name(2)
                } if data.employee_mapped else {} for data in employee_data_filter_by_group]
            })
        return revenue_plan_data


class RevenuePlanUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = RevenuePlan
        fields = (
            'title',
            'period_mapped',
            'group_mapped_list',
            'monthly',
            'quarterly',
            'auto_sum_target',
            'company_month_target',
            'company_quarter_target',
            'company_year_target'
        )

    def validate(self, validate_data):
        # if validate_data['period_mapped']:
        #     if validate_data['period_mapped'].start_date.year < datetime.now().year:
        #         raise serializers.ValidationError({'Period': SaleMsg.PERIOD_FINISHED})
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        create_revenue_plan_group(instance, self.initial_data.get('RevenuePlanGroup_data', []))
        create_revenue_plan_group_employee(instance, self.initial_data.get('RevenuePlanGroupEmployee_data', []))
        return instance

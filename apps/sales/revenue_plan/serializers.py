from datetime import datetime
from rest_framework import serializers
from apps.sales.revenue_plan.models import (
    RevenuePlanGroup, RevenuePlanGroupEmployee, RevenuePlan
)


class RevenuePlanListSerializer(serializers.ModelSerializer):
    period_mapped = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = RevenuePlan
        fields = '__all__'

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
        fields = '__all__'

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
        return revenue_plan


class RevenuePlanDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenuePlan
        fields = '__all__'


class RevenuePlanUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = RevenuePlan
        fields = '__all__'

    def validate(self, validate_data):
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

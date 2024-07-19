from datetime import datetime
from rest_framework import serializers
from apps.core.hr.models import Group
from apps.masterdata.saledata.models import Periods
from apps.sales.budgetplan.models import (
    BudgetPlan, BudgetPlanGroup, BudgetPlanCompanyExpense, BudgetPlanGroupExpense
)
from apps.shared import SaleMsg


class BudgetPlanListSerializer(serializers.ModelSerializer):
    period_mapped = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = BudgetPlan
        fields = (
            'id',
            'code',
            'title',
            'period_mapped',
            'employee_created',
            'date_created',
            'is_lock'
        )

    @classmethod
    def get_period_mapped(cls, obj):
        return {
            'id': obj.period_mapped_id,
            'code': obj.period_mapped.code,
            'title': obj.period_mapped.title,
            'start_date': obj.period_mapped.start_date,
            'fiscal_year': obj.period_mapped.fiscal_year,
            'space_month': obj.period_mapped.space_month
        } if obj.period_mapped else {}

    @classmethod
    def get_employee_created(cls, obj):
        return {
            'id': obj.employee_created_id,
            'code': obj.employee_created.code,
            'full_name': obj.employee_created.get_full_name(2),
        } if obj.employee_created else {}


class BudgetPlanCreateSerializer(serializers.ModelSerializer):
    period_mapped = serializers.UUIDField(required=True)

    class Meta:
        model = BudgetPlan
        fields = (
            'title',
            'period_mapped',
            'monthly',
            'quarterly',
            'auto_sum_target',
        )

    @classmethod
    def validate_period_mapped(cls, value):
        try:
            period_mapped = Periods.objects.get(id=value)
            if period_mapped.has_budget_planned is True:
                raise serializers.ValidationError({'Period': SaleMsg.PERIOD_HAS_PLAN})
            return period_mapped
        except Periods.DoesNotExist:
            raise serializers.ValidationError({'period': 'Periods obj is not exist.'})

    def validate(self, validate_data):
        return validate_data

    @classmethod
    def create_group_mapped(cls, budget_plan):
        bulk_info = []
        for item in Group.objects.filter(tenant=budget_plan.tenant, company=budget_plan.company):
            bulk_info.append(BudgetPlanGroup(budget_plan=budget_plan, group_mapped=item))
        BudgetPlanGroup.objects.bulk_create(bulk_info)
        return True

    def create(self, validated_data):
        period_mapped = validated_data['period_mapped']
        budget_plan = BudgetPlan.objects.create(
            **validated_data, code=f'BP{period_mapped.fiscal_year}', system_status=1
        )
        period_mapped.has_budget_planned = True
        period_mapped.save(update_fields=['has_budget_planned'])
        self.create_group_mapped(budget_plan)
        return budget_plan


class BudgetPlanDetailSerializer(serializers.ModelSerializer):
    period_mapped = serializers.SerializerMethodField()
    group_budget_data = serializers.SerializerMethodField()
    company_budget_data = serializers.SerializerMethodField()

    class Meta:
        model = BudgetPlan
        fields = (
            'id',
            'code',
            'title',
            'period_mapped',
            'monthly',
            'quarterly',
            'auto_sum_target',
            'group_budget_data',
            'company_budget_data'
        )

    @classmethod
    def get_period_mapped(cls, obj):
        return {
            'id': obj.period_mapped_id,
            'code': obj.period_mapped.code,
            'title': obj.period_mapped.title,
            'start_date': obj.period_mapped.start_date,
            'fiscal_year': obj.period_mapped.fiscal_year,
            'space_month': obj.period_mapped.space_month
        } if obj.period_mapped else {}

    @classmethod
    def get_group_budget_data(cls, obj):
        group_budget_data = []
        for item in obj.budget_plan_group_budget_plan.all():
            group_budget_data.append({
                'id': item.id,
                'group': {
                    'id': str(item.group_mapped_id),
                    'code': item.group_mapped.code,
                    'title': item.group_mapped.title,
                },
                'data_expense': [
                    {
                        'order': data.order,
                        'expense_item': {
                            'id': str(data.expense_item_id),
                            'code': data.expense_item.code,
                            'title': data.expense_item.title
                        } if data.expense_item else {},
                        'group_month_list': data.group_month_list,
                        'group_quarter_list': data.group_quarter_list,
                        'group_year': data.group_year
                    } for data in item.budget_plan_group_expense_budget_plan_group.all().order_by('order')
                ]
            })
        return group_budget_data

    @classmethod
    def get_company_budget_data(cls, obj):
        company_budget_data = []
        for item in obj.budget_plan_company_expense_budget_plan.all().order_by('order'):
            company_budget_data.append({
                'id': item.id,
                'order': item.order,
                'expense_item': {
                    'id': str(item.expense_item_id),
                    'code': item.expense_item.code,
                    'title': item.expense_item.title
                } if item.expense_item else {},
                'company_month_list': item.company_month_list,
                'company_quarter_list': item.company_quarter_list,
                'company_year': item.company_year
            })
        return company_budget_data


class BudgetPlanUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = BudgetPlan
        fields = ()

    @classmethod
    def create_new_budget_plan_group_expense(cls, instance, budget_plan_group, data_group_budget_plan):
        BudgetPlanGroupExpense.objects.filter(budget_plan_group=budget_plan_group).delete()
        print(BudgetPlanGroupExpense.objects.all().count())
        bulk_info = []
        for item in data_group_budget_plan:
            bulk_info.append(
                BudgetPlanGroupExpense(
                    budget_plan=instance, budget_plan_group=budget_plan_group, **item
                )
            )
        BudgetPlanGroupExpense.objects.bulk_create(bulk_info)
        return True

    @classmethod
    def create_new_budget_plan_company_expense(cls, instance):
        all_group_expense = BudgetPlanGroupExpense.objects.filter(budget_plan=instance)
        BudgetPlanCompanyExpense.objects.filter(budget_plan=instance).delete()
        print(BudgetPlanCompanyExpense.objects.all().count())
        existed_expense_id_list = []
        bulk_info = []
        order = 1
        for item in all_group_expense:
            if str(item.expense_item_id) not in existed_expense_id_list:
                bulk_info.append(
                    BudgetPlanCompanyExpense(
                        order=order,
                        budget_plan=instance,
                        expense_item=item.expense_item,
                        company_month_list=item.group_month_list,
                        company_quarter_list=item.group_quarter_list,
                        company_year=item.group_year
                    )
                )
                order += 1
            else:
                for data in bulk_info:
                    if str(data.expense_item_id) == str(item.expense_item_id):
                        data.company_month_list = [
                            float(mc) + float(mg) for mc, mg in zip(data.company_month_list, item.group_month_list)
                        ]
                        data.company_quarter_list = [
                            float(qc) + float(qg) for qc, qg in zip(data.company_quarter_list, item.group_quarter_list)
                        ]
                        data.company_year += item.group_year
            existed_expense_id_list.append(str(item.expense_item_id))
        BudgetPlanCompanyExpense.objects.bulk_create(bulk_info)
        return True

    def update(self, instance, validated_data):
        group_id = self.initial_data.get('group_id')
        data_group_budget_plan = self.initial_data.get('data_group_budget_plan')

        budget_plan_group = BudgetPlanGroup.objects.filter(budget_plan=instance, group_mapped_id=group_id).first()
        if budget_plan_group:
            self.create_new_budget_plan_group_expense(instance, budget_plan_group, data_group_budget_plan)
            self.create_new_budget_plan_company_expense(instance)
        return instance

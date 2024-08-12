from rest_framework import serializers

from apps.masterdata.saledata.models import Product, ExpenseItem, Account
from apps.sales.distribution_plan.models import (
    DistributionPlan,
    DistributionPlanSupplier,
    DistributionPlanFixedCost,
    DistributionPlanVariableCost
)


__all__ = [
    'DistributionPlanListSerializer',
    'DistributionPlanDetailSerializer',
    'DistributionPlanCreateSerializer',
    'DistributionPlanUpdateSerializer'
]


class DistributionPlanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionPlan
        fields = (
            'id',
            'code',
            'title',
            'start_date',
            'no_of_month',
            'system_status'
        )


class DistributionPlanCreateSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField(required=True)
    no_of_month = serializers.IntegerField(required=True)

    class Meta:
        model = DistributionPlan
        fields = (
            'title',
            'product',
            'start_date',
            'no_of_month',
            'product_price',
            'break_event_point',
            'expected_number',
            'net_income',
            'rate',
            'plan_description'
        )

    @classmethod
    def validate_product(cls, value):
        try:
            return Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': 'Product is not exist.'})

    @classmethod
    def validate_no_of_month(cls, value):
        if not value or value < 0:
            raise serializers.ValidationError({'product': 'Product is not exist.'})
        return value

    @classmethod
    def validate_supplier_list(cls, supplier_list):
        if len(supplier_list) == 0:
            raise serializers.ValidationError({'supplier_list': 'Supplier list is required.'})
        supplier_list_filter = Account.objects.filter(id__in=supplier_list)
        if supplier_list_filter.count() != len(supplier_list):
            raise serializers.ValidationError({'supplier_list': 'Supplier list is not valid.'})
        return supplier_list

    @classmethod
    def validate_fixed_cost_list(cls, fixed_cost_list):
        fixed_cost_list_filter = ExpenseItem.objects.filter(
            id__in=[expense_item.get('expense_item_id') for expense_item in fixed_cost_list]
        )
        if fixed_cost_list_filter.count() != len(fixed_cost_list):
            raise serializers.ValidationError({'fixed_cost_list': 'Fixed cost list is not valid.'})
        return fixed_cost_list

    @classmethod
    def validate_variable_cost_list(cls, variable_cost_list):
        variable_cost_list_filter = ExpenseItem.objects.filter(
            id__in=[expense_item.get('expense_item_id') for expense_item in variable_cost_list]
        )
        if variable_cost_list_filter.count() != len(variable_cost_list):
            raise serializers.ValidationError({'variable_cost_list': 'Variable cost list is not valid.'})
        return variable_cost_list

    def validate(self, validate_data):
        self.validate_supplier_list(self.initial_data.get('supplier_list', []))
        self.validate_fixed_cost_list(self.initial_data.get('fixed_cost_list', []))
        self.validate_variable_cost_list(self.initial_data.get('variable_cost_list', []))
        return validate_data

    # @decorator_run_workflow
    def create(self, validated_data):
        distribution_plan = DistributionPlan.objects.create(**validated_data)

        # create supplier mapped
        bulk_info_supplier = []
        for supplier_item in self.initial_data.get('supplier_list', []):
            bulk_info_supplier.append(
                DistributionPlanSupplier(distribution_plan=distribution_plan, supplier_id=supplier_item)
            )

        # create fixed cost mapped
        bulk_info_fixed_cost = []
        for fixed_cost_item in self.initial_data.get('fixed_cost_list', []):
            bulk_info_fixed_cost.append(
                DistributionPlanFixedCost(distribution_plan=distribution_plan, **fixed_cost_item)
            )

        # create variable cost mapped
        bulk_info_variable_cost = []
        for variable_cost_item in self.initial_data.get('variable_cost_list', []):
            bulk_info_variable_cost.append(
                DistributionPlanVariableCost(distribution_plan=distribution_plan, **variable_cost_item)
            )

        DistributionPlanSupplier.objects.bulk_create(bulk_info_supplier)
        DistributionPlanFixedCost.objects.bulk_create(bulk_info_fixed_cost)
        DistributionPlanVariableCost.objects.bulk_create(bulk_info_variable_cost)
        return distribution_plan


class DistributionPlanDetailSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    supplier_list = serializers.SerializerMethodField()
    fixed_cost_list = serializers.SerializerMethodField()
    variable_cost_list = serializers.SerializerMethodField()

    class Meta:
        model = DistributionPlan
        fields = (
            'id',
            'code',
            'title',
            'product',
            'start_date',
            'no_of_month',
            'product_price',
            'break_event_point',
            'expected_number',
            'net_income',
            'rate',
            'plan_description',
            'supplier_list',
            'fixed_cost_list',
            'variable_cost_list'
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': str(obj.product_id),
            'code': obj.product.code,
            'title': obj.product.title
        } if obj.product else {}

    @classmethod
    def get_supplier_list(cls, obj):
        supplier_list = []
        for item in obj.distribution_plan_supplier_distribution_plan.all():
            supplier_list.append({
                'id': str(item.supplier_id),
                'code': item.supplier.code,
                'name': item.supplier.name
            })
        return supplier_list

    @classmethod
    def get_fixed_cost_list(cls, obj):
        fixed_cost_list = []
        for item in obj.distribution_plan_fixed_cost_distribution_plan.all():
            fixed_cost_list.append({
                'expense_item': {
                    'id': str(item.expense_item_id),
                    'code': item.expense_item.code,
                    'title': item.expense_item.title,
                },
                'value': item.value,
                'order': item.order
            })
        return fixed_cost_list

    @classmethod
    def get_variable_cost_list(cls, obj):
        variable_cost_list = []
        for item in obj.distribution_plan_variable_cost_distribution_plan.all():
            variable_cost_list.append({
                'expense_item': {
                    'id': str(item.expense_item_id),
                    'code': item.expense_item.code,
                    'title': item.expense_item.title,
                },
                'value': item.value,
                'order': item.order
            })
        return variable_cost_list


class DistributionPlanUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionPlan
        fields = "__all__"

    def validate(self, validate_data):
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance

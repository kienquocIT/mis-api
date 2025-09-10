from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.masterdata.saledata.models import ExpenseItem, UnitOfMeasure, Tax, Product, Currency
from apps.sales.serviceorder.models import (
    ServiceOrderShipment, ServiceOrderExpense, ServiceOrderServiceDetail, ServiceOrderWorkOrder, ServiceOrderPayment,
)
from apps.shared import SVOMsg


__all__ = [
    'ServiceOrderServiceDetailSerializer',
    'ServiceOrderWorkOrderSerializer',
    'ServiceOrderShipmentSerializer',
    'ServiceOrderExpenseSerializer',
    'ServiceOrderPaymentSerializer'
]


# SERVICE DETAIL
class ServiceOrderServiceDetailSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField()
    uom = serializers.UUIDField(required=False, allow_null=True)
    tax = serializers.UUIDField(required=False, allow_null=True)
    id = serializers.CharField(required=False)

    class Meta:
        model = ServiceOrderServiceDetail
        fields = (
            'id',
            'product',
            'order',
            'code',
            'title',
            'description',
            'quantity',
            'uom',
            'uom_data',
            'price',
            'tax',
            'tax_data',
            'sub_total_value',
            'total_value',
            'delivery_balance_value',
            'total_contribution_percent',
            'total_payment_percent',
            'total_payment_value'
        )

    @classmethod
    def validate_product(cls, value):
        if value:
            try:
                product = Product.objects.get_on_company(id=value)
                return product
            except Product.DoesNotExist:
                raise serializers.ValidationError({'product': _('Product does not exist')})
        return None

    @classmethod
    def validate_uom(cls, value):
        if value:
            try:
                uom = UnitOfMeasure.objects.get_on_company(id=value)
                return uom
            except UnitOfMeasure.DoesNotExist:
                raise serializers.ValidationError({'uom': _('Unit of Measure does not exist')})
        raise serializers.ValidationError({'uom': _('Unit of Measure is required')})

    @classmethod
    def validate_tax(cls, value):
        if value:
            try:
                tax = Tax.objects.get_on_company(id=value)
                return tax
            except Tax.DoesNotExist:
                raise serializers.ValidationError({'tax': _('Tax does not exist')})
        raise serializers.ValidationError({'tax': _('Tax is required')})


# WORK ORDER
class ServiceOrderWorkOrderSerializer(serializers.ModelSerializer):
    product = serializers.UUIDField(allow_null=True, required=False)
    code = serializers.CharField(allow_blank=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    cost_data = serializers.JSONField()
    product_contribution = serializers.JSONField()

    class Meta:
        model = ServiceOrderWorkOrder
        fields = (
            'product',
            'order',
            'code',
            'title',
            'start_date',
            'end_date',
            'is_delivery_point',
            'quantity',
            'unit_cost',
            'total_value',
            'work_status',
            'cost_data',
            'product_contribution',
            'task_data',
        )

    @classmethod
    def validate_product(cls, value):
        if value:
            try:
                product = Product.objects.get_on_company(id=value)
                return product
            except Product.DoesNotExist:
                raise serializers.ValidationError({'product': _('Product does not exist')})
        return None

    @classmethod
    def validate_cost_data(cls, cost_data):
        for cost in cost_data:
            currency_id = cost.get('currency_id', None)
            if currency_id:
                try:
                    Currency.objects.get(id=currency_id)
                except Currency.DoesNotExist:
                    raise serializers.ValidationError(
                        {'work_order_cost': _('Currency of work order cost does not exist')}
                    )
            else:
                raise serializers.ValidationError({'work_order_cost': _('Currency of work order cost is missing')})

            tax_id = cost.get('tax_id', None)
            if tax_id:
                try:
                    Tax.objects.get(id=tax_id)
                except Tax.DoesNotExist:
                    raise serializers.ValidationError({'work_order_cost': _('Tax of work order cost does not exist')})
            else:
                raise serializers.ValidationError({'work_order_cost': _('Tax of work order cost is missing')})
        return cost_data


# SHIPMENT
class ServiceOrderShipmentSerializer(serializers.ModelSerializer):
    container_type = serializers.JSONField(required=False, allow_null=True)
    package_type = serializers.JSONField(required=False, allow_null=True)

    def validate(self, validate_data):
        if validate_data.get('is_container', True):
            if not validate_data.get('title'):
                raise serializers.ValidationError({'container name': SVOMsg.CONTAINER_NAME_NOT_EXIST})
            if not validate_data.get('reference_number'):
                raise serializers.ValidationError({'Container Reference Number': SVOMsg.CONTAINER_REF_NOT_EXIST})
        else:
            if not validate_data.get('title'):
                raise serializers.ValidationError({'Package Name': SVOMsg.PACKAGE_NAME_NOT_EXIST})
            if not validate_data.get('reference_container'):
                raise serializers.ValidationError({'Package Reference Container': SVOMsg.PACKAGE_REF_NOT_EXIST})

        return validate_data

    class Meta:
        model = ServiceOrderShipment
        fields = (
            'id',
            'code',
            'title',
            'order',
            'reference_number',
            'weight',
            'dimension',
            'description',
            'reference_container',
            'is_container',
            'container_type',
            'package_type'
        )


# EXPENSE
class ServiceOrderExpenseSerializer(serializers.ModelSerializer):
    expense_item = serializers.UUIDField()
    uom = serializers.UUIDField()
    tax = serializers.UUIDField(required=False, allow_null=True)

    @staticmethod
    def validate_expense_item(value):
        if not ExpenseItem.objects.filter(id=value).exists():
            raise serializers.ValidationError(SVOMsg.EXPENSE_ITEM_NOT_EXIST)
        return value

    @staticmethod
    def validate_uom(value):
        if not UnitOfMeasure.objects.filter(id=value).exists():
            raise serializers.ValidationError(SVOMsg.UOM_NOT_EXIST)
        return value

    @staticmethod
    def validate_tax(value):
        if value and not Tax.objects.filter(id=value).exists():
            raise serializers.ValidationError(SVOMsg.TAX_NOT_EXIST)
        return value

    class Meta:
        model = ServiceOrderExpense
        fields = (
            "id",
            "code",
            "title",
            "expense_item",
            "uom",
            "quantity",
            "expense_price",
            "tax",
            "subtotal_price",
        )


# PAYMENT
class ServiceOrderPaymentSerializer(serializers.ModelSerializer):
    payment_detail_data = serializers.JSONField(required=False)
    reconcile_data = serializers.JSONField()

    class Meta:
        model = ServiceOrderPayment
        fields = (
            'installment',
            'description',
            'payment_type',
            'is_invoice_required',
            'payment_value',
            'tax_value',
            'reconcile_value',
            'receivable_value',
            'due_date',
            'payment_detail_data',
            'reconcile_data'
        )

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account
from apps.sales.reconciliation.models import Reconciliation
from apps.shared import (
    AbstractListSerializerModel,
    AbstractCreateSerializerModel,
    AbstractDetailSerializerModel,
    ReconMsg
)


__all__ = [
    'ReconListSerializer',
    'ReconCreateSerializer',
    'ReconDetailSerializer',
    'ReconUpdateSerializer',
]


# main serializers
class ReconListSerializer(AbstractListSerializerModel):
    class Meta:
        model = Reconciliation
        fields = (
            'id',
            'code',
            'title',
            'customer_data',
            'system_status'
        )


class ReconCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    customer_id = serializers.UUIDField()
    posting_date = serializers.DateTimeField()
    document_date = serializers.DateTimeField()

    class Meta:
        model = Reconciliation
        fields = (
            'title',
            'customer_id',
            'posting_date',
            'document_date',
        )

    def validate(self, validate_data):
        ReconCommonFunction.validate_customer_id(validate_data)
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        cash_inflow_obj = Reconciliation.objects.create(**validated_data)
        return cash_inflow_obj


class ReconDetailSerializer(AbstractDetailSerializerModel):
    recon_items_data = serializers.SerializerMethodField()

    class Meta:
        model = Reconciliation
        fields = (
            'id',
            'code',
            'title',
            'posting_date',
            'document_date',
            'customer_data',
            'recon_items_data'
        )

    @classmethod
    def get_recon_items_data(cls, obj):
        return [{
            'id': item.id,
            'recon_data': item.recon_data,
            'order': item.order,
            'ar_invoice_data': item.ar_invoice_data,
            'cash_inflow_data': item.cash_inflow_data,
            'recon_balance': item.recon_balance,
            'recon_amount': item.recon_amount,
            'note': item.note,
            'accounting_account': item.accounting_account
        } for item in obj.recon_items.all()]


class ReconUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    customer_id = serializers.UUIDField()
    posting_date = serializers.DateTimeField()
    document_date = serializers.DateTimeField()

    class Meta:
        model = Reconciliation
        fields = (
            'title',
            'customer_id',
            'posting_date',
            'document_date',
        )

    def validate(self, validate_data):
        ReconCommonFunction.validate_customer_id(validate_data)
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class ReconCommonFunction:
    @classmethod
    def validate_customer_id(cls, validate_data):
        if 'customer_id' in validate_data:
            if validate_data.get('customer_id'):
                try:
                    customer = Account.objects.get(id=validate_data.get('customer_id'))
                    if not customer.is_customer_account:
                        raise serializers.ValidationError({'customer_id': ReconMsg.ACCOUNT_NOT_CUSTOMER})
                    validate_data['customer_id'] = str(customer.id)
                    validate_data['customer_data'] = {
                        'id': str(customer.id),
                        'code': customer.code,
                        'name': customer.name,
                        'tax_code': customer.tax_code,
                    }
                    print('1. validate_customer_id --- ok')
                    return validate_data
                except Account.DoesNotExist:
                    raise serializers.ValidationError({'customer_id': ReconMsg.CUSTOMER_NOT_EXIST})
        raise serializers.ValidationError({'customer_id': ReconMsg.CUSTOMER_NOT_NULL})

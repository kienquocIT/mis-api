import logging
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.accounting.accountingsettings.models import DefaultAccountDetermination
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account
from apps.sales.apinvoice.models import APInvoice
from apps.sales.arinvoice.models import ARInvoice
from apps.sales.financialcashflow.models import CashInflow, CashOutflow, CashOutflowItem, CashInflowItem
from apps.sales.reconciliation.models import Reconciliation, ReconciliationItem
from apps.shared import (
    ReconMsg, AbstractListSerializerModel, AbstractDetailSerializerModel,  AbstractCreateSerializerModel
)


logger = logging.getLogger(__name__)


__all__ = [
    'ReconListSerializer',
    'ReconCreateSerializer',
    'ReconDetailSerializer',
    'APInvoiceListForReconSerializer',
    'CashOutflowListForReconSerializer',
    'ARInvoiceListForReconSerializer',
    'CashInflowListForReconSerializer',
]

# main serializers
class ReconListSerializer(AbstractListSerializerModel):
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = Reconciliation
        fields = (
            'id',
            'code',
            'title',
            'business_partner_data',
            'date_created',
            'employee_created',
            'system_status',
            'system_auto_create',
        )

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}


class ReconCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    business_partner = serializers.UUIDField(allow_null=True)
    recon_item_data = serializers.JSONField(default=list)

    class Meta:
        model = Reconciliation
        fields = (
            'title',
            'business_partner',
            'posting_date',
            'document_date',
            'recon_type',
            'recon_item_data'
        )

    @classmethod
    def validate_business_partner(cls, value):
        if value:
            try:
                return Account.objects.get(id=value)
            except Account.DoesNotExist:
                raise serializers.ValidationError({'business_partner': ReconMsg.CUSTOMER_NOT_EXIST})
        return None

    def validate(self, validate_data):
        tenant_id = self.context.get('tenant_id', None)
        company_id = self.context.get('company_id', None)
        ReconCommonFunction.common_validate(tenant_id, company_id, validate_data)
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        recon_item_data = validated_data.pop('recon_item_data')

        recon_obj = Reconciliation.objects.create(**validated_data)

        ReconCommonFunction.create_recon_item(recon_obj, recon_item_data)

        return recon_obj


class ReconDetailSerializer(AbstractDetailSerializerModel):
    recon_items_data = serializers.SerializerMethodField()

    class Meta:
        model = Reconciliation
        fields = (
            'id',
            'code',
            'title',
            'recon_type',
            'posting_date',
            'document_date',
            'business_partner_data',
            'recon_items_data',
            'system_status',
            'system_auto_create',
        )

    @classmethod
    def get_recon_items_data(cls, obj):
        return [{
            'id': item.id,
            'recon_data': item.recon_data,
            'order': item.order,
            'debit_doc_id': item.debit_doc_id,
            'debit_app_code': item.debit_app_code,
            'debit_doc_data': item.debit_doc_data,
            'debit_account_data': item.debit_account_data,
            'credit_doc_id': item.credit_doc_id,
            'credit_app_code': item.credit_app_code,
            'credit_doc_data': item.credit_doc_data,
            'credit_account_data': item.credit_account_data,
            'recon_total': item.recon_total,
            'recon_balance': item.recon_balance,
            'recon_amount': item.recon_amount,
            'note': item.note,
        } for item in obj.recon_items.all()]


class ReconUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    business_partner = serializers.UUIDField(allow_null=True)
    recon_item_data = serializers.JSONField(default=list)

    class Meta:
        model = Reconciliation
        fields = (
            'title',
            'business_partner',
            'posting_date',
            'document_date',
            'recon_type',
            'recon_item_data'
        )

    @classmethod
    def validate_business_partner(cls, value):
        return ReconCreateSerializer.validate_business_partner(value)

    def validate(self, validate_data):
        tenant_id = self.context.get('tenant_id', None)
        company_id = self.context.get('company_id', None)
        ReconCommonFunction.common_validate(tenant_id, company_id, validate_data)
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        recon_item_data = validated_data.pop('recon_item_data')

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        ReconCommonFunction.create_recon_item(instance, recon_item_data)

        return instance


class ReconCommonFunction:
    @staticmethod
    def create_recon_item(recon_obj, recon_item_data):
        bulk_info = []
        for order, item in enumerate(recon_item_data):
            bulk_info.append(ReconciliationItem(
                recon=recon_obj,
                recon_data={
                    'id': str(recon_obj.id),
                    'code': recon_obj.code,
                    'title': recon_obj.title
                },
                order=order,
                **item
            ))
        ReconciliationItem.objects.filter(recon=recon_obj).delete()
        ReconciliationItem.objects.bulk_create(bulk_info)
        return True

    @staticmethod
    def sub_validate_recon_type_0(tenant_id, company_id, recon_item_data):
        for item in recon_item_data:
            if item.get('credit_doc_id'):
                ar_invoice_obj = ARInvoice.objects.filter(id=item.get('credit_doc_id')).first()
                if ar_invoice_obj:
                    item['credit_app_code'] = ar_invoice_obj.get_model_code()
                    item['credit_doc_data'] = {
                        'id': str(ar_invoice_obj.id),
                        'code': ar_invoice_obj.code,
                        'title': ar_invoice_obj.title,
                        'document_date': str(ar_invoice_obj.document_date),
                        'posting_date': str(ar_invoice_obj.posting_date),
                        'app_code': ar_invoice_obj.get_model_code()
                    }
            if item.get('debit_doc_id'):
                cif_obj = CashInflow.objects.filter(id=item.get('debit_doc_id')).first()
                if cif_obj:
                    item['debit_app_code'] = cif_obj.get_model_code()
                    item['debit_doc_data'] = {
                        'id': str(cif_obj.id),
                        'code': cif_obj.code,
                        'title': cif_obj.title,
                        'document_date': str(cif_obj.document_date),
                        'posting_date': str(cif_obj.posting_date),
                        'app_code': cif_obj.get_model_code()
                    }
            # get debit & credit account obj
            account_list = DefaultAccountDetermination.get_default_account_deter_sub_data(
                tenant_id=tenant_id,
                company_id=company_id,
                foreign_title='Receivables from customers'
            )
            if len(account_list) == 1:
                item['credit_account_id'] = str(account_list[0].id)
                item['credit_account_data'] = {
                    'id': str(account_list[0].id),
                    'acc_code': account_list[0].acc_code,
                    'acc_name': account_list[0].acc_name,
                    'foreign_acc_name': account_list[0].foreign_acc_name
                }
                item['debit_account_id'] = str(account_list[0].id)
                item['debit_account_data'] = {
                    'id': str(account_list[0].id),
                    'acc_code': account_list[0].acc_code,
                    'acc_name': account_list[0].acc_name,
                    'foreign_acc_name': account_list[0].foreign_acc_name
                }
            else:
                logger.error(msg='No debit account has found.')
        return True

    @staticmethod
    def sub_validate_recon_type_1(tenant_id, company_id, recon_item_data):
        for item in recon_item_data:
            if item.get('credit_doc_id'):
                ap_invoice_obj = APInvoice.objects.filter(id=item.get('credit_doc_id')).first()
                if ap_invoice_obj:
                    item['credit_app_code'] = ap_invoice_obj.get_model_code()
                    item['credit_doc_data'] = {
                        'id': str(ap_invoice_obj.id),
                        'code': ap_invoice_obj.code,
                        'title': ap_invoice_obj.title,
                        'document_date': str(ap_invoice_obj.document_date),
                        'posting_date': str(ap_invoice_obj.posting_date),
                        'app_code': ap_invoice_obj.get_model_code()
                    }
            if item.get('debit_doc_id'):
                cof_obj = CashOutflow.objects.filter(id=item.get('debit_doc_id')).first()
                if cof_obj:
                    item['debit_app_code'] = cof_obj.get_model_code()
                    item['debit_doc_data'] = {
                        'id': str(cof_obj.id),
                        'code': cof_obj.code,
                        'title': cof_obj.title,
                        'document_date': str(cof_obj.document_date),
                        'posting_date': str(cof_obj.posting_date),
                        'app_code': cof_obj.get_model_code()
                    }
            # get debit & credit account obj
            account_list = DefaultAccountDetermination.get_default_account_deter_sub_data(
                tenant_id=tenant_id,
                company_id=company_id,
                foreign_title='Payable to suppliers'
            )
            if len(account_list) == 1:
                item['credit_account_id'] = str(account_list[0].id)
                item['credit_account_data'] = {
                    'id': str(account_list[0].id),
                    'acc_code': account_list[0].acc_code,
                    'acc_name': account_list[0].acc_name,
                    'foreign_acc_name': account_list[0].foreign_acc_name
                }
                item['debit_account_id'] = str(account_list[0].id)
                item['debit_account_data'] = {
                    'id': str(account_list[0].id),
                    'acc_code': account_list[0].acc_code,
                    'acc_name': account_list[0].acc_name,
                    'foreign_acc_name': account_list[0].foreign_acc_name
                }
            else:
                logger.error(msg='No debit account has found.')
        return True

    @staticmethod
    def common_validate(tenant_id, company_id, validate_data):
        business_partner_obj = validate_data.get('business_partner')
        if business_partner_obj:
            if not business_partner_obj.is_customer_account and validate_data.get('recon_type') == 0:
                raise serializers.ValidationError({'business_partner': ReconMsg.ACCOUNT_NOT_CUSTOMER})
            if not business_partner_obj.is_supplier_account and validate_data.get('recon_type') == 1:
                raise serializers.ValidationError({'business_partner': ReconMsg.ACCOUNT_NOT_SUPPLIER})
            validate_data['business_partner_data'] = {
                'id': str(business_partner_obj.id),
                'code': business_partner_obj.code,
                'name': business_partner_obj.name,
                'tax_code': business_partner_obj.tax_code,
            } if business_partner_obj else {}

        recon_item_data = validate_data.get('recon_item_data', [])
        if validate_data.get('recon_type') == 0:
            ReconCommonFunction.sub_validate_recon_type_0(tenant_id, company_id, recon_item_data)
        elif validate_data.get('recon_type') == 1:
            ReconCommonFunction.sub_validate_recon_type_1(tenant_id, company_id, recon_item_data)
        return validate_data

# related features
class APInvoiceListForReconSerializer(serializers.ModelSerializer):
    credit_doc_id = serializers.SerializerMethodField()
    credit_app_code = serializers.SerializerMethodField()
    credit_doc_data = serializers.SerializerMethodField()
    recon_total = serializers.SerializerMethodField()
    sum_recon_amount = serializers.SerializerMethodField()

    class Meta:
        model = APInvoice
        fields = (
            'credit_doc_id',
            'credit_app_code',
            'credit_doc_data',
            'recon_total',
            'sum_recon_amount'
        )

    @classmethod
    def get_credit_doc_id(cls, obj):
        return obj.id if obj else ''

    @classmethod
    def get_credit_app_code(cls, obj):
        return obj.get_model_code() if obj else ''

    @classmethod
    def get_credit_doc_data(cls, obj):
        return {
            "id": obj.id,
            "code": obj.code,
            "title": obj.title,
            "posting_date": obj.posting_date,
            "document_date": obj.document_date,
            "app_code": obj.get_model_code()
        } if obj else {}

    @classmethod
    def get_recon_total(cls, obj):
        return sum(item.product_subtotal_final for item in obj.ap_invoice_items.all())

    @classmethod
    def get_sum_recon_amount(cls, obj):
        sum_recon_amount = sum(item.sum_payment_value for item in CashOutflowItem.objects.filter(
            cash_outflow__supplier_id=str(obj.supplier_mapped_id),
            has_ap_invoice=True,
            ap_invoice_id=str(obj.id)
        ))
        return sum_recon_amount


class CashOutflowListForReconSerializer(serializers.ModelSerializer):
    debit_doc_id = serializers.SerializerMethodField()
    debit_app_code = serializers.SerializerMethodField()
    debit_doc_data = serializers.SerializerMethodField()
    recon_total = serializers.SerializerMethodField()
    sum_recon_amount = serializers.SerializerMethodField()

    class Meta:
        model = CashOutflow
        fields = (
            'debit_doc_id',
            'debit_app_code',
            'debit_doc_data',
            'recon_total',
            'sum_recon_amount'
        )

    @classmethod
    def get_debit_doc_id(cls, obj):
        return obj.id if obj else ''

    @classmethod
    def get_debit_app_code(cls, obj):
        return obj.get_model_code() if obj else ''

    @classmethod
    def get_debit_doc_data(cls, obj):
        return {
            "id": obj.id,
            "code": obj.code,
            "title": obj.title,
            "posting_date": obj.posting_date,
            "document_date": obj.document_date,
            "app_code": obj.get_model_code()
        } if obj else {}

    @classmethod
    def get_recon_total(cls, obj):
        return obj.total_value

    @classmethod
    def get_sum_recon_amount(cls, obj):
        sum_recon_amount = sum(item.recon_amount for item in ReconciliationItem.objects.filter(
            recon__business_partner_id=str(obj.supplier_id) or str(obj.customer_id),
            debit_doc_id=str(obj.id)
        ))
        return sum_recon_amount


class ARInvoiceListForReconSerializer(serializers.ModelSerializer):
    debit_doc_id = serializers.SerializerMethodField()
    debit_app_code = serializers.SerializerMethodField()
    debit_doc_data = serializers.SerializerMethodField()
    recon_total = serializers.SerializerMethodField()
    sum_recon_amount = serializers.SerializerMethodField()

    class Meta:
        model = ARInvoice
        fields = (
            'debit_doc_id',
            'debit_app_code',
            'debit_doc_data',
            'recon_total',
            'sum_recon_amount'
        )

    @classmethod
    def get_debit_doc_id(cls, obj):
        return obj.id if obj else ''

    @classmethod
    def get_debit_app_code(cls, obj):
        return obj.get_model_code() if obj else ''

    @classmethod
    def get_debit_doc_data(cls, obj):
        return {
            "id": obj.id,
            "code": obj.code,
            "title": obj.title,
            "posting_date": obj.posting_date,
            "document_date": obj.document_date,
            "app_code": obj.get_model_code()
        } if obj else {}

    @classmethod
    def get_recon_total(cls, obj):
        return sum(item.product_subtotal_final for item in obj.ar_invoice_items.all())

    @classmethod
    def get_sum_recon_amount(cls, obj):
        sum_recon_amount = sum(item.sum_payment_value for item in CashInflowItem.objects.filter(
            cash_inflow__customer_id=str(obj.customer_mapped_id),
            has_ar_invoice=True,
            ar_invoice_id=str(obj.id)
        ))
        return sum_recon_amount


class CashInflowListForReconSerializer(serializers.ModelSerializer):
    credit_doc_id = serializers.SerializerMethodField()
    credit_app_code = serializers.SerializerMethodField()
    credit_doc_data = serializers.SerializerMethodField()
    recon_total = serializers.SerializerMethodField()
    sum_recon_amount = serializers.SerializerMethodField()

    class Meta:
        model = CashInflow
        fields = (
            'credit_doc_id',
            'credit_app_code',
            'credit_doc_data',
            'recon_total',
            'sum_recon_amount'
        )

    @classmethod
    def get_credit_doc_id(cls, obj):
        return obj.id if obj else ''

    @classmethod
    def get_credit_app_code(cls, obj):
        return obj.get_model_code() if obj else ''

    @classmethod
    def get_credit_doc_data(cls, obj):
        return {
            "id": obj.id,
            "code": obj.code,
            "title": obj.title,
            "posting_date": obj.posting_date,
            "document_date": obj.document_date,
            "app_code": obj.get_model_code()
        } if obj else {}

    @classmethod
    def get_recon_total(cls, obj):
        return obj.total_value

    @classmethod
    def get_sum_recon_amount(cls, obj):
        sum_recon_amount = sum(item.recon_amount for item in ReconciliationItem.objects.filter(
            recon__business_partner_id=str(obj.customer_id),
            credit_doc_id=str(obj.id)
        ))
        return sum_recon_amount

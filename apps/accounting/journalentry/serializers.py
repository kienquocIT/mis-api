from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.accounting.journalentry.models import JournalEntry


class JournalEntryListSerializer(serializers.ModelSerializer):
    employee_created = serializers.SerializerMethodField()
    original_transaction = serializers.SerializerMethodField()

    class Meta:
        model = JournalEntry
        fields = (
            'id',
            'code',
            'je_transaction_data',
            'original_transaction',
            'date_created',
            'employee_created',
            'system_status',
            'system_auto_create'
        )

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}

    @classmethod
    def get_original_transaction(cls, obj):
        return {
            'delivery.orderdeliverysub': _('Delivery'),
            'arinvoice.arinvoice': _('AR Invoice'),
            'financialcashflow.cashinflow': _('Cash Inflow'),
            'inventory.goodsreceipt': _('Goods Receipt'),
            'apinvoice.apinvoice': _('AP Invoice'),
            'financialcashflow.cashoutflow': _('Cash Outflow'),
        }.get(obj.je_transaction_app_code, '')


class JournalEntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = "__all__"


class JournalEntryDetailSerializer(serializers.ModelSerializer):
    original_transaction = serializers.SerializerMethodField()
    je_items = serializers.SerializerMethodField()

    class Meta:
        model = JournalEntry
        fields = (
            'id',
            'code',
            'je_transaction_data',
            'system_auto_create',
            'je_posting_date',
            'je_document_date',
            'original_transaction',
            'je_items',
            'system_status',
            'system_auto_create'
        )

    @classmethod
    def get_original_transaction(cls, obj):
        return {
            'delivery.orderdeliverysub': 0,
            'arinvoice.arinvoice': 1,
            'financialcashflow.cashinflow': 2,
            'inventory.goodsreceipt': 3,
            'apinvoice.apinvoice': 4,
            'financialcashflow.cashoutflow': 5,
        }.get(obj.je_transaction_app_code, None)

    @classmethod
    def get_je_items(cls, obj):
        je_items = []
        for item in obj.je_items.all():
            je_items.append({
                'id': item.id,
                'order': item.order,
                'account_data': item.account_data,
                'business_partner_data': item.business_partner_data,
                'debit': item.debit,
                'credit': item.credit,
                'is_fc': item.is_fc,
                'je_item_type': item.je_item_type,
                'taxable_value': item.taxable_value,
            })
        return je_items


class JournalEntryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = "__all__"

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.accounting.journalentry.models import JournalEntry


class JournalEntryListSerializer(serializers.ModelSerializer):
    original_transaction = serializers.SerializerMethodField()

    class Meta:
        model = JournalEntry
        fields = (
            'id',
            'code',
            'je_transaction_data',
            'original_transaction',
            'system_auto_create'
        )

    @classmethod
    def get_original_transaction(cls, obj):
        if obj.je_transaction_app_code == 'delivery.orderdeliverysub':
            return _('Delivery')
        if obj.je_transaction_app_code == 'arinvoice.arinvoice':
            return _('AR Invoice')
        if obj.je_transaction_app_code == 'financialcashflow.cashinflow':
            return _('Cash Inflow')
        return ''


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
            'je_items'
        )

    @classmethod
    def get_original_transaction(cls, obj):
        if obj.je_transaction_app_code == 'delivery.orderdeliverysub':
            return 0
        if obj.je_transaction_app_code == 'arinvoice.arinvoice':
            return 1
        if obj.je_transaction_app_code == 'financialcashflow.cashinflow':
            return 2
        return None

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

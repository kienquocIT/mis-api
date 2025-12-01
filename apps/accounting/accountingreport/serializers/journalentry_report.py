from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from apps.accounting.journalentry.models import JournalEntryLine


class JournalEntryLineListSerializer(serializers.ModelSerializer):
    journal_entry_info = serializers.SerializerMethodField()
    je_line_type_parsed = serializers.SerializerMethodField()
    dimensions = serializers.SerializerMethodField()

    class Meta:
        model = JournalEntryLine
        fields = (
            'id',
            'journal_entry',
            'journal_entry_info',
            'order',
            'account',
            'account_data',
            'je_line_type',
            'je_line_type_parsed',
            'product_mapped',
            'product_mapped_data',
            'business_partner',
            'business_partner_data',
            'business_employee',
            'business_employee_data',
            'debit',
            'credit',
            'is_fc',
            'currency_mapped',
            'currency_mapped_data',
            'taxable_value',
            'use_for_recon',
            'use_for_recon_type',
            'dimensions',
        )

    @classmethod
    def get_journal_entry_info(cls, obj):
        je = obj.journal_entry_info
        return {
            'id': je.id,
            'code': je.code,
            'je_transaction_app_code': je.je_transaction_app_code,
            'je_transaction_data': je.je_transaction_data,
            'je_posting_date': je.je_posting_date,
            'je_document_date': je.je_document_date,
            'je_state': je.je_state,
            'je_state_parsed': [_('Draft'), _('Posted'), _('Reversed')][je.je_state],
            'total_debit': je.total_debit,
            'total_credit': je.total_credit,
            'system_status': je.system_status,
            'system_auto_create': je.system_auto_create,
            'date_created': je.date_created,
        }

    @classmethod
    def get_je_line_type_parsed(cls, obj):
        return 'Debit' if obj.je_line_type == 'Debit' else 'Credit'

    @classmethod
    def get_dimensions(cls, obj):
        return [
            obj.business_partner_data,
            obj.business_partner_data,
            obj.product_mapped_data,
        ]

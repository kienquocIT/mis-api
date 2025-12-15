from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from apps.accounting.accountingsettings.models import JE_DOCUMENT_TYPE_APP
from apps.accounting.journalentry.models import JournalEntryLine


class JournalEntryLineListSerializer(serializers.ModelSerializer):
    journal_entry_info = serializers.SerializerMethodField()

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
            'use_for_recon_type'
        )

    @classmethod
    def get_journal_entry_info(cls, obj):
        je_obj = obj.journal_entry
        return {
            'id': je_obj.id,
            'code': je_obj.code,
            'je_transaction_app_code': je_obj.je_transaction_app_code,
            'je_transaction_data': je_obj.je_transaction_data,
            'original_transaction_parsed': dict(JE_DOCUMENT_TYPE_APP).get(je_obj.je_transaction_app_code),
            'je_posting_date': je_obj.je_posting_date,
            'je_document_date': je_obj.je_document_date,
            'je_state': je_obj.je_state,
            'je_state_parsed': [_('Draft'), _('Posted'), _('Reversed')][je_obj.je_state],
            'total_debit': je_obj.total_debit,
            'total_credit': je_obj.total_credit,
            'system_status': je_obj.system_status,
            'system_auto_create': je_obj.system_auto_create,
            'date_created': je_obj.date_created,
            'employee_created': je_obj.employee_created.get_detail_with_group() if je_obj.employee_created else {},
        } if je_obj else {}

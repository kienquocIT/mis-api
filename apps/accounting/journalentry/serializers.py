from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.accounting.journalentry.models import (
    JournalEntry, JournalEntryLine, JE_ALLOWED_APP,
    AllowedAppAutoJournalEntry,
)


class AllowedAppAutoJEListSerializer(serializers.ModelSerializer):
    app_code_parsed = serializers.SerializerMethodField()

    class Meta:
        model = AllowedAppAutoJournalEntry
        fields = (
            'id',
            'app_code',
            'app_code_parsed',
            'is_auto_je',
        )

    @classmethod
    def get_app_code_parsed(cls, obj):
        return JE_ALLOWED_APP[obj.app_code]


class AllowedAppAutoJEUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedAppAutoJournalEntry
        fields = ('is_auto_je',)


# JE
class JournalEntryListSerializer(serializers.ModelSerializer):
    employee_created = serializers.SerializerMethodField()
    original_transaction_parsed = serializers.SerializerMethodField()
    je_state_parsed = serializers.SerializerMethodField()
    # je_lines = serializers.SerializerMethodField()

    class Meta:
        model = JournalEntry
        fields = (
            'id',
            'code',
            'je_transaction_data',
            'original_transaction_parsed',
            'total_debit',
            'total_credit',
            'je_state',
            'je_state_parsed',
            'date_created',
            'employee_created',
            'system_status',
            'system_auto_create',
            # 'je_lines'
        )

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}

    @classmethod
    def get_original_transaction_parsed(cls, obj):
        return JE_ALLOWED_APP.get(obj.je_transaction_app_code, '')

    @classmethod
    def get_je_state_parsed(cls, obj):
        return [_('Draft'), _('Posted'), _('Reversed')][obj.je_state]

    # @classmethod
    # def get_je_lines(cls, obj):
    #     je_lines = []
    #     for item in obj.je_lines.all():
    #         je_lines.append(
    #             {
    #                 'id': item.id,
    #                 'order': item.order,
    #                 'account_data': item.account_data,
    #                 'business_partner_data': item.business_partner_data,
    #                 'debit': item.debit,
    #                 'credit': item.credit,
    #                 'is_fc': item.is_fc,
    #                 'je_line_type': item.je_line_type,
    #                 'taxable_value': item.taxable_value,
    #                 'dimensions': [item.business_partner_data]
    #             }
    #         )
    #     return je_lines


class JournalEntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = "__all__"


class JournalEntryDetailSerializer(serializers.ModelSerializer):
    original_transaction_parsed = serializers.SerializerMethodField()
    je_lines = serializers.SerializerMethodField()

    class Meta:
        model = JournalEntry
        fields = (
            'id',
            'code',
            'je_transaction_data',
            'system_auto_create',
            'je_posting_date',
            'je_document_date',
            'original_transaction_parsed',
            'je_state',
            'total_debit',
            'total_credit',
            'je_lines',
            'system_status',
            'system_auto_create'
        )

    @classmethod
    def get_original_transaction_parsed(cls, obj):
        return JE_ALLOWED_APP.get(obj.je_transaction_app_code, '')

    @classmethod
    def get_je_lines(cls, obj):
        je_lines = []
        for item in obj.je_lines.all():
            je_lines.append(
                {
                    'id': item.id,
                    'order': item.order,
                    'account_data': item.account_data,
                    'business_partner_data': item.business_partner_data,
                    'debit': item.debit,
                    'credit': item.credit,
                    'is_fc': item.is_fc,
                    'je_line_type': item.je_line_type,
                    'taxable_value': item.taxable_value,
                    'dimensions': [item.business_partner_data]
                }
            )
        return je_lines


class JournalEntryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = "__all__"


# ====================== Journal Entry Line ================
class JournalEntryLineListSerializer(serializers.ModelSerializer):

    class Meta:
        model = JournalEntryLine
        fields = (
            'id',
            'order',
            'account',
            'account_data',
            'je_line_type',
            'business_partner',
            'business_partner_data',
            'business_employee',
            'business_employee_data',
            'debit',
            'credit',
            'date_created',
        )

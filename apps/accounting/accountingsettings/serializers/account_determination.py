from rest_framework import serializers
from apps.accounting.accountingsettings.models.account_determination import (
    DOCUMENT_TYPE_CHOICES, JEDocumentType, JE_DOCUMENT_TYPE_APP, JEPostingRule,
)


class JEDocumentTypeListSerializer(serializers.ModelSerializer):
    module_parsed = serializers.SerializerMethodField()
    app_code_parsed = serializers.SerializerMethodField()

    class Meta:
        model = JEDocumentType
        fields = (
            'id',
            'code',
            'title',
            'module',
            'module_parsed',
            'app_code',
            'app_code_parsed',
            'is_auto_je',
        )

    @classmethod
    def get_module_parsed(cls, obj):
        return dict(DOCUMENT_TYPE_CHOICES)[obj.module]

    @classmethod
    def get_app_code_parsed(cls, obj):
        return dict(JE_DOCUMENT_TYPE_APP)[obj.app_code]


class JEDocumentTypeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JEDocumentType
        fields = ('is_auto_je',)


class JEPostingRuleListSerializer(serializers.ModelSerializer):
    document_type_code = serializers.SerializerMethodField()
    document_type_app_code_parsed = serializers.SerializerMethodField()
    fixed_account = serializers.SerializerMethodField()

    class Meta:
        model = JEPostingRule
        fields = (
            'id',
            'code',
            'title',
            'document_type_code',
            'document_type_app_code_parsed',
            'rule_level',
            # Ưu tiên
            'priority',
            # Role là gì
            'role_key',
            # Bên Nợ hay Có
            'side',
            # Lấy tiền từ nguồn nào (field trong model)
            'amount_source',
            # Chọn tài khoản từ đâu (cứng hay động)
            'account_source_type',
            # CASE A: Cứng
            'fixed_account',
            # Field bổ sung
            'description',
            'example',
            'is_active'
        )

    @classmethod
    def get_document_type_code(cls, obj):
        return obj.je_document_type.code

    @classmethod
    def get_document_type_app_code_parsed(cls, obj):
        return dict(JE_DOCUMENT_TYPE_APP)[obj.je_document_type.app_code]

    @classmethod
    def get_fixed_account(cls, obj):
        return {
            'id': str(obj.fixed_account.id),
            'acc_code': obj.fixed_account.acc_code,
            'acc_name': obj.fixed_account.acc_name,
            'foreign_acc_name': obj.fixed_account.foreign_acc_name,
        } if obj.fixed_account else {}

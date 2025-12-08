from rest_framework import serializers
from apps.accounting.accountingsettings.models.account_determination import (
    JEDocumentType, JEPostingRule, JEPostingGroup, JEGroupAssignment, JEGLAccountMapping,
    JE_DOCUMENT_TYPE_APP, DOCUMENT_TYPE_CHOICES, ASSIGNMENT_APP_CHOICES, GROUP_TYPE_CHOICES, ROLE_KEY_CHOICES,
    AMOUNT_SOURCE_CHOICES, RULE_LEVEL_CHOICES, SIDE_CHOICES,
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
    fixed_account_data = serializers.SerializerMethodField()
    rule_level_parsed = serializers.SerializerMethodField()
    role_key_parsed = serializers.SerializerMethodField()
    side_parsed = serializers.SerializerMethodField()
    amount_source_parsed = serializers.SerializerMethodField()

    class Meta:
        model = JEPostingRule
        fields = (
            'id',
            'code',
            'title',
            'document_type_code',
            'document_type_app_code_parsed',
            'rule_level',
            'rule_level_parsed',
            # Ưu tiên
            'priority',
            # Role là gì
            'role_key',
            'role_key_parsed',
            # Bên Nợ hay Có
            'side',
            'side_parsed',
            # Lấy tiền từ nguồn nào (field trong model)
            'amount_source',
            'amount_source_parsed',
            # Chọn tài khoản từ đâu (cứng hay động)
            'account_source_type',
            # CASE A: Cứng
            'fixed_account_data',
            # Field bổ sung
            'description',
            'example',
            'is_active'
        )

    @classmethod
    def get_rule_level_parsed(cls, obj):
        return dict(RULE_LEVEL_CHOICES)[obj.rule_level]

    @classmethod
    def get_role_key_parsed(cls, obj):
        return dict(ROLE_KEY_CHOICES)[obj.role_key]

    @classmethod
    def get_side_parsed(cls, obj):
        return dict(SIDE_CHOICES)[obj.side]

    @classmethod
    def get_amount_source_parsed(cls, obj):
        return dict(AMOUNT_SOURCE_CHOICES)[obj.amount_source]

    @classmethod
    def get_document_type_code(cls, obj):
        return obj.je_document_type.code

    @classmethod
    def get_document_type_app_code_parsed(cls, obj):
        return dict(JE_DOCUMENT_TYPE_APP)[obj.je_document_type.app_code]

    @classmethod
    def get_fixed_account_data(cls, obj):
        return {
            'id': str(obj.fixed_account.id),
            'acc_code': obj.fixed_account.acc_code,
            'acc_name': obj.fixed_account.acc_name,
            'foreign_acc_name': obj.fixed_account.foreign_acc_name,
        } if obj.fixed_account else {}


class JEPostingGroupListSerializer(serializers.ModelSerializer):
    posting_group_type_parsed = serializers.SerializerMethodField()

    class Meta:
        model = JEPostingGroup
        fields = (
            'id',
            'code',
            'title',
            'posting_group_type',
            'posting_group_type_parsed',
            'is_active'
        )

    @classmethod
    def get_posting_group_type_parsed(cls, obj):
        return dict(GROUP_TYPE_CHOICES)[obj.posting_group_type]


class JEGroupAssignmentListSerializer(serializers.ModelSerializer):
    item_app_parsed = serializers.SerializerMethodField()
    posting_group = serializers.SerializerMethodField()
    posting_group_type_parsed = serializers.SerializerMethodField()

    class Meta:
        model = JEGroupAssignment
        fields = (
            'id',
            'item_app',
            'item_app_parsed',
            'item_app_data',
            'posting_group',
            'posting_group_type_parsed',
            'is_active'
        )

    @classmethod
    def get_item_app_parsed(cls, obj):
        return dict(ASSIGNMENT_APP_CHOICES)[obj.item_app]

    @classmethod
    def get_posting_group(cls, obj):
        return {
            'id': obj.posting_group_id,
            'code': obj.posting_group.code,
            'title': obj.posting_group.title,
            'posting_group_type': obj.posting_group.posting_group_type,
            'is_active': obj.posting_group.is_active
        } if obj.posting_group else {}

    @classmethod
    def get_posting_group_type_parsed(cls, obj):
        return dict(GROUP_TYPE_CHOICES)[obj.posting_group.posting_group_type]


class JEGLAccountMappingListSerializer(serializers.ModelSerializer):
    role_key_parsed = serializers.SerializerMethodField()
    posting_group = serializers.SerializerMethodField()
    account_data = serializers.SerializerMethodField()

    class Meta:
        model = JEGLAccountMapping
        fields = (
            'id',
            'role_key',
            'role_key_parsed',
            'posting_group',
            'account_data',
            'is_active'
        )

    @classmethod
    def get_role_key_parsed(cls, obj):
        return dict(ROLE_KEY_CHOICES)[obj.role_key]

    @classmethod
    def get_posting_group(cls, obj):
        return {
            'id': obj.posting_group_id,
            'code': obj.posting_group.code,
            'title': obj.posting_group.title,
            'posting_group_type': obj.posting_group.posting_group_type,
            'is_active': obj.posting_group.is_active
        } if obj.posting_group else {}

    @classmethod
    def get_account_data(cls, obj):
        return {
            'id': str(obj.account.id),
            'acc_code': obj.account.acc_code,
            'acc_name': obj.account.acc_name,
            'foreign_acc_name': obj.account.foreign_acc_name,
        } if obj.account else {}

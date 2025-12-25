from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounting.accountingsettings.models import ChartOfAccounts
from apps.accounting.accountingsettings.models.account_determination import (
    JEDocumentType, JEPostingRule, JEPostingGroup, JEGroupAssignment, JEGLAccountMapping,
    JE_DOCUMENT_TYPE_APP, DOCUMENT_TYPE_CHOICES, ASSIGNMENT_APP_CHOICES, GROUP_TYPE_CHOICES, ROLE_KEY_CHOICES,
    AMOUNT_SOURCE_CHOICES, RULE_LEVEL_CHOICES, SIDE_CHOICES, JEPostingGroupRoleKey,
)
from apps.masterdata.saledata.models.product import ProductType
from apps.masterdata.saledata.models.accounts import AccountType
from apps.shared import BaseMsg

# =============================================================================
# DOCUMENT TYPE
# =============================================================================
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
        return dict(DOCUMENT_TYPE_CHOICES).get(obj.module, obj.module)

    @classmethod
    def get_app_code_parsed(cls, obj):
        return dict(JE_DOCUMENT_TYPE_APP).get(obj.app_code, obj.app_code)


class JEDocumentTypeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JEDocumentType
        fields = ('is_auto_je',)

# =============================================================================
# POSTING GROUP
# =============================================================================
class JEPostingGroupListSerializer(serializers.ModelSerializer):
    posting_group_type_parsed = serializers.SerializerMethodField()
    assignment_data_list = serializers.SerializerMethodField()

    class Meta:
        model = JEPostingGroup
        fields = (
            'id',
            'code',
            'title',
            'posting_group_type',
            'posting_group_type_parsed',
            'assignment_data_list',
            'is_active'
        )

    @classmethod
    def get_posting_group_type_parsed(cls, obj):
        return dict(GROUP_TYPE_CHOICES).get(obj.posting_group_type, obj.posting_group_type)

    @classmethod
    def get_assignment_data_list(cls, obj):
        return [item.item_app_data for item in obj.assignment_posting_group.all()]


class JEPostingGroupCreateSerializer(serializers.ModelSerializer):
    assignment_data_list = serializers.JSONField(default=list, required=False)

    class Meta:
        model = JEPostingGroup
        fields = (
            'code',
            'title',
            'posting_group_type',
            'assignment_data_list',
            'is_active'
        )

    @classmethod
    def validate_code(cls, value):
        if JEPostingGroup.objects.filter_on_company(code=value).exists():
            raise serializers.ValidationError({"code": BaseMsg.CODE_IS_EXISTS})
        return value

    def validate(self, validate_data):
        posting_group_type = validate_data.get('posting_group_type')
        assignment_data_list = validate_data.pop('assignment_data_list', [])

        if posting_group_type == 'ITEM_GROUP':
            validated_assignment_data_list = []
            existing_objs = ProductType.objects.filter(id__in=assignment_data_list)
            existing_map = {str(obj.id): obj for obj in existing_objs}
            assigned_qs = JEGroupAssignment.objects.filter_on_company(item_id__in=assignment_data_list)
            assigned_map = {str(x.item_id): x for x in assigned_qs}
            for item_id in assignment_data_list:
                item_str = str(item_id)
                if item_str not in existing_map:
                    raise serializers.ValidationError({"prd_type_obj": _('Product type does not exist')})
                if item_str in assigned_map:
                    obj = existing_map[item_str]
                    raise serializers.ValidationError(
                        {"prd_type_obj": _(f'{obj.code} - {obj.title} is belong to other group')}
                    )
                validated_assignment_data_list.append(existing_map[item_str])
            validate_data['assignment_data_list'] = validated_assignment_data_list

        elif posting_group_type == 'PARTNER_GROUP':
            validated_assignment_data_list = []
            existing_objs = AccountType.objects.filter(id__in=assignment_data_list)
            existing_map = {str(obj.id): obj for obj in existing_objs}
            assigned_qs = JEGroupAssignment.objects.filter_on_company(item_id__in=assignment_data_list)
            assigned_map = {str(x.item_id): x for x in assigned_qs}
            for item_id in assignment_data_list:
                item_str = str(item_id)
                if item_str not in existing_map:
                    raise serializers.ValidationError({"acc_type_obj": _('Account type does not exist')})
                if item_str in assigned_map:
                    obj = existing_map[item_str]
                    raise serializers.ValidationError(
                        {"acc_type_obj": _(f'{obj.code} - {obj.title} is belong to other group')}
                    )
                validated_assignment_data_list.append(existing_map[item_str])
            validate_data['assignment_data_list'] = validated_assignment_data_list

        return validate_data

    def create(self, validated_data):
        assignment_data_list = validated_data.pop('assignment_data_list', [])

        pg_obj = JEPostingGroup.objects.create(**validated_data)

        JEGroupAssignment.create_assignment_data(pg_obj, assignment_data_list)

        return pg_obj


class JEPostingGroupDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = JEPostingGroup
        fields = (
            'id',
            'code',
            'title',
            'posting_group_type',
            'is_active'
        )


class JEPostingGroupUpdateSerializer(serializers.ModelSerializer):
    assignment_data_list = serializers.JSONField(default=list, required=False)

    class Meta:
        model = JEPostingGroup
        fields = (
            'title',
            'is_active',
            'assignment_data_list'
        )

    def validate(self, validate_data):
        posting_group_type = validate_data.get('posting_group_type')
        assignment_data_list = validate_data.pop('assignment_data_list', [])

        if posting_group_type == 'ITEM_GROUP':
            validated_assignment_data_list = []
            existing_objs = ProductType.objects.filter(id__in=assignment_data_list)
            existing_map = {str(obj.id): obj for obj in existing_objs}
            assigned_qs = JEGroupAssignment.objects.filter_on_company(item_id__in=assignment_data_list)
            if self.instance:
                assigned_qs = assigned_qs.exclude(posting_group_id=self.instance.id)
            assigned_map = {str(x.item_id): x for x in assigned_qs}
            for item_id in assignment_data_list:
                item_str = str(item_id)
                if item_str not in existing_map:
                    raise serializers.ValidationError({"prd_type_obj": _('Product type does not exist')})
                if item_str in assigned_map:
                    obj = existing_map[item_str]
                    raise serializers.ValidationError(
                        {"prd_type_obj": _(f'{obj.code} - {obj.title} is belong to other group')}
                    )
                validated_assignment_data_list.append(existing_map[item_str])
            validate_data['assignment_data_list'] = validated_assignment_data_list

        elif posting_group_type == 'PARTNER_GROUP':
            validated_assignment_data_list = []
            existing_objs = AccountType.objects.filter(id__in=assignment_data_list)
            existing_map = {str(obj.id): obj for obj in existing_objs}
            assigned_qs = JEGroupAssignment.objects.filter_on_company(item_id__in=assignment_data_list)
            if self.instance:
                assigned_qs = assigned_qs.exclude(posting_group_id=self.instance.id)
            assigned_map = {str(x.item_id): x for x in assigned_qs}
            for item_id in assignment_data_list:
                item_str = str(item_id)
                if item_str not in existing_map:
                    raise serializers.ValidationError({"acc_type_obj": _('Account type does not exist')})
                if item_str in assigned_map:
                    obj = existing_map[item_str]
                    raise serializers.ValidationError(
                        {"acc_type_obj": _(f'{obj.code} - {obj.title} is belong to other group')}
                    )
                validated_assignment_data_list.append(existing_map[item_str])
            validate_data['assignment_data_list'] = validated_assignment_data_list

        return validate_data

    def update(self, instance, validated_data):
        assignment_data_list = validated_data.pop('assignment_data_list', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        JEGroupAssignment.create_assignment_data(instance, assignment_data_list)

        return instance

# =============================================================================
# POSTING GROUP - ROLE KEY
# =============================================================================
class JEPostingGroupRoleKeyListSerializer(serializers.ModelSerializer):

    class Meta:
        model = JEPostingGroupRoleKey
        fields = (
            'id',
            'posting_group',
            'role_key',
            'description',
        )

# =============================================================================
# GROUP ASSIGNMENT
# =============================================================================
class JEGroupAssignmentListSerializer(serializers.ModelSerializer):
    item_app_parsed = serializers.SerializerMethodField()
    posting_group_data = serializers.SerializerMethodField()
    posting_group_type_parsed = serializers.SerializerMethodField()

    class Meta:
        model = JEGroupAssignment
        fields = (
            'id',
            'item_app',
            'item_app_parsed',
            'item_app_data',
            'posting_group',
            'posting_group_data',
            'posting_group_type_parsed',
            'is_active'
        )

    @classmethod
    def get_item_app_parsed(cls, obj):
        return dict(ASSIGNMENT_APP_CHOICES).get(obj.item_app, obj.item_app)

    @classmethod
    def get_posting_group_data(cls, obj):
        return {
            'id': obj.posting_group_id,
            'code': obj.posting_group.code,
            'title': obj.posting_group.title,
            'posting_group_type': obj.posting_group.posting_group_type,
            'is_active': obj.posting_group.is_active
        } if obj.posting_group else {}

    @classmethod
    def get_posting_group_type_parsed(cls, obj):
        return dict(GROUP_TYPE_CHOICES).get(obj.posting_group.posting_group_type, obj.posting_group.posting_group_type)

# =============================================================================
# GL ACCOUNT MAPPING
# =============================================================================
class JEGLAccountMappingListSerializer(serializers.ModelSerializer):
    role_key_parsed = serializers.SerializerMethodField()
    posting_group_data = serializers.SerializerMethodField()
    account_data = serializers.SerializerMethodField()

    class Meta:
        model = JEGLAccountMapping
        fields = (
            'id',
            'role_key',
            'role_key_parsed',
            'posting_group',
            'posting_group_data',
            'account',
            'account_data',
            'is_active'
        )

    @classmethod
    def get_role_key_parsed(cls, obj):
        return dict(ROLE_KEY_CHOICES).get(obj.role_key, obj.role_key)

    @classmethod
    def get_posting_group_data(cls, obj):
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


class JEGLAccountMappingCreateSerializer(serializers.ModelSerializer):
    posting_group = serializers.UUIDField()
    account = serializers.UUIDField()

    class Meta:
        model = JEGLAccountMapping
        fields = (
            'posting_group',
            'role_key',
            'account',
            'is_active'
        )

    @classmethod
    def validate_posting_group(cls, value):
        try:
            return JEPostingGroup.objects.get(id=value, is_active=True)
        except JEPostingGroup.DoesNotExist:
            raise serializers.ValidationError({'posting_group': _('Posting group is not available')})

    @classmethod
    def validate_account(cls, value):
        try:
            return ChartOfAccounts.objects.get(id=value, is_active=True)
        except ChartOfAccounts.DoesNotExist:
            raise serializers.ValidationError({'account': _('Account is not available')})

    def validate(self, validate_data):
        posting_group = validate_data.get('posting_group')
        role_key = validate_data.get('role_key')

        # 1. Kiểm tra Role có thuộc về Group này không
        if not JEPostingGroupRoleKey.objects.filter_on_company(posting_group=posting_group, role_key=role_key).exists():
            raise serializers.ValidationError({"role_key": _(f'{posting_group.code} - {role_key} is not allowed')})

        # 2. Kiểm tra trùng lặp Mapping
        if JEGLAccountMapping.objects.filter_on_company(posting_group=posting_group, role_key=role_key).exists():
            raise serializers.ValidationError({"role_key": _(f'{posting_group.code} - {role_key} is existed')})
        return validate_data


class JEGLAccountMappingDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = JEGLAccountMapping
        fields = (
            'id',
            'role_key',
            'posting_group',
            'is_active'
        )


class JEGLAccountMappingUpdateSerializer(serializers.ModelSerializer):
    account = serializers.UUIDField()

    class Meta:
        model = JEGLAccountMapping
        fields = (
            'account',
            'is_active',
        )

    @classmethod
    def validate_account(cls, value):
        try:
            return ChartOfAccounts.objects.get(id=value, is_active=True)
        except ChartOfAccounts.DoesNotExist:
            raise serializers.ValidationError({'account': _('Account is not available')})

# =============================================================================
# POSTING RULE (PHẦN QUAN TRỌNG NHẤT)
# =============================================================================
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
        return dict(RULE_LEVEL_CHOICES).get(obj.rule_level, obj.rule_level)

    @classmethod
    def get_role_key_parsed(cls, obj):
        return dict(ROLE_KEY_CHOICES).get(obj.role_key, obj.role_key)

    @classmethod
    def get_side_parsed(cls, obj):
        return dict(SIDE_CHOICES).get(obj.side, obj.side)

    @classmethod
    def get_amount_source_parsed(cls, obj):
        return dict(AMOUNT_SOURCE_CHOICES).get(obj.amount_source, obj.amount_source)

    @classmethod
    def get_document_type_code(cls, obj):
        return obj.je_document_type.code

    @classmethod
    def get_document_type_app_code_parsed(cls, obj):
        return dict(JE_DOCUMENT_TYPE_APP).get(obj.je_document_type.app_code, obj.je_document_type.app_code)

    @classmethod
    def get_fixed_account_data(cls, obj):
        return {
            'id': str(obj.fixed_account.id),
            'acc_code': obj.fixed_account.acc_code,
            'acc_name': obj.fixed_account.acc_name,
            'foreign_acc_name': obj.fixed_account.foreign_acc_name,
        } if obj.fixed_account else {}


class JEPostingRuleCreateSerializer(serializers.ModelSerializer):
    je_document_type = serializers.CharField()
    fixed_account = serializers.UUIDField(allow_null=True, required=False)
    lookup_data = serializers.JSONField(required=False, default=dict)

    class Meta:
        model = JEPostingRule
        fields = (
            'je_document_type',
            'description',
            'side',
            'rule_level',
            'priority',
            'amount_source',
            'fixed_account',
            'role_key',
            'account_source_type',
            'lookup_data',
            'is_active'
        )

    @classmethod
    def validate_je_document_type(cls, value):
        try:
            return JEDocumentType.objects.get_on_company(app_code=value)
        except JEDocumentType.DoesNotExist:
            raise serializers.ValidationError({'je_document_type': _('Document type does not exist')})

    def validate(self, validate_data):
        account_source_type = validate_data.get('account_source_type')
        lookup_data = validate_data.get('lookup_data', {})

        if account_source_type == 'FIXED':
            role_key = validate_data.get('role_key')
            fixed_account = ChartOfAccounts.objects.filter(
                id=validate_data.get('fixed_account'), is_active=True
            ).first()
            if not fixed_account:
                raise serializers.ValidationError({'fixed_account': _('Fixed account is required')})
            validate_data['fixed_account'] = fixed_account
            if not role_key:
                raise serializers.ValidationError({'role_key': _('Role key is required')})
            validate_data['role_key'] = role_key

        elif account_source_type == 'LOOKUP':
            pg_id = lookup_data.get('posting_group')
            role_key = lookup_data.get('role_key')
            validate_data['fixed_account'] = None
            validate_data['role_key'] = role_key

            if not pg_id and not role_key:
                raise serializers.ValidationError({'lookup_data': _('Lookup data is required')})

            if not JEPostingGroupRoleKey.objects.filter_on_company(
                    posting_group_id=pg_id, posting_group__is_active=True, role_key=role_key
            ).exists():
                raise serializers.ValidationError({'lookup_data': _(f'{role_key} is not configure in this group.')})

        if JEPostingRule.objects.filter_on_company(
                je_document_type=validate_data.get('je_document_type'),
                rule_level=validate_data.get('rule_level'),
                priority=validate_data.get('priority')
        ).exists():
            raise serializers.ValidationError({'priority': _('Priority is exist')})

        # validate sớm
        try:
            validate_data_clone = validate_data.copy()
            if 'lookup_data' in validate_data_clone:
                del validate_data_clone['lookup_data']
            # Init Model ảo
            temp_rule = JEPostingRule(**validate_data_clone)
            JEPostingRule.check_posting_rule(temp_rule)
        except ValidationError as error:
            raise serializers.ValidationError(error.message_dict)
        except TypeError as error:
            raise serializers.ValidationError({'error': str(error)})

        return validate_data

    def create(self, validated_data):
        lookup_data = validated_data.pop('lookup_data', {})

        posting_rule_obj = JEPostingRule.objects.create(**validated_data)

        if posting_rule_obj.account_source_type == 'LOOKUP' and lookup_data:
            pg_id = lookup_data.get('posting_group')
            role_key = lookup_data.get('role_key')

            JEGLAccountMapping.objects.get_or_create(
                tenant_id=posting_rule_obj.tenant_id,
                company_id=posting_rule_obj.company_id,
                posting_group_id=pg_id,
                role_key=role_key,
                defaults={
                    'account': None
                }
            )
        return posting_rule_obj


class JEPostingRuleDetailSerializer(serializers.ModelSerializer):
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
        return dict(RULE_LEVEL_CHOICES).get(obj.rule_level, obj.rule_level)

    @classmethod
    def get_role_key_parsed(cls, obj):
        return dict(ROLE_KEY_CHOICES).get(obj.role_key, obj.role_key)

    @classmethod
    def get_side_parsed(cls, obj):
        return dict(SIDE_CHOICES).get(obj.side, obj.side)

    @classmethod
    def get_amount_source_parsed(cls, obj):
        return dict(AMOUNT_SOURCE_CHOICES).get(obj.amount_source, obj.amount_source)

    @classmethod
    def get_document_type_code(cls, obj):
        return obj.je_document_type.code

    @classmethod
    def get_document_type_app_code_parsed(cls, obj):
        return dict(JE_DOCUMENT_TYPE_APP).get(obj.je_document_type.app_code, obj.je_document_type.app_code)

    @classmethod
    def get_fixed_account_data(cls, obj):
        return {
            'id': str(obj.fixed_account.id),
            'acc_code': obj.fixed_account.acc_code,
            'acc_name': obj.fixed_account.acc_name,
            'foreign_acc_name': obj.fixed_account.foreign_acc_name,
        } if obj.fixed_account else {}


class JEPostingRuleUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = JEPostingRule
        fields = (
            'description',
            'is_active'
        )

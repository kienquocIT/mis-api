from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounting.accountingsettings.models.chart_of_account import ChartOfAccounts
from apps.accounting.accountingsettings.models.account_determination import (
    ACCOUNT_DETERMINATION_TYPE,
    AccountDetermination, AccountDeterminationSub,
)
from apps.masterdata.saledata.models import WareHouse, Product, ProductType


class AccountDeterminationListSerializer(serializers.ModelSerializer):
    account_determination_sub_list = serializers.SerializerMethodField()
    account_determination_type_convert = serializers.SerializerMethodField()

    class Meta:
        model = AccountDetermination
        fields = (
            'id', 'code', 'title', 'foreign_title', 'transaction_key',
            'description', 'account_determination_sub_list',
            'account_determination_type', 'account_determination_type_convert',
            'can_change_account'
        )

    @classmethod
    def get_account_determination_sub_list(cls, obj):
        subs = obj.sub_items.select_related('account_mapped').order_by('priority', 'id')
        data = []
        for sub in subs:
            context_desc = []
            if sub.match_context:
                ctx = sub.match_context
                if ctx.get('warehouse_id'):
                    wh = WareHouse.objects.filter(id=ctx['warehouse_id']).first()
                    if wh:
                        context_desc.append(f"Warehouse: {wh.code}")
                if ctx.get('product_type_id'):
                    pt = ProductType.objects.filter(id=ctx['product_type_id']).first()
                    if pt:
                        context_desc.append(f"Product type: {pt.code}")
                if ctx.get('product_id'):
                    prd = Product.objects.filter(id=ctx['product_id']).first()
                    if prd:
                        context_desc.append(f"Product: {prd.code}")
            data.append({
                'transaction_key': obj.transaction_key,
                'id': sub.id,
                'transaction_key_sub': sub.transaction_key_sub,
                'description': sub.description,
                'account_mapped_data': {
                    'id': str(sub.account_mapped.id),
                    'acc_code': sub.account_mapped.acc_code,
                    'acc_name': sub.account_mapped.acc_name,
                    'foreign_acc_name': sub.account_mapped.foreign_acc_name,
                },
                'example': sub.example,
                'match_context': sub.match_context,
                'search_rule': sub.search_rule,
                'priority': sub.priority,
                'is_custom': sub.is_custom,
                'context_description': ", ".join(context_desc) if context_desc else '',
            })
        return data

    @classmethod
    def get_account_determination_type_convert(cls, obj):
        return ACCOUNT_DETERMINATION_TYPE[obj.account_determination_type][1]


class AccountDeterminationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDetermination
        fields = "__all__"


class AccountDeterminationUpdateSerializer(serializers.ModelSerializer):
    rule_data = serializers.JSONField(default=dict)
    special_rule_data = serializers.JSONField(default=dict)

    class Meta:
        model = AccountDetermination
        fields = ('rule_data', 'special_rule_data')

    @classmethod
    def validate_rule_data(cls, rule_data):
        valid_rule_data = {}
        if rule_data:
            account_mapped_obj = ChartOfAccounts.objects.filter(id=rule_data.get('account_mapped')).first()
            if account_mapped_obj:
                valid_rule_data['account_mapped'] = account_mapped_obj,
                valid_rule_data['account_mapped_data'] = {
                    'id': str(account_mapped_obj.id),
                    'acc_code': account_mapped_obj.acc_code,
                    'acc_name': account_mapped_obj.acc_name,
                    'foreign_acc_name': account_mapped_obj.foreign_acc_name,
                }
            raise serializers.ValidationError({'account_mapped': _('Account mapped not found')})
        return valid_rule_data

    @classmethod
    def validate_special_rule_data(cls, special_rule_data):
        valid_special_rule_data = {
            'description_sub': special_rule_data.get('description_sub', ''),
            'example_sub': special_rule_data.get('example_sub', ''),
            'id_sub': special_rule_data.get('id_sub', ''),
            'context_dict': {}
        }
        if special_rule_data:
            # Validate Account
            acc_id = special_rule_data.get('account_mapped')
            account_mapped_obj = ChartOfAccounts.objects.filter(id=acc_id).first()
            if not account_mapped_obj:
                raise serializers.ValidationError({'account_mapped': _('Account not found')})
            valid_special_rule_data['account_mapped_code'] = account_mapped_obj.acc_code

            # Validate Warehouse
            warehouse_id = special_rule_data.get('warehouse_id')
            if warehouse_id:
                warehouse_obj = WareHouse.objects.filter(id=warehouse_id).first()
                if not warehouse_obj:
                    raise serializers.ValidationError({'warehouse_id': _('Warehouse not found')})
                valid_special_rule_data['context_dict']['warehouse_id'] = warehouse_id

            # Validate Product Type
            product_type_id = special_rule_data.get('product_type_id')
            if product_type_id:
                product_type_obj = ProductType.objects.filter(id=product_type_id).first()
                if not product_type_obj:
                    raise serializers.ValidationError({'product_type_id': _('Product type not found')})
                valid_special_rule_data['context_dict']['product_type_id'] = product_type_id

            # Validate Product
            product_id = special_rule_data.get('product_id')
            if product_id:
                product_obj = Product.objects.filter(id=product_id).first()
                if not product_obj:
                    raise serializers.ValidationError({'product_id': _('Product not found')})
                valid_special_rule_data['context_dict']['product_id'] = product_id

            if not warehouse_id and not product_type_id and not product_id:
                raise serializers.ValidationError({'transaction_key_sub': _('Special condition is missing')})
        return valid_special_rule_data

    def validate(self, validate_data):
        if not self.instance.can_change_account and validate_data.get('rule_data'):
            raise serializers.ValidationError({'detail': _('Not allowed to change default account for this rule')})
        return validate_data

    def update(self, instance, validated_data):
        rule_data = validated_data.pop('rule_data', {})
        special_rule_data = validated_data.pop('special_rule_data', {})

        if rule_data:
            AccountDeterminationSub.objects.update_or_create(
                account_determination=instance,
                search_rule='default',
                defaults={**rule_data}
            )

        if special_rule_data:
            default_rule = instance.sub_items.filter(id=special_rule_data.get('id_sub')).first()
            inherited_transaction_key_sub = default_rule.transaction_key_sub if default_rule else ''
            AccountDeterminationSub.create_specific_rule(
                company_id=instance.company_id,
                transaction_key=instance.transaction_key,
                account_code=special_rule_data.get('account_mapped_code'),
                context_dict={**special_rule_data.get('context_dict', {})},
                transaction_key_sub=inherited_transaction_key_sub,
                description_sub=special_rule_data.get('description_sub'),
                example_sub=special_rule_data.get('example_sub')
            )

        return instance
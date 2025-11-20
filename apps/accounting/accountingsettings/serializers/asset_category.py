from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

__all__ = [
    'AssetCategoryListSerializer',
    'AssetCategoryCreateSerializer',
    'AssetCategoryDetailSerializer',
    'AssetCategoryUpdateSerializer'
]

from apps.accounting.accountingsettings.models import AssetCategory, ChartOfAccounts
from apps.masterdata.saledata.models import Product


class AssetCategoryListSerializer(serializers.ModelSerializer):
    depreciation_method_display = serializers.SerializerMethodField()
    category_type_display = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()

    class Meta:
        model = AssetCategory
        fields = (
            'id',
            'title',
            'code',
            'category_type',
            'category_type_display',
            'depreciation_method',
            'depreciation_method_display',
            'depreciation_time',
            'has_children',
            'parent_id'
        )

    @classmethod
    def get_depreciation_method_display(cls, obj):
        return obj.get_depreciation_method_display()

    @classmethod
    def get_category_type_display(cls, obj):
        return obj.get_category_type_display()

    @classmethod
    def get_has_children(cls, obj):
        return obj.child_categories.all().count() > 0

class AssetCategoryCreateSerializer(serializers.ModelSerializer):
    parent_id = serializers.UUIDField(allow_null=True, required=False, error_messages={
        'blank': 'Asset category id must not be blank',
    })
    asset_account_id = serializers.UUIDField(error_messages={
        'blank': 'Asset account must not be blank',
        'required': 'Asset account is required',
        'null': 'Asset account must not be null',
    })
    accumulated_depreciation_account_id = serializers.UUIDField(error_messages={
        'blank': 'Accumulated depreciation account must not be blank',
        'required': 'Accumulated depreciation account is required',
        'null': 'Accumulated depreciation account must not be null',
    })
    depreciation_expense_account_id = serializers.UUIDField(error_messages={
        'blank': 'Depreciation expense account must not be blank',
        'required': 'Depreciation expense account is required',
        'null': 'Depreciation expense account must not be null',
    })
    linked_product_data = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    remark = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = AssetCategory
        fields = (
            'title',
            'code',
            'category_type',
            'parent_id',
            'remark',
            'depreciation_method',
            'depreciation_time',
            'asset_account_id',
            'accumulated_depreciation_account_id',
            'depreciation_expense_account_id',
            'linked_product_data'
        )


    def validate_parent_id(self, value):
        if value:
            try:
                parent = AssetCategory.objects.get(id=value)
                if int(self.initial_data.get('category_type')) != parent.category_type:
                    raise serializers.ValidationError({'category_type': _('Not matching type with parent category')})
                return parent.id
            except AssetCategory.DoesNotExist:
                raise serializers.ValidationError({'parent': _('Parent category does not exist.')})
        return value

    @classmethod
    def _validate_account(cls, field_name, value):
        if not ChartOfAccounts.objects.filter(id=value).exists():
            raise serializers.ValidationError({field_name: _("Account does not exist.")})
        return ChartOfAccounts.objects.get(id=value).id

    @classmethod
    def validate_asset_account_id(cls, value):
        return cls._validate_account(field_name='asset_account_id', value=value)

    @classmethod
    def validate_accumulated_depreciation_account_id(cls, value):
        return cls._validate_account(field_name='accumulated_depreciation_account_id', value=value)

    @classmethod
    def validate_depreciation_expense_account_id(cls, value):
        return cls._validate_account(field_name='depreciation_expense_account_id', value=value)

    @classmethod
    def validate_linked_product_data(cls, linked_product_data):
        return_data = []
        for item in linked_product_data:
            product = Product.objects.filter(id=item).first()
            if not product:
                raise serializers.ValidationError({'linked_product_data': _('Linked products does not exist')})
            if product.asset_category:
                raise serializers.ValidationError(
                    {'linked_product_data': _('Product already linked with another asset category')})
            return_data.append(item)
        return return_data

    @transaction.atomic
    def create(self, validated_data):
        linked_product_data = validated_data.pop('linked_product_data', [])
        print(linked_product_data)
        asset_category = AssetCategory.objects.create(**validated_data)

        for item in linked_product_data:
            product = Product.objects.filter(id=item).first()
            product.asset_category = asset_category
            product.save(update_fields=['asset_category'])

        return asset_category

class AssetCategoryDetailSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()
    asset_account = serializers.SerializerMethodField()
    accumulated_depreciation_account = serializers.SerializerMethodField()
    depreciation_expense_account = serializers.SerializerMethodField()
    linked_product_data = serializers.SerializerMethodField()

    class Meta:
        model = AssetCategory
        fields = (
            'id',
            'title',
            'code',
            'remark',
            'parent',
            'category_type',
            'depreciation_method',
            'depreciation_time',
            'asset_account',
            'accumulated_depreciation_account',
            'depreciation_expense_account',
            'linked_product_data'
        )

    @classmethod
    def get_parent(cls, obj):
        if obj.parent:
            return {
                'id': obj.parent.id,
                'title': obj.parent.title,
                'code': obj.parent.code
            }
        return None

    @classmethod
    def get_asset_account(cls, obj):
        if obj.asset_account:
            return {
                'id': obj.asset_account.id,
                'acc_code': obj.asset_account.acc_code,
                'acc_name': obj.asset_account.acc_name,
            }
        return None

    @classmethod
    def get_accumulated_depreciation_account(cls, obj):
        if obj.accumulated_depreciation_account:
            return {
                'id': obj.accumulated_depreciation_account.id,
                'acc_code': obj.accumulated_depreciation_account.acc_code,
                'acc_name': obj.accumulated_depreciation_account.acc_name,
            }
        return None

    @classmethod
    def get_depreciation_expense_account(cls, obj):
        if obj.depreciation_expense_account:
            return {
                'id': obj.depreciation_expense_account.id,
                'acc_code': obj.depreciation_expense_account.acc_code,
                'acc_name': obj.depreciation_expense_account.acc_name,
            }
        return None

    @classmethod
    def get_depreciation_method_text(cls, obj):
        return obj.get_depreciation_method_display()

    @classmethod
    def get_linked_product_data(cls, obj):
        return [{
            'product_id': item.id,
            'title': item.title,
            'code': item.code,
        } for item in obj.asset_category_products.all()]

class AssetCategoryUpdateSerializer(serializers.ModelSerializer):
    parent_id = serializers.UUIDField(allow_null=True, required=False, error_messages={
        'blank': 'Asset category id must not be blank',
    })
    asset_account_id = serializers.UUIDField(allow_null=True, required=False, error_messages={})
    accumulated_depreciation_account_id = serializers.UUIDField(allow_null=True, required=False, error_messages={})
    depreciation_expense_account_id = serializers.UUIDField(allow_null=True, required=False, error_messages={})

    class Meta:
        model = AssetCategory
        fields = (
            'title',
            'code',
            'parent_id',
            'remark',
            'depreciation_method',
            'depreciation_time',
            'asset_account_id',
            'accumulated_depreciation_account_id',
            'depreciation_expense_account_id'
        )

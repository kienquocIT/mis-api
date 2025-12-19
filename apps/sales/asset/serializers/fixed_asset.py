import logging
from datetime import datetime

from rest_framework import serializers

from django.db.models import Min
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.accounting.accountingsettings.models import AssetCategory, ChartOfAccounts
from apps.core.hr.models import Group
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import ProductWareHouse
from apps.sales.asset.models import FixedAsset, FixedAssetUseDepartment
from apps.sales.asset.models.fixed_asset import FixedAssetCashOutPurchaseItem, \
    FixedAssetApInvoicePurchaseItemDetailProduct, FixedAssetApInvoicePurchaseItem, FixedAssetInventoryItem, \
    FixedAssetDepreciation
from apps.sales.asset.serializers.handler import CommonHandler
from apps.shared import BaseMsg, FixedAssetMsg, AbstractCreateSerializerModel, AbstractDetailSerializerModel, \
    AbstractListSerializerModel

logger = logging.getLogger(__name__)

__all__= [
    'FixedAssetListSerializer',
    'FixedAssetCreateSerializer',
    'FixedAssetDetailSerializer',
    'FixedAssetUpdateSerializer',
    'AssetForLeaseListSerializer',
    'AssetStatusLeaseListSerializer',
    'ProductWarehouseListSerializerForFixedAsset',
    'FixedAssetListWithDepreciationSerializer',
    'RunFixedAssetDepreciationSerializer'
]


class FixedAssetListSerializer(AbstractListSerializerModel):
    manage_department = serializers.SerializerMethodField()
    use_department = serializers.SerializerMethodField()
    use_customer = serializers.SerializerMethodField()
    depreciation_status = serializers.SerializerMethodField()

    class Meta:
        model = FixedAsset
        fields = (
            'id',
            'code',
            'asset_code',
            'title',
            'status',
            'manage_department',
            'use_department',
            'use_customer',
            'date_created',
            'depreciation_time',
            'depreciation_time_unit',
            'depreciation_status'
        )

    @classmethod
    def get_manage_department(cls, obj):
        return {
            'id': obj.manage_department.id,
            'code': obj.manage_department.code,
            'title': obj.manage_department.title,
        } if obj.manage_department else {}

    @classmethod
    def get_use_department(cls, obj):
        data = []
        for use_department_item in obj.use_departments.all():
            data.append({
                'id': use_department_item.use_department_id,
                'title': use_department_item.use_department.title,
                'code': use_department_item.use_department.code,
            })
        return data

    @classmethod
    def get_use_customer(cls, obj):
        return {
            'id': obj.use_customer.id,
            'code': obj.use_customer.code,
            'fullname': obj.use_customer.name,
        } if obj.use_customer else {}

    @classmethod
    def get_depreciation_status(cls, obj):
        if obj.net_book_value == 0:
            return {'status': 2, 'display': _('Fully Depreciated')}

        has_posted = obj.depreciations.filter(is_posted=True).exists()

        if not has_posted:
            return {'status': 0, 'display': _('Not Yet Started')}

        return {'status': 1, 'display': _('In Depreciation')}


class FixedAssetCreateSerializer(AbstractCreateSerializerModel):
    manage_department = serializers.UUIDField()
    use_department = serializers.ListSerializer(
        child=serializers.UUIDField(required=False)
    )
    asset_code = serializers.CharField(required=False)
    original_cost = serializers.FloatField()
    net_book_value = serializers.FloatField()
    depreciation_value = serializers.FloatField()
    asset_category_id = serializers.UUIDField(error_messages={
        'required': _('Asset category is required'),
        'null': _('Asset category must not be null'),
        'blank': _('Asset category must not be blank'),
    })
    source_data = serializers.JSONField()
    asset_account_id = serializers.UUIDField(error_messages={
        'required': _('Asset account is required'),
        'null': _('Asset account must not be null'),
        'blank': _('Asset account must not be blank'),
    })
    accumulated_depreciation_account_id = serializers.UUIDField(error_messages={
        'required': _('Accumulated depreciation account is required'),
        'null': _('Accumulated depreciation account must not be null'),
        'blank': _('Accumulated depreciation account must not be blank'),
    })
    depreciation_expense_account_id = serializers.UUIDField(error_messages={
        'required': _('Depreciation expense account is required'),
        'null': _('Depreciation expense account must not be null'),
        'blank': _('Depreciation expense account must not be blank'),
    })

    class Meta:
        model = FixedAsset
        fields = (
            'title',
            'asset_code',
            'manage_department',
            'use_department',
            'original_cost',
            'accumulative_depreciation',
            'net_book_value',
            'source_type',
            'source_data',
            'depreciation_method',
            'depreciation_time',
            'depreciation_time_unit',
            'adjustment_factor',
            'depreciation_start_date',
            'depreciation_end_date',
            'depreciation_value',
            'depreciation_data',
            'asset_category_id',
            'asset_account_id',
            'accumulated_depreciation_account_id',
            'depreciation_expense_account_id'
        )

    @classmethod
    def validate_account(cls, field_name, value):
        if not ChartOfAccounts.objects.filter(id=value).exists():
            raise serializers.ValidationError({field_name: _("Account does not exist.")})
        return ChartOfAccounts.objects.get(id=value).id

    @classmethod
    def validate_asset_account_id(cls, value):
        return cls.validate_account(field_name='asset_account_id', value=value)

    @classmethod
    def validate_accumulated_depreciation_account_id(cls, value):
        return cls.validate_account(field_name='accumulated_depreciation_account_id', value=value)

    @classmethod
    def validate_depreciation_expense_account_id(cls, value):
        return cls.validate_account(field_name='depreciation_expense_account_id', value=value)

    @classmethod
    def validate_manage_department(cls, value):
        try:
            return Group.objects.get(id=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError({'manage_department': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_use_department(cls, value):
        if isinstance(value, list):
            department_list = Group.objects.filter(id__in=value)
            if department_list.count() == len(value):
                return department_list
            raise serializers.ValidationError({"use_department": BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({"use_department": BaseMsg.FORMAT_NOT_MATCH})

    @classmethod
    def validate_asset_category_id(cls, value):
        try:
            return AssetCategory.objects.get(id=value).id
        except AssetCategory.DoesNotExist:
            raise serializers.ValidationError({'asset_category_id': _('Asset category does not exist')})

    def validate(self, validate_data):
        depreciation_value = validate_data.get('depreciation_value')
        original_cost = validate_data.get('original_cost')

        if int(depreciation_value) > int(original_cost):
            raise serializers.ValidationError({"depreciation_value": FixedAssetMsg.DEPRECIATION_MUST_BE_LESS_THAN_COST})

        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        use_departments = validated_data.pop('use_department')
        source_data = validated_data.pop('source_data')
        depreciation_data = validated_data.get('depreciation_data', [])

        try:
            with transaction.atomic():
                fixed_asset = FixedAsset.objects.create(**validated_data)

                CommonHandler.create_use_department(
                    fixed_asset,
                    use_departments=use_departments,
                    use_department_model=FixedAssetUseDepartment,
                )

                CommonHandler.create_source_detail(
                    fixed_asset,
                    source_data = source_data
                )

                CommonHandler.create_depreciation_data(
                    fixed_asset,
                    depreciation_data=depreciation_data,
                )

            return fixed_asset
        except Exception as err:
            logger.error(msg=f'Create fixed asset errors: {str(err)}')
            raise serializers.ValidationError({'asset': FixedAssetMsg.ERROR_CREATE})


class FixedAssetDetailSerializer(AbstractDetailSerializerModel):
    manage_department = serializers.SerializerMethodField()
    use_department = serializers.SerializerMethodField()
    source_data = serializers.SerializerMethodField()
    asset_category = serializers.SerializerMethodField()
    asset_account = serializers.SerializerMethodField()
    accumulated_depreciation_account = serializers.SerializerMethodField()
    depreciation_expense_account = serializers.SerializerMethodField()

    class Meta:
        model = FixedAsset
        fields = (
            'id',
            'source_type',
            'source_data',
            'title',
            'code',
            'asset_code',
            'manage_department',
            'use_department',
            'asset_category',
            'original_cost',
            'accumulative_depreciation',
            'net_book_value',
            'depreciation_method',
            'depreciation_time',
            'depreciation_time_unit',
            'adjustment_factor',
            'depreciation_start_date',
            'depreciation_end_date',
            'depreciation_value',
            'asset_account',
            'accumulated_depreciation_account',
            'depreciation_expense_account'
        )

    @classmethod
    def get_asset_category(cls, obj):
        return {
            'id': obj.asset_category_id,
            'title': obj.asset_category.title,
            'code': obj.asset_category.code,
        } if obj.asset_category else {}

    @classmethod
    def get_manage_department(cls, obj):
        return {
            'id': obj.manage_department.id,
            'code': obj.manage_department.code,
            'title': obj.manage_department.title,
        } if obj.manage_department else {}

    @classmethod
    def get_use_department(cls, obj):
        data = []
        for use_department_item in obj.use_departments.all():
            data.append({
                'id': use_department_item.use_department_id,
                'title': use_department_item.use_department.title,
                'code': use_department_item.use_department.code,
            })
        return data

    @classmethod
    def get_source_data(cls, obj):
        source_type = obj.source_type

        # Inventory source
        if source_type == 0:
            item = obj.inventory_items.first()
            if item:
                return {
                    'id': item.id,
                    'product_id': item.product_id,
                    'product_title': item.product.title if item.product else None,
                    'product_code': item.product.code if item.product else None,
                    'warehouse_id': item.warehouse_id,
                    'warehouse_title': item.warehouse.title if item.warehouse else None,
                    'warehouse_code': item.warehouse.code if item.warehouse else None,
                    'tracking_number': item.tracking_number,
                    'tracking_method': item.tracking_method,
                    'total_register_value': item.total_register_value,
                }
            return {}


        # AP Invoice purchase source
        if source_type == 1:
            ap_invoice_item_data = []
            for item in obj.ap_purchase_items.select_related('ap_invoice').all():
                ap_invoice_item_data.append({
                    'id': item.id,
                    'ap_invoice_id': item.ap_invoice_id,
                    'ap_invoice_code': item.ap_invoice.code if item.ap_invoice else None,
                    'ap_invoice_title': item.ap_invoice.title if item.ap_invoice else None,
                    'total_register_value': item.total_register_value,
                    'detail_products': [{
                        'id': detail_product.id,
                        'title': detail_product.title,
                        'code': detail_product.code,
                        'ap_invoice_item_id': detail_product.ap_invoice_item.id if detail_product.ap_invoice_item
                                                                                 else None,
                        'amount': detail_product.amount,
                        'quantity': detail_product.quantity,
                        'unit_price': detail_product.unit_price,
                    } for detail_product in item.detail_products.all()]
                })

            cash_out_item_data=[]
            for item in obj.cash_out_purchase_items.select_related('cash_out').all():
                cash_out_item_data.append({
                    'id': item.id,
                    'cash_out_id': item.cash_out_id,
                    'cash_out_code': item.cash_out.code if item.cash_out else None,
                    'cash_out_title': item.cash_out.title if item.cash_out else None,
                    'cof_type': item.cash_out.cof_type if item.cash_out else None,
                    'total_register_value': item.total_register_value,
                })

            return {
                'ap_invoice_items': ap_invoice_item_data,
                'cash_out_items' : cash_out_item_data
            }
        return []

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


class FixedAssetUpdateSerializer(AbstractCreateSerializerModel):
    manage_department = serializers.UUIDField()
    use_department = serializers.ListSerializer(
        child=serializers.UUIDField(required=False)
    )
    asset_code = serializers.CharField(required=False)
    original_cost = serializers.FloatField()
    net_book_value = serializers.FloatField()
    depreciation_value = serializers.FloatField()
    asset_category_id = serializers.UUIDField(error_messages={
        'required': _('Asset category is required'),
        'null': _('Asset category must not be null'),
        'blank': _('Asset category must not be blank'),
    })
    source_data = serializers.JSONField()
    asset_account_id = serializers.UUIDField(error_messages={
        'required': _('Asset account is required'),
        'null': _('Asset account must not be null'),
        'blank': _('Asset account must not be blank'),
    })
    accumulated_depreciation_account_id = serializers.UUIDField(error_messages={
        'required': _('Accumulated depreciation account is required'),
        'null': _('Accumulated depreciation account must not be null'),
        'blank': _('Accumulated depreciation account must not be blank'),
    })
    depreciation_expense_account_id = serializers.UUIDField(error_messages={
        'required': _('Depreciation expense account is required'),
        'null': _('Depreciation expense account must not be null'),
        'blank': _('Depreciation expense account must not be blank'),
    })

    class Meta:
        model = FixedAsset
        fields = (
            'title',
            'asset_code',
            'manage_department',
            'use_department',
            'original_cost',
            'accumulative_depreciation',
            'net_book_value',
            'source_type',
            'source_data',
            'depreciation_method',
            'depreciation_time',
            'depreciation_time_unit',
            'adjustment_factor',
            'depreciation_start_date',
            'depreciation_end_date',
            'depreciation_value',
            'depreciation_data',
            'asset_category_id',
            'asset_account_id',
            'accumulated_depreciation_account_id',
            'depreciation_expense_account_id'
        )

    @classmethod
    def validate_account(cls, field_name, value):
        if not ChartOfAccounts.objects.filter(id=value).exists():
            raise serializers.ValidationError({field_name: _("Account does not exist.")})
        return ChartOfAccounts.objects.get(id=value).id

    @classmethod
    def validate_asset_account_id(cls, value):
        return cls.validate_account(field_name='asset_account_id', value=value)

    @classmethod
    def validate_accumulated_depreciation_account_id(cls, value):
        return cls.validate_account(field_name='accumulated_depreciation_account_id', value=value)

    @classmethod
    def validate_depreciation_expense_account_id(cls, value):
        return cls.validate_account(field_name='depreciation_expense_account_id', value=value)

    @classmethod
    def validate_manage_department(cls, value):
        try:
            return Group.objects.get(id=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError({'manage_department': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_use_department(cls, value):
        if isinstance(value, list):
            department_list = Group.objects.filter(id__in=value)
            if department_list.count() == len(value):
                return department_list
            raise serializers.ValidationError({"use_department": BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({"use_department": BaseMsg.FORMAT_NOT_MATCH})

    @classmethod
    def validate_asset_category_id(cls, value):
        try:
            return AssetCategory.objects.get(id=value).id
        except AssetCategory.DoesNotExist:
            raise serializers.ValidationError({'asset_category_id': _('Asset category does not exist')})

    def validate(self, validate_data):
        depreciation_value = validate_data.get('depreciation_value')
        original_cost = validate_data.get('original_cost')

        if int(depreciation_value) > int(original_cost):
            raise serializers.ValidationError({"depreciation_value": FixedAssetMsg.DEPRECIATION_MUST_BE_LESS_THAN_COST})

        return validate_data

    @classmethod
    def _delete_related_models(cls, fixed_asset):
        FixedAssetUseDepartment.objects.filter(fixed_asset=fixed_asset).delete()

        FixedAssetInventoryItem.objects.filter(fixed_asset=fixed_asset).delete()

        ap_invoice_items = FixedAssetApInvoicePurchaseItem.objects.filter(fixed_asset=fixed_asset)
        for ap_item in ap_invoice_items:
            FixedAssetApInvoicePurchaseItemDetailProduct.objects.filter(
                ap_invoice_purchase_item=ap_item
            ).delete()
        ap_invoice_items.delete()

        FixedAssetCashOutPurchaseItem.objects.filter(fixed_asset=fixed_asset).delete()

        # remove all depreciation and update last posted date
        FixedAssetDepreciation.objects.filter(fixed_asset=fixed_asset).delete()
        setattr(fixed_asset, 'last_posted_date', None)


    @decorator_run_workflow
    def update(self, fixed_asset, validated_data):
        use_departments = validated_data.pop('use_department', None)
        source_data = validated_data.pop('source_data', None)
        depreciation_data = validated_data.get('depreciation_data', None)

        try:
            with transaction.atomic():
                self._delete_related_models(fixed_asset)

                for key, value in validated_data.items():
                    setattr(fixed_asset, key, value)
                fixed_asset.save()

                if use_departments is not None:
                    CommonHandler.create_use_department(
                        fixed_asset,
                        use_departments=use_departments,
                        use_department_model=FixedAssetUseDepartment,
                    )

                if source_data is not None:
                    CommonHandler.create_source_detail(
                        fixed_asset,
                        source_data=source_data
                    )

                if depreciation_data is not None:
                    CommonHandler.create_depreciation_data(
                        fixed_asset,
                        depreciation_data=depreciation_data
                    )

            return fixed_asset
        except Exception as err:
            logger.error(msg=f'Update fixed asset errors: {str(err)}')
            raise serializers.ValidationError({'asset': FixedAssetMsg.ERROR_CREATE})


class AssetForLeaseListSerializer(serializers.ModelSerializer):
    asset_id = serializers.SerializerMethodField()
    origin_cost = serializers.SerializerMethodField()
    net_value = serializers.SerializerMethodField()
    product_id = serializers.SerializerMethodField()
    product_data = serializers.SerializerMethodField()
    depreciation_time = serializers.SerializerMethodField()

    class Meta:
        model = FixedAsset
        fields = (
            'id',
            'title',
            'code',
            'asset_id',
            'origin_cost',
            'net_value',
            'product_id',
            'product_data',

            'depreciation_method',
            'depreciation_time',
            'adjustment_factor',
            'depreciation_start_date',
            'depreciation_end_date',
            'depreciation_data',
        )

    @classmethod
    def get_asset_id(cls, obj):
        return str(obj.id)

    @classmethod
    def get_origin_cost(cls, obj):
        return obj.original_cost

    @classmethod
    def get_net_value(cls, obj):
        return 0 if obj else 0

    @classmethod
    def get_product_id(cls, obj):
        return str(obj.product_id)

    @classmethod
    def get_product_data(cls, obj):
        return {
            'id': str(obj.product_id),
            'title': obj.product.title,
            'code': obj.product.code,
            'sale_information': {
                'default_uom': {
                    'id': str(obj.product.sale_default_uom_id), 'title': obj.product.sale_default_uom.title,
                    'code': obj.product.sale_default_uom.code, 'ratio': obj.product.sale_default_uom.ratio,
                    'rounding': obj.product.sale_default_uom.rounding,
                    'is_referenced_unit': obj.product.sale_default_uom.is_referenced_unit
                } if obj.product.sale_default_uom else {},
            }
        } if obj.product else {}

    @classmethod
    def get_depreciation_time(cls, obj):
        return obj.depreciation_time


class AssetStatusLeaseListSerializer(serializers.ModelSerializer):
    quantity = serializers.SerializerMethodField()
    quantity_leased = serializers.SerializerMethodField()
    asset_type = serializers.SerializerMethodField()
    lease_order_data = serializers.SerializerMethodField()
    origin_cost = serializers.SerializerMethodField()
    net_value = serializers.SerializerMethodField()

    class Meta:
        model = FixedAsset
        fields = (
            'id',
            'title',
            'code',
            'quantity',
            'quantity_leased',
            'asset_type',
            'status',
            'lease_order_data',

            'origin_cost',
            'net_value',
            'depreciation_time',
            'depreciation_start_date',
            'depreciation_end_date',
            'depreciation_data',
        )

    @classmethod
    def get_quantity(cls, obj):
        return 1 if obj else 0

    @classmethod
    def get_quantity_leased(cls, obj):
        return 1 if obj.status == 2 else 0

    @classmethod
    def get_asset_type(cls, obj):
        return 'Fixed asset' if obj else ''

    @classmethod
    def get_lease_order_data(cls, obj):
        lease_order = None
        delivery_product_asset = obj.delivery_pa_asset.filter(delivery_sub__system_status=3).first()
        if delivery_product_asset and obj.status == 2:
            if delivery_product_asset.delivery_sub:
                if delivery_product_asset.delivery_sub.order_delivery:
                    lease_order = delivery_product_asset.delivery_sub.order_delivery.lease_order
        return {
            'id': lease_order.id,
            'title': lease_order.title,
            'code': lease_order.code,
            'customer': {
                'id': lease_order.customer_id,
                'title': lease_order.customer.name,
                'code': lease_order.customer.code
            } if lease_order.customer else {},
            'product_lease_start_date': delivery_product_asset.product_lease_start_date,
            'product_lease_end_date': delivery_product_asset.product_lease_end_date,
        } if lease_order else {}

    @classmethod
    def get_origin_cost(cls, obj):
        return obj.original_cost

    @classmethod
    def get_net_value(cls, obj):
        return 0 if obj else 0


class ProductWarehouseListSerializerForFixedAsset(serializers.ModelSerializer):
    warehouse = serializers.SerializerMethodField()
    serial_items_data = serializers.SerializerMethodField()
    lot_items_data = serializers.SerializerMethodField()
    product_unit_cost = serializers.SerializerMethodField()

    class Meta:
        model = ProductWareHouse
        fields = (
            'id',
            'warehouse',
            'stock_amount',
            'serial_items_data',
            'lot_items_data',
            'product_unit_cost'
        )

    @classmethod
    def get_product_unit_cost(cls, obj):
        return obj.product.get_current_cost_info(1, **{
            'warehouse_id': obj.warehouse_id,
        })

    @classmethod
    def get_warehouse(cls, obj):
        return {
            'id': obj.warehouse_id,
            'title': obj.warehouse.title,
            'code': obj.warehouse.code,
        } if obj.warehouse else {}

    @classmethod
    def get_serial_items_data(cls, obj):
        return [
            {
                'id': item.id,
                'serial_number': item.serial_number,
                'manufacture_date': item.manufacture_date,
                'unit_cost': obj.product.get_current_cost_info(1, **{
                    'warehouse_id': obj.warehouse_id,
                })
            } for item in obj.product_warehouse_serial_product_warehouse.filter(serial_status=False)
        ]

    @classmethod
    def get_lot_items_data(cls, obj):
        return [
            {
                'id': item.id,
                'lot_number': item.lot_number,
                'manufacture_date': item.manufacture_date,
                'quantity_import': item.quantity_import,
                'unit_cost': obj.product.get_current_cost_info(1, **{
                    'warehouse_id': obj.warehouse_id,
                })
            } for item in obj.product_warehouse_lot_product_warehouse.filter(quantity_import__gt=0)
        ]


class FixedAssetListWithDepreciationSerializer(serializers.ModelSerializer):
    asset_category = serializers.SerializerMethodField()
    next_depreciation_period = serializers.SerializerMethodField()
    depreciation_status = serializers.SerializerMethodField()

    class Meta:
        model = FixedAsset
        fields = (
            'id',
            'code',
            'asset_code',
            'asset_category',
            'title',
            'original_cost',
            'accumulative_depreciation',
            'net_book_value',
            'last_posted_date',
            'depreciation_end_date',
            'next_depreciation_period',
            'depreciation_status'
        )

    @classmethod
    def get_asset_category(cls, obj):
        return {
            'id': obj.asset_category_id,
            'title': obj.asset_category.title,
            'code': obj.asset_category.code,
        } if obj.asset_category else {}

    @classmethod
    def get_next_depreciation_period(cls, obj):
        depreciation = obj.depreciations.filter(is_posted=False).order_by('start_date').first()
        if depreciation:
            return depreciation.start_date
        return None

    @classmethod
    def get_depreciation_status(cls, obj):
        if obj.net_book_value == 0:
            return {'status': 2, 'display': _('Fully Depreciated')}

        has_posted = obj.depreciations.filter(is_posted=True).exists()

        if not has_posted:
            return {'status': 0, 'display': _('Not Yet Started')}

        return {'status': 1, 'display': _('In Depreciation')}

class RunFixedAssetDepreciationSerializer(serializers.Serializer):
    asset_list = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
    )
    depreciation_month = serializers.CharField(required=True)  # Format: YYYY-MM-DD (use first day of month)

    @classmethod
    def validate_depreciation_month(cls, value):
        """Parse YYYY-MM format"""
        try:
            parsed_date = datetime.strptime(value, "%Y-%m")
            return {
                'year': parsed_date.year,
                'month': parsed_date.month,
                'raw': value
            }
        except ValueError:
            raise serializers.ValidationError("Invalid format. Use YYYY-MM (e.g., 2025-12)")

    @classmethod
    def validate_asset_list(cls, value):
        # Check all assets exist
        existing_ids = set(
            FixedAsset.objects.filter(id__in=value).values_list('id', flat=True)
        )
        missing_ids = set(value) - existing_ids

        if missing_ids:
            raise serializers.ValidationError(f"Fixed assets not found: {list(missing_ids)}")
        return value

    def validate(self, attrs):
        asset_list = attrs['asset_list']
        dep_month = attrs['depreciation_month']
        input_year = dep_month['year']
        input_month = dep_month['month']

        # Get the earliest unposted depreciation for each asset (next month to run)
        earliest_unposted = FixedAssetDepreciation.objects.filter(
            fixed_asset_id__in=asset_list,
            is_posted=False
        ).values('fixed_asset_id').annotate(
            earliest_start_date=Min('start_date')
        )

        if not earliest_unposted:
            raise serializers.ValidationError({
                'detail': "No unposted depreciation records found for selected assets"
            })

        # Check if all assets have unposted records
        # assets_with_unposted = {item['fixed_asset_id'] for item in earliest_unposted}
        # assets_without_unposted = set(asset_list) - assets_with_unposted
        # if assets_without_unposted:
        #     raise serializers.ValidationError({
        #         'detail': f"These assets have no unposted depreciation: {list(assets_without_unposted)}"
        #     })

        # Collect earliest months for each asset
        earliest_months = {}
        for item in earliest_unposted:
            asset_id = item['fixed_asset_id']
            earliest_date = item['earliest_start_date']
            month_key = f"{earliest_date.year}-{earliest_date.month:02d}"
            earliest_months[asset_id] = {
                'year': earliest_date.year,
                'month': earliest_date.month,
                'display': month_key
            }

        # Validation 1: All assets must have the same next depreciation month
        unique_months = set(m['display'] for m in earliest_months.values())
        if len(unique_months) > 1:
            raise serializers.ValidationError({
                'detail': "Fixed assets have different depreciation progress. "
                          "All assets must be at the same depreciation month.",
            })

        # Validation 2: Input month must match the next month to run
        next_month = list(earliest_months.values())[0]

        # Input month is ahead - trying to skip months
        if (input_year, input_month) > (next_month['year'], next_month['month']):
            raise serializers.ValidationError({
                'detail': f"Cannot run depreciation for {dep_month['month']}/{dep_month['year']}. "
                          f"Must run {next_month['month']}/{next_month['year']} first."
            })

        # Input month is behind - already posted
        if (input_year, input_month) < (next_month['year'], next_month['month']):
            raise serializers.ValidationError({
                'detail': f"Depreciation for {dep_month['month']}/{dep_month['year']} has already been posted. "
                          f"Next available month is {next_month['month']}/{next_month['year']}."
            })

        # Find unposted depreciation records for the specified month
        depreciations = FixedAssetDepreciation.objects.filter(
            fixed_asset_id__in=asset_list,
            start_date__year=dep_month['year'],
            start_date__month=dep_month['month'],
            is_posted=False
        ).select_related('fixed_asset')

        if not depreciations.exists():
            raise serializers.ValidationError({
                'detail': f"No unposted depreciation records found for {dep_month['month']}/{dep_month['year']}."
            })

        attrs['depreciations'] = list(depreciations)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        depreciations = validated_data['depreciations']

        assets_to_update = []
        depreciations_to_update = []

        for depreciation in depreciations:
            # Mark depreciation as posted
            depreciation.is_posted = True
            depreciations_to_update.append(depreciation)

            # Update fixed asset values
            fixed_asset = depreciation.fixed_asset
            fixed_asset.accumulative_depreciation = depreciation.accumulated_depreciation
            fixed_asset.net_book_value = fixed_asset.original_cost - depreciation.accumulated_depreciation
            fixed_asset.last_posted_date = depreciation.end_date
            assets_to_update.append(fixed_asset)

        # Bulk update for performance
        FixedAssetDepreciation.objects.bulk_update(
            depreciations_to_update,
            ['is_posted']
        )
        FixedAsset.objects.bulk_update(
            assets_to_update,
            ['accumulative_depreciation', 'net_book_value', 'last_posted_date']
        )

        return assets_to_update

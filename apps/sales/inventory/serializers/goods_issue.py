from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import UnitOfMeasure, WareHouse, ProductWareHouse, Product
from apps.sales.inventory.models import GoodsIssue, GoodsIssueProduct, InventoryAdjustmentItem, InventoryAdjustment
from apps.shared import ProductMsg, WarehouseMsg, GOODS_ISSUE_TYPE, SYSTEM_STATUS, AbstractDetailSerializerModel, \
    AbstractCreateSerializerModel, AbstractListSerializerModel
from apps.shared.translations.goods_issue import GIMsg

__all__ = [
    'GoodsIssueListSerializer',
    'GoodsIssueCreateSerializer',
    'GoodsIssueDetailSerializer',
    'GoodsIssueUpdateSerializer'
]


class GoodsIssueListSerializer(AbstractListSerializerModel):
    goods_issue_type = serializers.SerializerMethodField()

    class Meta:
        model = GoodsIssue
        fields = (
            'id',
            'code',
            'title',
            'goods_issue_type',
            'date_created'
        )

    @classmethod
    def get_goods_issue_type(cls, obj):
        return obj.goods_issue_type


class GoodsIssueCreateSerializer(AbstractCreateSerializerModel):
    goods_issue_type = serializers.IntegerField()
    inventory_adjustment_id = serializers.UUIDField(required=False)
    detail_data_ia = serializers.ListField()

    class Meta:
        model = GoodsIssue
        fields = (
            'title',
            'goods_issue_type',
            'inventory_adjustment_id',
            'note',
            'detail_data_ia',
        )

    def validate(self, validate_data):
        GoodsIssueCommonFunction.validate_goods_issue_type(validate_data)
        GoodsIssueCommonFunction.validate_inventory_adjustment_id(validate_data)
        GoodsIssueCommonFunction.validate_detail_data_ia(validate_data)
        print('*validate done')
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        detail_data_ia = validated_data.pop('detail_data_ia', [])
        instance = GoodsIssue.objects.create(**validated_data)
        GoodsIssueCommonFunction.create_issue_item(
            instance,
            detail_data_ia
        )
        return instance


class GoodsIssueDetailSerializer(AbstractDetailSerializerModel):
    inventory_adjustment = serializers.SerializerMethodField()
    detail_data_ia = serializers.SerializerMethodField()

    class Meta:
        model = GoodsIssue
        fields = (
            'id',
            'code',
            'title',
            'note',
            'goods_issue_type',
            'detail_data_ia',
            'inventory_adjustment',
            'system_status',
            'date_created'
        )

    @classmethod
    def get_inventory_adjustment(cls, obj):
        if obj.inventory_adjustment:
            return {
                'id': obj.inventory_adjustment_id,
                'title': obj.inventory_adjustment.title,
                'code': obj.inventory_adjustment.code,
            }
        return {}

    @classmethod
    def get_detail_data_ia(cls, obj):
        detail_data_ia = []
        for item in obj.goods_issue_product.all():
            ia_item = item.inventory_adjustment_item
            detail_data_ia.append({
                'id': ia_item.id,
                'product_warehouse_mapped_id': item.product_warehouse_id,
                'stock_quantity': item.product_warehouse.stock_amount,
                'product_mapped': {
                    'id': item.product_id,
                    'code': item.product.code,
                    'title': item.product.title,
                    'description': item.product.description,
                    'general_traceability_method': item.product.general_traceability_method
                },
                'uom_mapped': {
                    'id': item.uom_id,
                    'code': item.uom.code,
                    'title': item.uom.title
                },
                'warehouse_mapped': {
                    'id': item.warehouse_id,
                    'code': item.warehouse.code,
                    'title': item.warehouse.title
                },
                'limit_quantity': (
                    ia_item.book_quantity - ia_item.count - ia_item.issued_quantity
                ) if ia_item.action_type == 1 else (
                    ia_item.book_quantity - ia_item.count - ia_item.receipted_quantity
                ) if ia_item.action_type == 2 else 0,
                'quantity': item.quantity,
                'lot_data': item.lot_data,
                'sn_data': item.sn_data
            })
        return detail_data_ia


class GoodsIssueUpdateSerializer(AbstractCreateSerializerModel):
    goods_issue_type = serializers.IntegerField()
    inventory_adjustment_id = serializers.UUIDField(required=False)
    detail_data_ia = serializers.ListField()

    class Meta:
        model = GoodsIssue
        fields = (
            'title',
            'goods_issue_type',
            'inventory_adjustment_id',
            'note',
            'detail_data_ia',
        )

    def validate(self, validate_data):
        GoodsIssueCommonFunction.validate_goods_issue_type(validate_data)
        GoodsIssueCommonFunction.validate_inventory_adjustment_id(validate_data)
        GoodsIssueCommonFunction.validate_detail_data_ia(validate_data)
        print('*validate done')
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        detail_data_ia = validated_data.pop('detail_data_ia', [])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        GoodsIssueCommonFunction.create_issue_item(
            instance,
            detail_data_ia
        )
        return instance


class GoodsIssueCommonFunction:
    @classmethod
    def validate_goods_issue_type(cls, validate_data):
        goods_issue_type = validate_data.get('goods_issue_type')
        if goods_issue_type in [0, 1, 2]:
            validate_data['goods_issue_type'] = goods_issue_type
            print('1. validate_goods_issue_type --- ok')
            return True
        raise serializers.ValidationError({'goods_issue_type': "Goods issue type is not valid"})

    @classmethod
    def validate_inventory_adjustment_id(cls, validate_data):
        try:
            validate_data['inventory_adjustment_id'] = InventoryAdjustment.objects.get(
                id=validate_data.get('inventory_adjustment_id')
            ).id
            print('2. validate_inventory_adjustment_id  --- ok')
            return True
        except InventoryAdjustment.DoesNotExist:
            raise serializers.ValidationError({'inventory_adjustment': GIMsg.IA_NOT_EXIST})

    @classmethod
    def validate_detail_data_ia(cls, validate_data):
        try:
            detail_data_ia = validate_data.get('detail_data_ia')
            for item in detail_data_ia:
                prd_wh_obj = ProductWareHouse.objects.get(id=item.get('product_warehouse_id'))
                ia_item = InventoryAdjustmentItem.objects.get(id=item.get('inventory_adjustment_item_id'))
                if all([
                    prd_wh_obj.stock_amount >= float(item.get('quantity')),
                    ia_item.book_quantity - ia_item.count - ia_item.issued_quantity >= float(item.get('quantity'))
                ]):
                    item['inventory_adjustment_item_id'] = ia_item.id
                    item['product_warehouse_id'] = prd_wh_obj.id
                    item['product_id'] = Product.objects.get(id=item.get('product_id')).id
                    item['warehouse_id'] = WareHouse.objects.get(id=item.get('warehouse_id')).id
                    item['uom_id'] = UnitOfMeasure.objects.get(id=item.get('uom_id')).id
                else:
                    raise serializers.ValidationError({'stock_quantity': "Issue quantity can't > Stock quantity."})
            validate_data['detail_data_ia'] = detail_data_ia
            print('3. validate_detail_data_ia --- ok')
            return True
        except Exception as err:
            raise serializers.ValidationError({'detail_data_ia': f"Detail IA data is not valid. {err}"})

    @classmethod
    def create_issue_item(cls, instance, data):
        bulk_data = []
        for item in data:
            obj = GoodsIssueProduct(
                goods_issue=instance,
                inventory_adjustment_item_id=item['inventory_adjustment_item_id'],
                product_warehouse_id=item['product_warehouse_id'],
                product_id=item['product_id'],
                warehouse_id=item['warehouse_id'],
                uom_id=item['uom_id'],
                limit_quantity=item['limit_quantity'],
                quantity=item['quantity'],
                lot_data=item['lot_data'],
                sn_data=item['sn_data']
            )
            bulk_data.append(obj)
        GoodsIssueProduct.objects.filter(goods_issue=instance).delete()
        GoodsIssueProduct.objects.bulk_create(bulk_data)
        return True

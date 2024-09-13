from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import (
    UnitOfMeasure, WareHouse, ProductWareHouse, Product,
    ProductWareHouseSerial, ProductWareHouseLot
)
from apps.sales.inventory.models import GoodsIssue, GoodsIssueProduct, InventoryAdjustmentItem, InventoryAdjustment
from apps.sales.production.models import ProductionOrder
from apps.shared import AbstractDetailSerializerModel, AbstractCreateSerializerModel, AbstractListSerializerModel
from apps.shared.translations.goods_issue import GIMsg

__all__ = [
    'GoodsIssueListSerializer',
    'GoodsIssueCreateSerializer',
    'GoodsIssueDetailSerializer',
    'GoodsIssueUpdateSerializer',
    'ProductionOrderListSerializerForGIS',
    'ProductionOrderDetailSerializerForGIS'
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
                'product_mapped': item.product_data,
                'uom_mapped': item.uom_data,
                'warehouse_mapped': item.warehouse_data,
                'sum_quantity': ia_item.book_quantity - ia_item.count,
                'before_quantity': (
                        item.before_quantity + item.issued_quantity
                ) if obj.system_status == 3 else item.before_quantity,
                'remain_quantity': (
                        item.remain_quantity - item.issued_quantity
                ) if obj.system_status == 3 else item.remain_quantity,
                'issued_quantity': item.issued_quantity,
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
            validate_data['inventory_adjustment_id'] = str(InventoryAdjustment.objects.get(
                id=validate_data.get('inventory_adjustment_id')
            ).id)
            print('2. validate_inventory_adjustment_id  --- ok')
            return True
        except InventoryAdjustment.DoesNotExist:
            raise serializers.ValidationError({'inventory_adjustment': GIMsg.IA_NOT_EXIST})

    @classmethod
    def validate_detail_data_ia(cls, validate_data):
        try:
            detail_data_ia = validate_data.get('detail_data_ia')
            for item in detail_data_ia:
                product_obj = Product.objects.get(id=item.get('product_id'))
                warehouse_obj = WareHouse.objects.get(id=item.get('warehouse_id'))
                uom = UnitOfMeasure.objects.get(id=item.get('uom_id'))
                prd_wh_obj = ProductWareHouse.objects.get(product=product_obj, warehouse=warehouse_obj)
                ia_item = InventoryAdjustmentItem.objects.get(id=item.get('inventory_adjustment_item_id'))
                if prd_wh_obj.stock_amount < float(item.get('remain_quantity')):
                    raise serializers.ValidationError({'remain_quantity': "Remain quantity can't > stock quantity."})
                if prd_wh_obj.stock_amount < float(item.get('issued_quantity')):
                    raise serializers.ValidationError({'issued_quantity': "Issue quantity can't > stock quantity."})
                if ia_item.book_quantity - ia_item.count - ia_item.issued_quantity < float(item.get('issued_quantity')):
                    raise serializers.ValidationError({'issued_quantity': "Issue quantity can't > remain quantity."})
                item['inventory_adjustment_item_id'] = str(ia_item.id)
                item['product_id'] = str(product_obj.id)
                item['product_data'] = {
                    'id': str(product_obj.id),
                    'code': product_obj.code,
                    'title': product_obj.title,
                    'description': product_obj.description,
                    'general_traceability_method': product_obj.general_traceability_method
                }
                item['warehouse_id'] = str(warehouse_obj.id)
                item['warehouse_data'] = {
                    'id': str(warehouse_obj.id),
                    'code': warehouse_obj.code,
                    'title': warehouse_obj.title
                }
                item['uom_id'] = str(uom.id)
                item['uom_data'] = {
                    'id': str(uom.id),
                    'code': uom.code,
                    'title': uom.title
                }
            validate_data['detail_data_ia'] = detail_data_ia
            print('3. validate_detail_data_ia --- ok')
            return True
        except Exception as err:
            raise serializers.ValidationError({'detail_data_ia': f"Detail IA data is not valid. {err}"})

    @classmethod
    def create_issue_item(cls, instance, data):
        bulk_data = []
        for item in data:
            obj = GoodsIssueProduct(goods_issue=instance, **item)
            bulk_data.append(obj)
        GoodsIssueProduct.objects.filter(goods_issue=instance).delete()
        GoodsIssueProduct.objects.bulk_create(bulk_data)
        return True


# related serializers
class InventoryAdjustmentListSerializerForGIS(AbstractListSerializerModel):

    class Meta:
        model = InventoryAdjustment
        fields = (
            'id',
            'title',
            'code',
        )


class InventoryAdjustmentDetailSerializerForGIS(AbstractDetailSerializerModel):
    ia_data = serializers.SerializerMethodField()

    class Meta:
        model = InventoryAdjustment
        fields = (
            'id',
            'title',
            'ia_data',
        )

    @classmethod
    def get_ia_data(cls, obj):
        ia_data = []
        order = 1
        for item in obj.inventory_adjustment_item_mapped.filter(action_type=1).order_by('product_mapped__code'):
            ia_data.append({
                'id': item.id,
                'order': order,
                'product_mapped': {
                    'id': item.product_mapped_data.get('id'),
                    'code': item.product_mapped_data.get('code'),
                    'title': item.product_mapped_data.get('title'),
                    'description': item.product_mapped_data.get('description'),
                    'general_traceability_method': item.product_mapped_data.get('general_traceability_method')
                } if item.product_mapped_data else {},
                'uom_mapped': {
                    'id': item.uom_mapped_data.get('id'),
                    'code': item.uom_mapped_data.get('code'),
                    'title': item.uom_mapped_data.get('title'),
                    'ratio': item.uom_mapped_data.get('ratio')
                } if item.uom_mapped_data else {},
                'warehouse_mapped': {
                    'id': item.warehouse_mapped_data.get('id'),
                    'code': item.warehouse_mapped_data.get('code'),
                    'title': item.warehouse_mapped_data.get('title')
                } if item.warehouse_mapped_data else {},
                'before_quantity': item.issued_quantity,
                'remain_quantity': item.book_quantity - item.count - item.issued_quantity,
            })
            order += 1
        return ia_data


class ProductionOrderListSerializerForGIS(AbstractListSerializerModel):

    class Meta:
        model = ProductionOrder
        fields = (
            'id',
            'title',
            'code',
        )


class ProductionOrderDetailSerializerForGIS(AbstractDetailSerializerModel):
    task_data = serializers.SerializerMethodField()

    class Meta:
        model = ProductionOrder
        fields = (
            'id',
            'title',
            'task_data',
        )

    @classmethod
    def get_task_data(cls, obj):
        task_data = []
        for item in obj.po_task_production_order.filter(is_task=False):
            task_data.append({
                'id': item.id,
                'order': item.order,
                'product_mapped': {
                    'id': item.product_data.get('id'),
                    'code': item.product_data.get('code'),
                    'title': item.product_data.get('title'),
                    'description': item.product_data.get('description'),
                    'general_traceability_method': item.product.general_traceability_method
                } if item.product_data else {},
                'uom_mapped': {
                    'id': item.uom_data.get('id'),
                    'code': item.uom_data.get('code'),
                    'title': item.uom_data.get('title'),
                    'ratio': item.uom_data.get('ratio')
                } if item.uom_data else {},
                'warehouse_mapped': {
                    'id': item.warehouse_data.get('id'),
                    'code': item.warehouse_data.get('code'),
                    'title': item.warehouse_data.get('title')
                } if item.warehouse_data else {},
                'is_all_warehouse': item.is_all_warehouse,
                'limit_quantity': item.quantity,
                'sum_issued_quantity': 0
            })
        return task_data


class ProductWareHouseListSerializerForGIS(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = (
            'id',
            'stock_amount'
        )


class ProductWarehouseLotListSerializerForGIS(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouseLot
        fields = (
            'id',
            'lot_number',
            'quantity_import',
            'expire_date',
            'manufacture_date'
        )


class ProductWarehouseSerialListSerializerForGIS(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouseSerial
        fields = (
            'id',
            'vendor_serial_number',
            'serial_number',
            'expire_date',
            'manufacture_date',
            'warranty_start',
            'warranty_end',
            'is_delete'
        )

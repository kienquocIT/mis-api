from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import (
    UnitOfMeasure, WareHouse, Product,
    ProductWareHouse, ProductWareHouseSerial, ProductWareHouseLot
)
from apps.sales.inventory.models import GoodsIssue, GoodsIssueProduct, InventoryAdjustmentItem, InventoryAdjustment
from apps.sales.production.models import ProductionOrder, ProductionOrderTask
from apps.shared import AbstractDetailSerializerModel, AbstractCreateSerializerModel, AbstractListSerializerModel

__all__ = [
    'GoodsIssueListSerializer',
    'GoodsIssueCreateSerializer',
    'GoodsIssueDetailSerializer',
    'GoodsIssueUpdateSerializer',
    'ProductionOrderListSerializerForGIS',
    'ProductionOrderDetailSerializerForGIS',
    'InventoryAdjustmentListSerializerForGIS',
    'InventoryAdjustmentDetailSerializerForGIS',
    'ProductWarehouseSerialListSerializerForGIS',
    'ProductWarehouseLotListSerializerForGIS',
    'ProductWareHouseListSerializerForGIS'
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
    inventory_adjustment_id = serializers.UUIDField(required=False, allow_null=True)
    detail_data_ia = serializers.ListField()
    production_order_id = serializers.UUIDField(required=False, allow_null=True)
    detail_data_po = serializers.ListField()

    class Meta:
        model = GoodsIssue
        fields = (
            'title',
            'note',
            'goods_issue_type',
            'inventory_adjustment_id',
            'detail_data_ia',
            'production_order_id',
            'detail_data_po'
        )

    def validate(self, validate_data):
        GoodsIssueCommonFunction.validate_goods_issue_type(validate_data)
        GoodsIssueCommonFunction.validate_inventory_adjustment_id(validate_data)
        GoodsIssueCommonFunction.validate_detail_data_ia(validate_data)
        GoodsIssueCommonFunction.validate_production_order_id(validate_data)
        GoodsIssueCommonFunction.validate_detail_data_po(validate_data)
        print('*validate done')
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        detail_data_ia = validated_data.pop('detail_data_ia', [])
        detail_data_po = validated_data.pop('detail_data_po', [])
        instance = GoodsIssue.objects.create(**validated_data)
        GoodsIssueCommonFunction.create_issue_item(instance, detail_data_ia)
        GoodsIssueCommonFunction.create_issue_item(instance, detail_data_po)
        return instance


class GoodsIssueDetailSerializer(AbstractDetailSerializerModel):
    inventory_adjustment = serializers.SerializerMethodField()
    detail_data_ia = serializers.SerializerMethodField()
    production_order = serializers.SerializerMethodField()
    detail_data_po = serializers.SerializerMethodField()

    class Meta:
        model = GoodsIssue
        fields = (
            'id',
            'code',
            'title',
            'note',
            'goods_issue_type',
            'inventory_adjustment',
            'detail_data_ia',
            'production_order',
            'detail_data_po',
            'date_created'
        )

    @classmethod
    def get_inventory_adjustment(cls, obj):
        return {
            'id': obj.inventory_adjustment_id,
            'title': obj.inventory_adjustment.title,
            'code': obj.inventory_adjustment.code,
        } if obj.inventory_adjustment else {}

    @classmethod
    def get_detail_data_ia(cls, obj):
        detail_data_ia = []
        if obj.inventory_adjustment:
            if obj.system_status == 3:
                for item in obj.goods_issue_product.filter(issued_quantity__gt=0):
                    ia_item = item.inventory_adjustment_item
                    detail_data_ia.append({
                        'id': ia_item.id,
                        'product_mapped': item.product_data,
                        'uom_mapped': item.uom_data,
                        'warehouse_mapped': item.warehouse_data,
                        'sum_quantity': ia_item.book_quantity - ia_item.count,
                        'before_quantity': item.before_quantity,
                        'remain_quantity': item.remain_quantity,
                        'issued_quantity': item.issued_quantity,
                        'lot_data': item.lot_data,
                        'sn_data': item.sn_data
                    })
            else:
                for item in obj.goods_issue_product.all():
                    ia_item = item.inventory_adjustment_item
                    detail_data_ia.append({
                        'id': ia_item.id,
                        'product_mapped': item.product_data,
                        'uom_mapped': item.uom_data,
                        'warehouse_mapped': item.warehouse_data,
                        'sum_quantity': ia_item.book_quantity - ia_item.count,
                        'before_quantity': ia_item.issued_quantity,
                        'remain_quantity': ia_item.book_quantity - ia_item.count - ia_item.issued_quantity,
                        'issued_quantity': item.issued_quantity,
                        'lot_data': item.lot_data,
                        'sn_data': item.sn_data
                    })
        return detail_data_ia

    @classmethod
    def get_production_order(cls, obj):
        return {
            'id': obj.production_order_id,
            'title': obj.production_order.title,
            'code': obj.production_order.code,
        } if obj.production_order else {}

    @classmethod
    def get_detail_data_po(cls, obj):
        detail_data_po = []
        if obj.production_order:
            if obj.system_status == 3:
                for item in obj.goods_issue_product.filter(issued_quantity__gt=0):
                    po_item = item.production_order_item
                    detail_data_po.append({
                        'id': po_item.id,
                        'product_mapped': item.product_data,
                        'uom_mapped': item.uom_data,
                        'warehouse_mapped': item.warehouse_data,
                        'sum_quantity': po_item.quantity,
                        'before_quantity': item.before_quantity,
                        'remain_quantity': item.remain_quantity,
                        'issued_quantity': item.issued_quantity,
                        'lot_data': item.lot_data,
                        'sn_data': item.sn_data
                    })
            else:
                for item in obj.goods_issue_product.all():
                    po_item = item.production_order_item
                    detail_data_po.append({
                        'id': po_item.id,
                        'product_mapped': item.product_data,
                        'uom_mapped': item.uom_data,
                        'warehouse_mapped': item.warehouse_data,
                        'sum_quantity': po_item.quantity,
                        'before_quantity': po_item.issued_quantity,
                        'remain_quantity': po_item.quantity - po_item.issued_quantity,
                        'issued_quantity': item.issued_quantity,
                        'lot_data': item.lot_data,
                        'sn_data': item.sn_data
                    })
        return detail_data_po


class GoodsIssueUpdateSerializer(AbstractCreateSerializerModel):
    goods_issue_type = serializers.IntegerField()
    inventory_adjustment_id = serializers.UUIDField(required=False, allow_null=True)
    detail_data_ia = serializers.ListField()
    production_order_id = serializers.UUIDField(required=False, allow_null=True)
    detail_data_po = serializers.ListField()

    class Meta:
        model = GoodsIssue
        fields = (
            'title',
            'note',
            'goods_issue_type',
            'inventory_adjustment_id',
            'detail_data_ia',
            'production_order_id',
            'detail_data_po'
        )

    def validate(self, validate_data):
        GoodsIssueCommonFunction.validate_goods_issue_type(validate_data)
        GoodsIssueCommonFunction.validate_inventory_adjustment_id(validate_data)
        GoodsIssueCommonFunction.validate_detail_data_ia(validate_data)
        GoodsIssueCommonFunction.validate_production_order_id(validate_data)
        GoodsIssueCommonFunction.validate_detail_data_po(validate_data)
        print('*validate done')
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        detail_data_ia = validated_data.pop('detail_data_ia', [])
        detail_data_po = validated_data.pop('detail_data_po', [])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        GoodsIssueCommonFunction.create_issue_item(instance, detail_data_ia)
        GoodsIssueCommonFunction.create_issue_item(instance, detail_data_po)
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
        if validate_data.get('inventory_adjustment_id'):
            try:
                validate_data['inventory_adjustment_id'] = str(InventoryAdjustment.objects.get(
                    id=validate_data.get('inventory_adjustment_id')
                ).id)
            except InventoryAdjustment.DoesNotExist:
                raise serializers.ValidationError({'inventory_adjustment': 'Inventory adjustment is not exist'})
        else:
            validate_data['inventory_adjustment_id'] = None
        print('2. validate_inventory_adjustment_id  --- ok')
        return True

    @classmethod
    def validate_production_order_id(cls, validate_data):
        if validate_data.get('production_order_id'):
            try:
                validate_data['production_order_id'] = str(ProductionOrder.objects.get(
                    id=validate_data.get('production_order_id')
                ).id)
            except ProductionOrderTask.DoesNotExist:
                raise serializers.ValidationError({'production_order': 'Product order is not exist'})
        else:
            validate_data['production_order_id'] = None
        print('2. validate_production_order_id  --- ok')
        return True

    @classmethod
    def validate_sn_data(cls, item, product_obj):
        serial_list = ProductWareHouseSerial.objects.filter(id__in=item.get('sn_data', []), is_delete=False)
        if serial_list.count() != len(item.get('sn_data', [])):
            raise serializers.ValidationError(
                {'sn_data': f"[{product_obj.title}] Some selected serials aren't currently in any warehouse."}
            )
        return True

    @classmethod
    def validate_lot_data(cls, item, product_obj):
        lot_id_list = []
        lot_data = []
        for lot in item.get('lot', []):
            if lot.get('lot_id') not in lot_id_list:
                lot_obj = ProductWareHouseLot.objects.filter(id=lot.get('lot_id')).first()
                if lot_obj:
                    lot_id_list.append(lot_obj.id)
                    lot_data.append(
                        {'lot_id': lot.get('lot_id'), 'lot_quantity': lot_obj, 'issued_quantity': lot.get('quantity')})
                else:
                    raise serializers.ValidationError({'error': "Lot object is not exist."})
            else:
                for data in lot_data:
                    if data['lot_id'] == lot.get('lot_id'):
                        data['issued_quantity'] += lot.get('quantity')
                        break
        for data in lot_data:
            if data.get('lot_quantity', 0) < data.get('issued_quantity', 0):
                raise serializers.ValidationError(
                    {'error': f"[{product_obj.title}] Issued quantity can't > lot quantity."})
        return True

    @classmethod
    def validate_detail_data_ia(cls, validate_data):
        detail_data_ia = validate_data.get('detail_data_ia', [])
        for item in detail_data_ia:
            product_obj = Product.objects.filter(id=item.get('product_id')).first()
            warehouse_obj = WareHouse.objects.filter(id=item.get('warehouse_id')).first()
            uom_obj = UnitOfMeasure.objects.filter(id=item.get('uom_id')).first()
            prd_wh_obj = ProductWareHouse.objects.filter(product=product_obj, warehouse=warehouse_obj).first()
            ia_item_obj = InventoryAdjustmentItem.objects.filter(id=item.get('inventory_adjustment_item_id')).first()
            if prd_wh_obj and warehouse_obj and uom_obj and prd_wh_obj and ia_item_obj:
                if prd_wh_obj.stock_amount < float(item.get('issued_quantity')):
                    raise serializers.ValidationError({'issued_quantity': "Issue quantity can't > stock quantity."})
                if (
                        ia_item_obj.book_quantity - ia_item_obj.count - ia_item_obj.issued_quantity
                ) < float(item.get('issued_quantity')):
                    raise serializers.ValidationError({'issued_quantity': "Issue quantity can't > remain quantity."})

                cls.validate_sn_data(item, product_obj)
                cls.validate_lot_data(item, product_obj)

                item['inventory_adjustment_item_id'] = str(ia_item_obj.id)
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
                item['uom_id'] = str(uom_obj.id)
                item['uom_data'] = {
                    'id': str(uom_obj.id),
                    'code': uom_obj.code,
                    'title': uom_obj.title
                }
            else:
                raise serializers.ValidationError({'error': "Some objects are not exist."})
        validate_data['detail_data_ia'] = detail_data_ia
        print('3. validate_detail_data_ia --- ok')
        return True

    @classmethod
    def validate_detail_data_po(cls, validate_data):
        detail_data_po = validate_data.get('detail_data_po', [])
        for item in detail_data_po:
            product_obj = Product.objects.filter(id=item.get('product_id')).first()
            warehouse_obj = WareHouse.objects.filter(id=item.get('warehouse_id')).first()
            uom_obj = UnitOfMeasure.objects.filter(id=item.get('uom_id')).first()
            prd_wh_obj = ProductWareHouse.objects.filter(product=product_obj, warehouse=warehouse_obj).first()
            po_item_obj = ProductionOrderTask.objects.filter(id=item.get('production_order_item_id')).first()
            if prd_wh_obj and warehouse_obj and uom_obj and prd_wh_obj and po_item_obj:
                if prd_wh_obj.stock_amount < float(item.get('issued_quantity')):
                    raise serializers.ValidationError({'issued_quantity': f"[{product_obj.title}] Issue quantity can't > stock quantity."})
                if po_item_obj.quantity - po_item_obj.issued_quantity < float(item.get('issued_quantity')):
                    raise serializers.ValidationError({'issued_quantity': f"[{product_obj.title}] Issue quantity can't > remain quantity."})

                cls.validate_sn_data(item, product_obj)
                cls.validate_lot_data(item, product_obj)

                item['production_order_item_id'] = str(po_item_obj.id)
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
                item['uom_id'] = str(uom_obj.id)
                item['uom_data'] = {
                    'id': str(uom_obj.id),
                    'code': uom_obj.code,
                    'title': uom_obj.title
                }
            else:
                raise serializers.ValidationError({'error': "Some objects are not exist."})
        validate_data['detail_data_po'] = detail_data_po
        print('3. validate_detail_data_po --- ok')
        return True

    @classmethod
    def create_issue_item(cls, instance, data):
        if len(data) > 0:
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
            if item.book_quantity - item.count - item.issued_quantity > 0:
                ia_data.append({
                    'id': item.id,
                    'order': order,
                    'product_mapped': {
                        'id': item.product_mapped_data.get('id'),
                        'code': item.product_mapped_data.get('code'),
                        'title': item.product_mapped_data.get('title'),
                        'description': item.product_mapped_data.get('description'),
                        'general_traceability_method': item.product_mapped_data.get('general_traceability_method')
                    } if item.product_mapped else {},
                    'uom_mapped': {
                        'id': item.uom_mapped_data.get('id'),
                        'code': item.uom_mapped_data.get('code'),
                        'title': item.uom_mapped_data.get('title'),
                        'ratio': item.uom_mapped_data.get('ratio')
                    } if item.uom_mapped else {},
                    'warehouse_mapped': {
                        'id': item.warehouse_mapped_data.get('id'),
                        'code': item.warehouse_mapped_data.get('code'),
                        'title': item.warehouse_mapped_data.get('title')
                    } if item.warehouse_mapped else {},
                    'sum_quantity': item.book_quantity - item.count,
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
        for item in obj.po_task_production_order.filter(is_task=False).order_by('product__code'):
            if item.quantity - item.issued_quantity > 0:
                task_data.append({
                    'id': item.id,
                    'order': item.order,
                    'product_mapped': {
                        'id': item.product_data.get('id'),
                        'code': item.product_data.get('code'),
                        'title': item.product_data.get('title'),
                        'description': item.product_data.get('description'),
                        'general_traceability_method': item.product.general_traceability_method
                    } if item.product else {},
                    'uom_mapped': {
                        'id': item.uom_data.get('id'),
                        'code': item.uom_data.get('code'),
                        'title': item.uom_data.get('title'),
                        'ratio': item.uom_data.get('ratio')
                    } if item.uom else {},
                    'warehouse_mapped': {
                        'id': item.warehouse_data.get('id'),
                        'code': item.warehouse_data.get('code'),
                        'title': item.warehouse_data.get('title')
                    } if item.warehouse else {},
                    'is_all_warehouse': item.is_all_warehouse,
                    'sum_quantity': item.quantity,
                    'before_quantity': item.issued_quantity,
                    'remain_quantity': item.quantity - item.issued_quantity,
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

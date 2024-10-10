from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.core.base.models import Application
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import (
    UnitOfMeasure, WareHouse, Product,
    ProductWareHouse, ProductWareHouseSerial, ProductWareHouseLot
)
from apps.sales.inventory.models import GoodsIssue, GoodsIssueProduct, InventoryAdjustmentItem, InventoryAdjustment
from apps.sales.inventory.models.goods_issue import GoodsIssueAttachmentFile
from apps.sales.production.models import ProductionOrder, ProductionOrderTask, WorkOrder, WorkOrderTask
from apps.shared import AbstractDetailSerializerModel, AbstractCreateSerializerModel, AbstractListSerializerModel, HRMsg

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
    'ProductWareHouseListSerializerForGIS',
    'WorkOrderListSerializerForGIS',
    'WorkOrderDetailSerializerForGIS',
    'GoodsIssueProductListSerializer',
]

from apps.shared.translations.base import AttachmentMsg


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
    work_order_id = serializers.UUIDField(required=False, allow_null=True)
    detail_data_wo = serializers.ListField()
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = GoodsIssue
        fields = (
            'title',
            'note',
            'goods_issue_type',
            'inventory_adjustment_id',
            'detail_data_ia',
            'production_order_id',
            'detail_data_po',
            'work_order_id',
            'detail_data_wo',
            'attachment'
        )

    def validate(self, validate_data):
        GoodsIssueCommonFunction.validate_goods_issue_type(validate_data)
        GoodsIssueCommonFunction.validate_inventory_adjustment_id(validate_data)
        GoodsIssueCommonFunction.validate_detail_data_ia(validate_data)
        GoodsIssueCommonFunction.validate_production_order_id(validate_data)
        GoodsIssueCommonFunction.validate_detail_data_po(validate_data)
        GoodsIssueCommonFunction.validate_work_order_id(validate_data)
        GoodsIssueCommonFunction.validate_detail_data_wo(validate_data)
        GoodsIssueCommonFunction.validate_attachment(
            context_user=self.context.get('user', None),
            doc_id=None,
            validate_data=validate_data
        )
        if 'title' in validate_data:
            if validate_data.get('title'):
                validate_data['title'] = validate_data.get('title')
            else:
                raise serializers.ValidationError({'title': "Title is not null"})
        print('*validate done')
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        detail_data_ia = validated_data.pop('detail_data_ia', [])
        detail_data_po = validated_data.pop('detail_data_po', [])
        detail_data_wo = validated_data.pop('detail_data_wo', [])
        attachment = validated_data.pop('attachment', [])

        instance = GoodsIssue.objects.create(**validated_data)

        GoodsIssueCommonFunction.create_issue_item(instance, detail_data_ia)
        GoodsIssueCommonFunction.create_issue_item(instance, detail_data_po)
        GoodsIssueCommonFunction.create_issue_item(instance, detail_data_wo)
        GoodsIssueCommonFunction.handle_attach_file(instance, attachment)
        return instance


class GoodsIssueDetailSerializer(AbstractDetailSerializerModel):
    inventory_adjustment = serializers.SerializerMethodField()
    detail_data_ia = serializers.SerializerMethodField()
    production_order = serializers.SerializerMethodField()
    detail_data_po = serializers.SerializerMethodField()
    work_order = serializers.SerializerMethodField()
    detail_data_wo = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()

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
            'work_order',
            'detail_data_wo',
            'date_created',
            'attachment'
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
                    remain_quantity = ia_item.book_quantity - ia_item.count - ia_item.issued_quantity
                    detail_data_ia.append({
                        'id': ia_item.id,
                        'product_mapped': item.product_data,
                        'uom_mapped': item.uom_data,
                        'warehouse_mapped': item.warehouse_data,
                        'sum_quantity': ia_item.book_quantity - ia_item.count,
                        'before_quantity': ia_item.issued_quantity,
                        'remain_quantity': remain_quantity,
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
            'type': 0
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
                    remain_quantity = po_item.quantity - po_item.issued_quantity
                    detail_data_po.append({
                        'id': po_item.id,
                        'product_mapped': item.product_data,
                        'uom_mapped': item.uom_data,
                        'warehouse_mapped': item.warehouse_data,
                        'sum_quantity': po_item.quantity,
                        'before_quantity': po_item.issued_quantity,
                        'remain_quantity': remain_quantity,
                        'issued_quantity': item.issued_quantity,
                        'lot_data': item.lot_data,
                        'sn_data': item.sn_data
                    })
        return detail_data_po

    @classmethod
    def get_work_order(cls, obj):
        return {
            'id': obj.work_order_id,
            'title': obj.work_order.title,
            'code': obj.work_order.code,
            'type': 1
        } if obj.work_order else {}

    @classmethod
    def get_detail_data_wo(cls, obj):
        detail_data_wo = []
        if obj.work_order:
            if obj.system_status == 3:
                for item in obj.goods_issue_product.filter(issued_quantity__gt=0):
                    wo_item = item.work_order_item
                    detail_data_wo.append({
                        'id': wo_item.id,
                        'product_mapped': item.product_data,
                        'uom_mapped': item.uom_data,
                        'warehouse_mapped': item.warehouse_data,
                        'sum_quantity': wo_item.quantity,
                        'before_quantity': item.before_quantity,
                        'remain_quantity': item.remain_quantity,
                        'issued_quantity': item.issued_quantity,
                        'lot_data': item.lot_data,
                        'sn_data': item.sn_data
                    })
            else:
                for item in obj.goods_issue_product.all():
                    wo_item = item.work_order_item
                    remain_quantity = wo_item.quantity - wo_item.issued_quantity
                    detail_data_wo.append({
                        'id': wo_item.id,
                        'product_mapped': item.product_data,
                        'uom_mapped': item.uom_data,
                        'warehouse_mapped': item.warehouse_data,
                        'sum_quantity': wo_item.quantity,
                        'before_quantity': wo_item.issued_quantity,
                        'remain_quantity': remain_quantity,
                        'issued_quantity': item.issued_quantity,
                        'lot_data': item.lot_data,
                        'sn_data': item.sn_data
                    })
        return detail_data_wo

    @classmethod
    def get_attachment(cls, obj):
        att_objs = GoodsIssueAttachmentFile.objects.select_related('attachment').filter(goods_issue=obj)
        return [item.attachment.get_detail() for item in att_objs]


class GoodsIssueUpdateSerializer(AbstractCreateSerializerModel):
    detail_data_ia = serializers.ListField()
    detail_data_po = serializers.ListField()
    detail_data_wo = serializers.ListField()
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)

    class Meta:
        model = GoodsIssue
        fields = (
            'title',
            'note',
            'detail_data_ia',
            'detail_data_po',
            'detail_data_wo',
            'attachment'
        )

    def validate(self, validate_data):
        GoodsIssueCommonFunction.validate_detail_data_ia(validate_data)
        GoodsIssueCommonFunction.validate_detail_data_po(validate_data)
        GoodsIssueCommonFunction.validate_detail_data_wo(validate_data)
        GoodsIssueCommonFunction.validate_attachment(
            context_user=self.context.get('user', None),
            doc_id=self.instance.id,
            validate_data=validate_data
        )
        if 'title' in validate_data:
            if validate_data.get('title'):
                validate_data['title'] = validate_data.get('title')
            else:
                raise serializers.ValidationError({'title': "Title is not null"})
        print('*validate done')
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        detail_data_ia = validated_data.pop('detail_data_ia', [])
        detail_data_po = validated_data.pop('detail_data_po', [])
        detail_data_wo = validated_data.pop('detail_data_wo', [])
        attachment = validated_data.pop('attachment', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        GoodsIssueCommonFunction.create_issue_item(instance, detail_data_ia)
        GoodsIssueCommonFunction.create_issue_item(instance, detail_data_po)
        GoodsIssueCommonFunction.create_issue_item(instance, detail_data_wo)
        GoodsIssueCommonFunction.handle_attach_file(instance, attachment)
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
                print('2. validate_inventory_adjustment_id  --- ok')
            except InventoryAdjustment.DoesNotExist:
                raise serializers.ValidationError({'inventory_adjustment': 'Inventory adjustment does not exist'})
        else:
            validate_data['inventory_adjustment_id'] = None
        return True

    @classmethod
    def validate_production_order_id(cls, validate_data):
        if validate_data.get('production_order_id'):
            try:
                validate_data['production_order_id'] = str(ProductionOrder.objects.get(
                    id=validate_data.get('production_order_id')
                ).id)
                print('2. validate_production_order_id  --- ok')
            except ProductionOrder.DoesNotExist:
                raise serializers.ValidationError({'production_order': 'Product order does not exist'})
        else:
            validate_data['production_order_id'] = None
        return True

    @classmethod
    def validate_work_order_id(cls, validate_data):
        if validate_data.get('work_order_id'):
            try:
                validate_data['work_order_id'] = str(WorkOrder.objects.get(
                    id=validate_data.get('work_order_id')
                ).id)
                print('2. validate_work_order_id  --- ok')
            except WorkOrder.DoesNotExist:
                raise serializers.ValidationError({'work_order': 'Work order does not exist'})
        else:
            validate_data['work_order_id'] = None
        return True

    @classmethod
    def validate_sn_data(cls, item, product_obj, selected_sn):
        serial_list = ProductWareHouseSerial.objects.filter(id__in=item.get('sn_data', []), is_delete=False)
        if serial_list.count() != len(item.get('sn_data', [])):
            raise serializers.ValidationError(
                {'sn_data': f"[{product_obj.title}] Some selected serials aren't currently in any warehouse."}
            )

        for serial in serial_list:
            if serial.id in selected_sn:
                raise serializers.ValidationError(
                    {'duplicated_sn': f"[{product_obj.title}] Some serials are selected in different rows."}
                )
            selected_sn.append(serial.id)
        return selected_sn

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
                    raise serializers.ValidationError({'error': "Lot object does not exist."})
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
        if len(detail_data_ia) > 0:
            selected_sn = []
            for item in detail_data_ia:
                if all([
                    float(item.get('issued_quantity', 0)) > 0,
                    item.get('product_id'),
                    item.get('warehouse_id'),
                    item.get('uom_id'),
                    item.get('inventory_adjustment_item_id')
                ]):
                    product_obj = Product.objects.filter(id=item.get('product_id')).first()
                    warehouse_obj = WareHouse.objects.filter(id=item.get('warehouse_id')).first()
                    uom_obj = UnitOfMeasure.objects.filter(id=item.get('uom_id')).first()
                    prd_wh_obj = ProductWareHouse.objects.filter(product=product_obj, warehouse=warehouse_obj).first()
                    ia_item_obj = InventoryAdjustmentItem.objects.filter(
                        id=item.get('inventory_adjustment_item_id')
                    ).first()
                    if prd_wh_obj and warehouse_obj and uom_obj and prd_wh_obj and ia_item_obj:
                        if prd_wh_obj.stock_amount < float(item.get('issued_quantity', 0)):
                            raise serializers.ValidationError({'issued_quantity': "Issue quantity can't > stock quantity."})
                        if (
                                ia_item_obj.book_quantity - ia_item_obj.count - ia_item_obj.issued_quantity
                        ) < float(item.get('issued_quantity', 0)):
                            raise serializers.ValidationError(
                                {'issued_quantity': "Issue quantity can't > remain quantity."}
                            )

                        selected_sn = cls.validate_sn_data(item, product_obj, selected_sn)
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
            print('3. validate_detail_data_ia --- ok')
        validate_data['detail_data_ia'] = detail_data_ia
        return True

    @classmethod
    def validate_detail_data_po(cls, validate_data):
        detail_data_po = validate_data.get('detail_data_po', [])
        if len(detail_data_po) > 0:
            selected_sn = []
            for item in detail_data_po:
                if all([
                    float(item.get('issued_quantity', 0)) > 0,
                    item.get('product_id'),
                    item.get('warehouse_id'),
                    item.get('uom_id'),
                    item.get('production_order_item_id')
                ]):
                    product_obj = Product.objects.filter(id=item.get('product_id')).first()
                    warehouse_obj = WareHouse.objects.filter(id=item.get('warehouse_id')).first()
                    uom_obj = UnitOfMeasure.objects.filter(id=item.get('uom_id')).first()
                    prd_wh_obj = ProductWareHouse.objects.filter(product=product_obj, warehouse=warehouse_obj).first()
                    po_item_obj = ProductionOrderTask.objects.filter(id=item.get('production_order_item_id')).first()
                    if prd_wh_obj and warehouse_obj and uom_obj and prd_wh_obj and po_item_obj:
                        if prd_wh_obj.stock_amount < float(item.get('issued_quantity', 0)):
                            raise serializers.ValidationError(
                                {'issued_quantity': f"[{product_obj.title}] Issue quantity can't > stock quantity."}
                            )

                        selected_sn = cls.validate_sn_data(item, product_obj, selected_sn)
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
            print('3. validate_detail_data_po --- ok')
        validate_data['detail_data_po'] = detail_data_po
        return True

    @classmethod
    def validate_detail_data_wo(cls, validate_data):
        detail_data_wo = validate_data.get('detail_data_wo', [])
        if len(detail_data_wo) > 0:
            selected_sn = []
            for item in detail_data_wo:
                if all([
                    float(item.get('issued_quantity', 0)) > 0,
                    item.get('product_id'),
                    item.get('warehouse_id'),
                    item.get('uom_id'),
                    item.get('work_order_item_id')
                ]):
                    product_obj = Product.objects.filter(id=item.get('product_id')).first()
                    warehouse_obj = WareHouse.objects.filter(id=item.get('warehouse_id')).first()
                    uom_obj = UnitOfMeasure.objects.filter(id=item.get('uom_id')).first()
                    prd_wh_obj = ProductWareHouse.objects.filter(product=product_obj, warehouse=warehouse_obj).first()
                    wo_item_obj = WorkOrderTask.objects.filter(id=item.get('work_order_item_id')).first()
                    if prd_wh_obj and warehouse_obj and uom_obj and prd_wh_obj and wo_item_obj:
                        if prd_wh_obj.stock_amount < float(item.get('issued_quantity', 0)):
                            raise serializers.ValidationError(
                                {'issued_quantity': f"[{product_obj.title}] Issue quantity can't > stock quantity."}
                            )

                        selected_sn = cls.validate_sn_data(item, product_obj, selected_sn)
                        cls.validate_lot_data(item, product_obj)

                        item['work_order_item_id'] = str(wo_item_obj.id)
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
            print('3. validate_detail_data_wo --- ok')
        validate_data['detail_data_wo'] = detail_data_wo
        return True

    @classmethod
    def validate_attachment(cls, context_user, doc_id, validate_data):
        if 'attachment' in validate_data:
            if validate_data.get('attachment'):
                if context_user and hasattr(context_user, 'employee_current_id'):
                    state, result = GoodsIssueAttachmentFile.valid_change(
                        current_ids=validate_data.get('attachment', []),
                        employee_id=context_user.employee_current_id,
                        doc_id=doc_id
                    )
                    if state is True:
                        validate_data['attachment'] = result
                    else:
                        raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
                else:
                    raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})
        print('4. validate_attachment --- ok')
        return validate_data

    @classmethod
    def create_issue_item(cls, instance, data):
        if len(data) > 0:
            bulk_data = []
            for item in data:
                if float(item.get('issued_quantity', 0)) > 0:
                    bulk_data.append(GoodsIssueProduct(goods_issue=instance, **item))
            GoodsIssueProduct.objects.filter(goods_issue=instance).delete()
            GoodsIssueProduct.objects.bulk_create(bulk_data)
        return True

    @classmethod
    def handle_attach_file(cls, instance, attachment_result):
        if attachment_result and isinstance(attachment_result, dict):
            relate_app = Application.objects.filter(id="f26d7ce4-e990-420a-8ec6-2dc307467f2c").first()
            if relate_app:
                state = GoodsIssueAttachmentFile.resolve_change(
                    result=attachment_result, doc_id=instance.id, doc_app=relate_app,
                )
                if state:
                    return True
            raise serializers.ValidationError({'attachment': AttachmentMsg.ERROR_VERIFY})
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
                remain_quantity = item.book_quantity - item.count - item.issued_quantity
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
                    'remain_quantity': remain_quantity,
                })
                order += 1
        return ia_data


class ProductionOrderListSerializerForGIS(AbstractListSerializerModel):
    app = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = ProductionOrder
        fields = (
            'id',
            'title',
            'code',
            'app',
            'type'
        )

    @classmethod
    def get_app(cls, obj):
        return _('Production Order') if obj else ''

    @classmethod
    def get_type(cls, obj):
        return 0 if obj else None


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
            remain_quantity = item.quantity - item.issued_quantity
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
                'remain_quantity': remain_quantity,
            })
        return task_data


class WorkOrderListSerializerForGIS(AbstractListSerializerModel):
    app = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = (
            'id',
            'title',
            'code',
            'app',
            'type'
        )

    @classmethod
    def get_app(cls, obj):
        return _('Work Order') if obj else ''

    @classmethod
    def get_type(cls, obj):
        return 1 if obj else None


class WorkOrderDetailSerializerForGIS(AbstractDetailSerializerModel):
    task_data = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = (
            'id',
            'title',
            'task_data'
        )

    @classmethod
    def get_task_data(cls, obj):
        task_data = []
        for item in obj.wo_task_work_order.filter(is_task=False).order_by('product__code'):
            remain_quantity = item.quantity - item.issued_quantity
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
                'remain_quantity': remain_quantity,
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


class GoodsIssueProductListSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsIssueProduct
        fields = (
            'id',
            'issued_quantity',
        )

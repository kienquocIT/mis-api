from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.masterdata.saledata.models import ProductWareHouse, ProductWareHouseLot, ProductWareHouseSerial
from apps.sales.inventory.models import InventoryAdjustment, GoodsIssueProduct
from apps.sales.production.models import ProductionOrder, WorkOrder
from apps.sales.productmodification.models import ProductModification
from apps.shared import AbstractDetailSerializerModel, AbstractListSerializerModel


__all__ = [
    'ProductionOrderListSerializerForGIS',
    'ProductionOrderDetailSerializerForGIS',
    'InventoryAdjustmentListSerializerForGIS',
    'InventoryAdjustmentDetailSerializerForGIS',
    'ProductWarehouseSerialListSerializerForGIS',
    'ProductWarehouseLotListSerializerForGIS',
    'ProductWareHouseListSerializerForGIS',
    'WorkOrderListSerializerForGIS',
    'WorkOrderDetailSerializerForGIS',
    'ProductModificationListSerializerForGIS',
    'ProductModificationDetailSerializerForGIS',
    'GoodsIssueProductListSerializer',
]


# related serializers
class InventoryAdjustmentListSerializerForGIS(AbstractListSerializerModel):
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = InventoryAdjustment
        fields = (
            'id',
            'title',
            'code',
            'employee_created',
            'date_created'
        )

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}


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
    employee_created = serializers.SerializerMethodField()
    app = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = ProductionOrder
        fields = (
            'id',
            'title',
            'code',
            'app',
            'type',
            'employee_created',
            'date_created'
        )

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}

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
    employee_created = serializers.SerializerMethodField()
    app = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = (
            'id',
            'title',
            'code',
            'app',
            'type',
            'employee_created',
            'date_created'
        )

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}

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


class ProductModificationListSerializerForGIS(AbstractListSerializerModel):
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = ProductModification
        fields = (
            'id',
            'title',
            'code',
            'employee_created',
            'date_created'
        )

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}


class ProductModificationDetailSerializerForGIS(AbstractDetailSerializerModel):
    representative_product_modified = serializers.SerializerMethodField()

    class Meta:
        model = ProductModification
        fields = (
            'id',
            'title',
            'representative_product_modified'
        )

    @classmethod
    def get_representative_product_modified(cls, obj):
        return {
            'id': str(obj.representative_product_modified_id),
            'code': obj.representative_product_modified.code,
            'title': obj.representative_product_modified.title,
            'description': obj.representative_product_modified.description,
            'general_traceability_method': obj.representative_product_modified.general_traceability_method,
            'valuation_method': obj.representative_product_modified.valuation_method,
            'uom_mapped': {
                'id': str(obj.representative_product_modified.general_uom_group.uom_reference_id),
                'code': obj.representative_product_modified.general_uom_group.uom_reference.code,
                'title': obj.representative_product_modified.general_uom_group.uom_reference.title,
            } if obj.representative_product_modified.general_uom_group else {}
        } if obj.representative_product_modified else {}


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

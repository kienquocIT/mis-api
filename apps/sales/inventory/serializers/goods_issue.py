from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import UnitOfMeasure, WareHouse, ProductWareHouse
from apps.sales.inventory.models import GoodsIssue, GoodsIssueProduct, InventoryAdjustmentItem, InventoryAdjustment
from apps.shared import ProductMsg, WarehouseMsg, GOODS_ISSUE_TYPE, SYSTEM_STATUS, AbstractDetailSerializerModel
from apps.shared.translations.goods_issue import GIMsg

__all__ = [
    'GoodsIssueListSerializer',
    'GoodsIssueCreateSerializer',
    'GoodsIssueDetailSerializer',
    'GoodsIssueUpdateSerializer'
]


class GoodsIssueProductSerializer(serializers.ModelSerializer):
    warehouse = serializers.UUIDField()
    uom = serializers.UUIDField()
    product_warehouse = serializers.UUIDField()
    inventory_adjustment_item = serializers.UUIDField(allow_null=True)
    sn_changes = serializers.ListField(default=[])
    lot_changes = serializers.ListField(default=[])

    class Meta:
        model = GoodsIssueProduct
        fields = (
            'inventory_adjustment_item',
            'product_warehouse',
            'warehouse',
            'uom',
            'description',
            'quantity',
            'unit_cost',
            'subtotal',
            'sn_changes',
            'lot_changes'
        )

    @classmethod
    def validate_inventory_adjustment_item(cls, value):
        if value:
            try:
                InventoryAdjustmentItem.objects.get(id=value)
                return str(value)
            except ProductWareHouse.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        'inventory_adjustment_item': GIMsg.IA_PRODUCT_NOT_EXIST
                    }
                )
        return None

    @classmethod
    def validate_product_warehouse(cls, value):
        try:  # noqa
            obj = ProductWareHouse.objects.select_related('product').get(id=value)
            return {
                'id': str(obj.id),
                'product_general_traceability_method': obj.product.general_traceability_method,
                'product_data': {
                    'id': str(obj.product_id),
                    'title': obj.product.title,
                    'code': obj.product.code,
                }

            }
        except ProductWareHouse.DoesNotExist:
            raise serializers.ValidationError(
                {
                    'warehouse_product': WarehouseMsg.PRODUCT_NOT_EXIST
                }
            )

    @classmethod
    def validate_warehouse(cls, value):
        try:
            warehouse = WareHouse.objects.get(id=value)
            return {
                'id': str(warehouse.id),
                'title': warehouse.title,
                'code': warehouse.code,
            }
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError(
                {
                    'end_warehouse': WarehouseMsg.END_WAREHOUSE_NOT_EXIST
                }
            )

    @classmethod
    def validate_uom(cls, value):
        try:
            uom = UnitOfMeasure.objects.get(id=value)
            return {
                'id': str(uom.id),
                'title': uom.title,
                'code': uom.code,
            }
        except UnitOfMeasure.DoesNotExist:
            raise serializers.ValidationError(
                {
                    'unit_of_measure': ProductMsg.UNIT_OF_MEASURE_NOT_EXIST
                }
            )


class GoodsIssueListSerializer(serializers.ModelSerializer):
    goods_issue_type = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()

    class Meta:
        model = GoodsIssue
        fields = (
            'id',
            'code',
            'title',
            'date_issue',
            'goods_issue_type',
            'system_status'
        )

    @classmethod
    def get_goods_issue_type(cls, obj):
        return str(dict(GOODS_ISSUE_TYPE).get(obj.goods_issue_type))

    @classmethod
    def get_system_status(cls, obj):
        if obj.system_status or obj.system_status == 0:
            return dict(SYSTEM_STATUS).get(obj.system_status)
        return None


class GoodsIssueCreateSerializer(serializers.ModelSerializer):
    goods_issue_datas = serializers.ListField(child=GoodsIssueProductSerializer())
    inventory_adjustment = serializers.UUIDField(required=False)

    class Meta:
        model = GoodsIssue
        fields = (
            'title',
            'date_issue',
            'note',
            'goods_issue_type',
            'inventory_adjustment',
            'goods_issue_datas',
            'system_status'
        )

    @classmethod
    def validate_inventory_adjustment(cls, value):
        try:
            return InventoryAdjustment.objects.get(id=value)
        except InventoryAdjustment.DoesNotExist:
            raise serializers.ValidationError(
                {
                    'inventory_adjustment': GIMsg.IA_NOT_EXIST
                }
            )

    @classmethod
    def common_create_sub_goods_issue(cls, instance, data):
        bulk_data = []
        for item in data:
            obj = GoodsIssueProduct(
                goods_issue=instance,
                inventory_adjustment_item_id=item['inventory_adjustment_item'],
                warehouse_id=item['warehouse']['id'],
                description=item['description'],
                warehouse_title=item['warehouse']['title'],
                product_warehouse_id=item['product_warehouse']['id'],
                product_id=item['product_warehouse']['product_data']['id'],
                product_title=item['product_warehouse']['product_data']['title'],
                uom_id=item['uom']['id'],
                uom_title=item['uom']['title'],
                quantity=item['quantity'],
                unit_cost=item['unit_cost'],
                subtotal=item['subtotal'],
                company=instance.company,
                tenant=instance.tenant,
                lot_data=item['lot_changes'],
                sn_data=item['sn_changes']
            )
            bulk_data.append(obj)
        GoodsIssueProduct.objects.filter(goods_issue=instance).delete()
        GoodsIssueProduct.objects.bulk_create(bulk_data)
        return True

    @decorator_run_workflow
    def create(self, validated_data):
        instance = GoodsIssue.objects.create(**validated_data)
        self.common_create_sub_goods_issue(instance, validated_data['goods_issue_datas'])
        return instance


class GoodsIssueDetailSerializer(AbstractDetailSerializerModel):
    inventory_adjustment = serializers.SerializerMethodField()
    goods_issue_datas = serializers.SerializerMethodField()

    class Meta:
        model = GoodsIssue
        fields = (
            'id',
            'code',
            'title',
            'date_issue',
            'note',
            'goods_issue_type',
            'goods_issue_datas',
            'inventory_adjustment',
            'system_status',
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
    def get_goods_issue_datas(cls, obj):
        return [{
            'id': item.inventory_adjustment_item.id,
            'product_warehouse': {
                'id': item.product_warehouse_id,
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
                }
            },
            'quantity': item.quantity,
            'unit_cost': item.unit_cost,
            'subtotal': item.subtotal,
            'lot_data': item.lot_data,
            'sn_data': item.sn_data
        } for item in obj.goods_issue_product.all()]


class GoodsIssueUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    note = serializers.CharField(required=False, allow_blank=True)
    goods_issue_datas = serializers.ListField(child=GoodsIssueProductSerializer())

    class Meta:
        model = GoodsIssue
        fields = (
            'title',
            'note',
            'goods_issue_datas',
            'system_status'
        )

    @classmethod
    def validate_inventory_adjustment(cls, value):
        try:
            return InventoryAdjustment.objects.get(id=value)
        except InventoryAdjustment.DoesNotExist:
            raise serializers.ValidationError({'inventory_adjustment': GIMsg.IA_NOT_EXIST})

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        GoodsIssueCreateSerializer.common_create_sub_goods_issue(instance, validated_data['goods_issue_datas'])
        return instance

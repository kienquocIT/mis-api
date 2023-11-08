from rest_framework import serializers

from apps.masterdata.saledata.models import UnitOfMeasure, WareHouse, ProductWareHouse
from apps.sales.inventory.models import GoodsIssue, GoodsIssueProduct, InventoryAdjustmentItem, InventoryAdjustment

__all__ = ['GoodsIssueListSerializer', 'GoodsIssueDetailSerializer', 'GoodsIssueCreateSerializer']

from apps.shared import ProductMsg, WarehouseMsg, GOODS_ISSUE_TYPE, SYSTEM_STATUS
from apps.shared.translations.goods_issue import GIMsg


class GoodsIssueProductSerializer(serializers.ModelSerializer):
    warehouse = serializers.UUIDField()
    uom = serializers.UUIDField()
    product_warehouse = serializers.UUIDField()
    inventory_adjustment_item = serializers.UUIDField(allow_null=True)

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
        return str(dict(SYSTEM_STATUS).get(obj.system_status))


class GoodsIssueDetailSerializer(serializers.ModelSerializer):
    inventory_adjustment = serializers.SerializerMethodField()
    system_status = serializers.SerializerMethodField()

    class Meta:
        model = GoodsIssue
        fields = (
            'id',
            'code',
            'title',
            'date_issue',
            'note',
            'goods_issue_type',
            'system_status',
            'goods_issue_datas',
            'inventory_adjustment',
        )

    @classmethod
    def get_system_status(cls, obj):
        return str(dict(SYSTEM_STATUS).get(obj.system_status))

    @classmethod
    def get_inventory_adjustment(cls, obj):
        if obj.inventory_adjustment:
            return {
                'id': obj.inventory_adjustment_id,
                'title': obj.inventory_adjustment.title,
                'code': obj.inventory_adjustment.code,
            }
        return {}


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
    def update_product_amount(cls, data):
        ProductWareHouse.pop_from_transfer(
            instance_id=data['product_warehouse']['id'],
            amount=data['quantity'],
        )
        return True

    @classmethod
    def update_status_inventory_adjustment_item(cls, item_id, value):
        item = InventoryAdjustmentItem.objects.get(id=item_id)
        item.action_status = value
        item.save(update_fields=['action_status'])
        return True

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
                tenant=instance.tenant
            )
            bulk_data.append(obj)
            cls.update_product_amount(item)
            if item['inventory_adjustment_item']:
                cls.update_status_inventory_adjustment_item(item['inventory_adjustment_item'], True)
        GoodsIssueProduct.objects.bulk_create(bulk_data)

        return True

    def create(self, validated_data):
        instance = GoodsIssue.objects.create(**validated_data)
        self.common_create_sub_goods_issue(instance, validated_data['goods_issue_datas'])
        return instance


class GoodsIssueUpdateSerializer(serializers.ModelSerializer):
    goods_issue_datas = serializers.ListField(child=GoodsIssueProductSerializer(), required=False)
    inventory_adjustment = serializers.UUIDField(required=False)
    title = serializers.CharField(required=False)
    date_issue = serializers.DateTimeField(required=False)
    goods_issue_type = serializers.IntegerField(required=False)
    note = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = GoodsIssue
        fields = (
            'title',
            'date_issue',
            'note',
            'goods_issue_type',
            'inventory_adjustment',
            'goods_issue_datas',
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
    def revert_stock_amount(cls, instance):
        objs = GoodsIssueProduct.objects.select_related('product_warehouse').filter(goods_issue=instance)
        for item in objs:
            item.product_warehouse.stock_amount += item.quantity
            item.product_warehouse.save(update_fields=['stock_amount'])
            if item.inventory_adjustment_item:
                item.inventory_adjustment_item.action_status = False
                item.inventory_adjustment_item.save(update_fields=['action_status'])
        objs.delete()
        return True

    def update(self, instance, validated_data):
        if 'goods_issue_datas' in validated_data:
            self.revert_stock_amount(instance)
            GoodsIssueCreateSerializer.common_create_sub_goods_issue(instance, validated_data['goods_issue_datas'])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

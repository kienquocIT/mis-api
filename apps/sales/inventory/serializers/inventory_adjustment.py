from django.utils import timezone
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
# from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.inventory.models import (
    InventoryAdjustment, InventoryAdjustmentWarehouse, InventoryAdjustmentEmployeeInCharge,
    InventoryAdjustmentItem
)


def create_inventory_adjustment_warehouses(obj, data):
    bulk_info = []
    for wh_id in data:
        bulk_info.append(
            InventoryAdjustmentWarehouse(
                warehouse_mapped_id=wh_id,
                inventory_adjustment_mapped=obj,
            )
        )
    InventoryAdjustmentWarehouse.objects.filter(inventory_adjustment_mapped=obj).delete()
    InventoryAdjustmentWarehouse.objects.bulk_create(bulk_info)
    return True


def create_inventory_adjustment_employees_in_charge(obj, data):
    bulk_info = []
    for em_id in data:
        bulk_info.append(InventoryAdjustmentEmployeeInCharge(employee_mapped_id=em_id, inventory_adjustment_mapped=obj))
    InventoryAdjustmentEmployeeInCharge.objects.filter(inventory_adjustment_mapped=obj).delete()
    InventoryAdjustmentEmployeeInCharge.objects.bulk_create(bulk_info)
    return True


def create_inventory_adjustment_items(obj, data):
    bulk_info = []
    for item in data:
        difference_quantity = int(item.get('count', 0)) - item.get('book_quantity', 0)
        bulk_info.append(
            InventoryAdjustmentItem(
                **item,
                inventory_adjustment_mapped=obj,
                tenant=obj.tenant,
                company=obj.company,
                gr_remain_quantity=difference_quantity if difference_quantity > 0 else 0
            )
        )
    InventoryAdjustmentItem.objects.filter(inventory_adjustment_mapped=obj).delete()
    InventoryAdjustmentItem.objects.bulk_create(bulk_info)
    return True


def update_inventory_adjustment_items(obj, data):
    for item in data:
        item_obj = obj.inventory_adjustment_item_mapped.filter(id=item['id']).first()
        if item_obj:
            item_obj.count = item['count']
            item_obj.action_type = item['action_type']
            item_obj.select_for_action = item['select_for_action']
            item_obj.save(update_fields=['count', 'action_type', 'select_for_action'])
        else:
            raise serializers.ValidationError('Inventory Adjustment Item not exist')
    return True


class InventoryAdjustmentListSerializer(serializers.ModelSerializer):
    warehouses = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = InventoryAdjustment
        fields = (
            'id',
            'code',
            'title',
            'warehouses',
            'date_created',
            'state'
        )

    @classmethod
    def get_warehouses(cls, obj):
        all_item = obj.warehouses_mapped.all()
        data = []
        for item in all_item:
            data.append(
                {
                    'warehouse_id': str(item.id),
                    'warehouse_code': item.code,
                    'warehouse_title': item.title,
                }
            )
        return data

    @classmethod
    def get_state(cls, obj):
        if obj.state:
            return _("Finished")
        return _("Opening")


class InventoryAdjustmentDetailSerializer(serializers.ModelSerializer):
    warehouses = serializers.SerializerMethodField()
    employees_in_charge = serializers.SerializerMethodField()
    inventory_adjustment_item_mapped = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = InventoryAdjustment
        fields = (
            'id',
            'code',
            'title',
            'warehouses',
            'employees_in_charge',
            'inventory_adjustment_item_mapped',
            'date_created',
            'state'
        )

    @classmethod
    def get_warehouses(cls, obj):
        all_item = obj.warehouses_mapped.all()
        data = []
        for item in all_item:
            data.append(
                {
                    'id': str(item.id),
                    'code': item.code,
                    'title': item.title,
                }
            )
        return data

    @classmethod
    def get_employees_in_charge(cls, obj):
        all_item = obj.employees_in_charge_mapped.all()
        data = []
        for item in all_item:
            data.append(
                {
                    'id': str(item.id),
                    'code': item.code,
                    'full_name': item.get_full_name(2),
                }
            )
        return data

    @classmethod
    def get_inventory_adjustment_item_mapped(cls, obj):
        all_item = obj.inventory_adjustment_item_mapped.all()
        data = []
        for item in all_item:
            data.append(
                {
                    'id': item.id,
                    'product_warehouse_mapped': {
                        'id': item.product_warehouse_id,
                        'code': item.product_warehouse.code,
                        'title': item.product_warehouse.title
                    } if item.product_mapped else {},
                    'product_mapped': {
                        'id': item.product_mapped_id,
                        'code': item.product_mapped.code,
                        'title': item.product_mapped.title
                    } if item.product_mapped else {},
                    'warehouse_mapped': {
                        'id': item.warehouse_mapped_id,
                        'code': item.warehouse_mapped.code,
                        'title': item.warehouse_mapped.title
                    } if item.warehouse_mapped else {},
                    'uom_mapped': {
                        'id': item.uom_mapped_id,
                        'code': item.uom_mapped.code,
                        'title': item.uom_mapped.title
                    } if item.uom_mapped else {},
                    'book_quantity': item.book_quantity,
                    'count': item.count,
                    'select_for_action': item.select_for_action,
                    'action_status': item.action_status
                }
            )
        return data

    @classmethod
    def get_state(cls, obj):
        if obj.state:
            return _('Finished')
        return _('Opening')


class InventoryAdjustmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAdjustment
        fields = ('title',)

    def create(self, validated_data):
        if InventoryAdjustment.objects.filter_current(fill__tenant=True, fill__company=True).count() == 0:
            new_code = 'IA.0001'
        else:
            latest_code = InventoryAdjustment.objects.filter_current(
                fill__tenant=True, fill__company=True
            ).latest('date_created').code
            new_code = int(latest_code.split('.')[-1]) + 1
            new_code = 'IA.000' + str(new_code)

        obj = InventoryAdjustment.objects.create(**validated_data, code=new_code)
        create_inventory_adjustment_warehouses(obj, self.initial_data.get('ia_warehouses_data', []))
        create_inventory_adjustment_employees_in_charge(obj, self.initial_data.get('ia_employees_in_charge', []))
        create_inventory_adjustment_items(obj, self.initial_data.get('ia_items_data', []))
        return obj


class InventoryAdjustmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAdjustment
        fields = ()

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        create_inventory_adjustment_employees_in_charge(instance, self.initial_data.get('ia_employees_in_charge', []))
        update_inventory_adjustment_items(instance, self.initial_data.get('ia_items_data', []))
        instance.update_ia_state()
        return instance


class InventoryAdjustmentProductListSerializer(serializers.ModelSerializer):
    product_mapped = serializers.SerializerMethodField()
    warehouse_mapped = serializers.SerializerMethodField()
    uom_mapped = serializers.SerializerMethodField()

    class Meta:
        model = InventoryAdjustmentItem
        fields = (
            'id',
            'book_quantity',
            'count',
            'action_type',
            'inventory_adjustment_mapped',
            'product_warehouse',
            'product_mapped',
            'warehouse_mapped',
            'uom_mapped',
            'action_status',
        )

    @classmethod
    def get_product_mapped(cls, obj):
        if obj.product_mapped:
            return {
                'id': obj.product_mapped_id,
                'title': obj.product_mapped.title,
                'code': obj.product_mapped.code,
                'description': obj.product_mapped.description,
                'general_traceability_method': obj.product_mapped.general_traceability_method,
            }
        return {}

    @classmethod
    def get_warehouse_mapped(cls, obj):
        if obj.warehouse_mapped:
            return {
                'id': obj.warehouse_mapped_id,
                'title': obj.warehouse_mapped.title,
                'code': obj.warehouse_mapped.code,
            }
        return {}

    @classmethod
    def get_uom_mapped(cls, obj):
        if obj.uom_mapped:
            return {
                'id': obj.uom_mapped_id,
                'title': obj.uom_mapped.title,
                'code': obj.uom_mapped.code,
            }
        return {}


# Inventory adjustment list use for other apps
class InventoryAdjustmentOtherListSerializer(serializers.ModelSerializer):
    inventory_adjustment_product = serializers.SerializerMethodField()

    class Meta:
        model = InventoryAdjustment
        fields = (
            'id',
            'code',
            'title',
            'inventory_adjustment_product',
        )

    @classmethod
    def get_inventory_adjustment_product(cls, obj):
        return [{
            'id': ia_product.id,
            'product': {
                'id': ia_product.product_mapped_id,
                'title': ia_product.product_mapped.title,
                'code': ia_product.product_mapped.code,
                'general_traceability_method': ia_product.product_mapped.general_traceability_method,
                'description': ia_product.product_mapped.description,
            } if ia_product.product_mapped else {},
            'uom': {
                'id': ia_product.uom_mapped_id,
                'title': ia_product.uom_mapped.title,
                'code': ia_product.uom_mapped.code,
            } if ia_product.uom_mapped else {},
            'warehouse': {
                'id': ia_product.warehouse_mapped_id,
                'title': ia_product.warehouse_mapped.title,
                'code': ia_product.warehouse_mapped.code,
            } if ia_product.warehouse_mapped else {},
            'quantity_ia': (ia_product.count - ia_product.book_quantity),
            'quantity_import': (ia_product.count - ia_product.book_quantity),
            'select_for_action': ia_product.select_for_action,
            'action_status': ia_product.action_status,
            'product_unit_price': 0,
            'product_subtotal_price': 0,
            'product_cost_price': cls.get_cost(
                product_obj=ia_product.product_mapped, warehouse_id=ia_product.warehouse_mapped_id
            )
        } for ia_product in obj.inventory_adjustment_item_mapped.filter(action_type=2, action_status=False)]

    @classmethod
    def get_cost(cls, product_obj, warehouse_id):
        current_date = timezone.now()
        for period in product_obj.company.saledata_periods_belong_to_company.all():
            if period.fiscal_year == current_date.year:
                for product_inventory in product_obj.report_inventory_product_warehouse_product.all():
                    if product_inventory.period_mapped:
                        if product_inventory.period_mapped.fiscal_year == period.fiscal_year \
                                and product_inventory.sub_period_order == (current_date.month - period.space_month):
                            if product_inventory.warehouse_id == warehouse_id:
                                return product_inventory.ending_balance_cost
                break
        return 0

from rest_framework import serializers
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
                tenant=obj.tenant,
                company=obj.company,
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
        bulk_info.append(InventoryAdjustmentItem(**item, inventory_adjustment_mapped=obj))
    InventoryAdjustmentItem.objects.filter(inventory_adjustment_mapped=obj).delete()
    InventoryAdjustmentItem.objects.bulk_create(bulk_info)
    return True


class InventoryAdjustmentListSerializer(serializers.ModelSerializer):
    warehouses = serializers.SerializerMethodField()

    class Meta:
        model = InventoryAdjustment
        fields = (
            'id',
            'code',
            'title',
            'warehouses',
            'date_created'
        )

    @classmethod
    def get_warehouses(cls, obj):
        all_item = obj.warehouses_mapped.all()
        data = []
        for item in all_item:
            data.append({
                'warehouse_id': str(item.id),
                'warehouse_code': item.code,
                'warehouse_title': item.title,
            })
        return data


class InventoryAdjustmentDetailSerializer(serializers.ModelSerializer):
    warehouses = serializers.SerializerMethodField()
    employees_in_charge = serializers.SerializerMethodField()
    inventory_adjustment_item_mapped = serializers.SerializerMethodField()

    class Meta:
        model = InventoryAdjustment
        fields = (
            'id',
            'code',
            'title',
            'warehouses',
            'employees_in_charge',
            'inventory_adjustment_item_mapped',
            'date_created'
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
        fields = ('title',)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        create_inventory_adjustment_warehouses(instance, self.initial_data.get('ia_warehouses_data', []))
        create_inventory_adjustment_employees_in_charge(instance, self.initial_data.get('ia_employees_in_charge', []))
        create_inventory_adjustment_items(instance, self.initial_data.get('ia_items_data', []))
        return instance


class InventoryAdjustmentProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAdjustmentItem
        fields = '__all__'

__all__ = ['AssetToolsConfigDetailSerializers', 'AssetToolsConfigDetailUpdateSerializers']

from rest_framework import serializers

from apps.eoffice.assettools.models import AssetToolsConfig, AssetToolsConfigWarehouse, AssetToolsConfigEmployee
from apps.shared import TypeCheck


class AssetToolsConfigDetailSerializers(serializers.ModelSerializer):
    product_type = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()
    employee_tools_list_access = serializers.SerializerMethodField()

    @classmethod
    def get_warehouse(cls, obj):
        if obj.warehouse:
            warehouse_list = []
            for item in list(obj.warehouse.all()):
                warehouse_list.append({
                    'id': item.id,
                    'title': item.title,
                    'code': item.code
                })
            return warehouse_list
        return []

    @classmethod
    def get_employee_tools_list_access(cls, obj):
        if obj.employee_tools_list_access:
            employee_list = []
            for item in list(obj.employee_tools_list_access.all()):
                employee_list.append({'id': item.id, 'full_name': item.get_full_name()})
            return employee_list
        return []

    @classmethod
    def get_product_type(cls, obj):
        return {
            "id": obj.product_type_id,
            "title": obj.product_type.title,
        } if obj.product_type else {}

    class Meta:
        model = AssetToolsConfig
        fields = (
            'id',
            'warehouse',
            'product_type',
            'employee_tools_list_access'
        )


class AssetToolsConfigDetailUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = AssetToolsConfig
        fields = (
            'warehouse',
            'product_type',
            'employee_tools_list_access'
        )

    @classmethod
    def cover_warehouse_list(cls, instance, warehouse_list):
        AssetToolsConfigWarehouse.objects.filter(asset_tools_config=instance).delete()
        list_create = []
        for item in warehouse_list:
            if TypeCheck.check_uuid(item):
                list_create.append(
                    AssetToolsConfigWarehouse(
                        asset_tools_config=instance,
                        warehouse_id=item,
                    )
                )
        AssetToolsConfigWarehouse.objects.bulk_create(list_create)
        return True

    @classmethod
    def cover_employee_tools_list_access(cls, instance, employee_list):
        AssetToolsConfigEmployee.objects.filter(asset_tools_config=instance).delete()
        list_create = []
        for item in employee_list:
            if TypeCheck.check_uuid(item):
                list_create.append(
                    AssetToolsConfigEmployee(
                        asset_tools_config=instance,
                        employee_id=item,
                    )
                )
        AssetToolsConfigEmployee.objects.bulk_create(list_create)
        return True

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if 'warehouse' in self.initial_data and len(self.initial_data['warehouse']):
            warehouse_list = self.initial_data['warehouse']
            self.cover_warehouse_list(instance, warehouse_list)
        if 'employee_tools_list_access' in self.initial_data and len(self.initial_data['employee_tools_list_access']):
            employee_list = self.initial_data['employee_tools_list_access']
            self.cover_employee_tools_list_access(instance, employee_list)
        return instance

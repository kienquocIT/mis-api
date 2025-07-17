from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Product
from apps.masterdata.saledata.models.product_warehouse import PWModified
from apps.sales.productmodificationbom.models import (
    ProductModificationBOM, PMBOMCurrentComponent, PMBOMAddedComponent,
)
from apps.shared import (
    AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel,
)


__all__ = [
    'ProductModificationBOMListSerializer',
    'ProductModificationBOMCreateSerializer',
    'ProductModificationBOMDetailSerializer',
    'ProductModificationBOMUpdateSerializer',
    'ProductModifiedListSerializer',
    'ProductModifiedBeforeListSerializer',
    'ProductComponentListSerializer',
    'LatestComponentListSerializer',
]

# main
class ProductModificationBOMListSerializer(AbstractListSerializerModel):
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = ProductModificationBOM
        fields = (
            'id',
            'title',
            'code',
            'date_created',
            'employee_created',
        )

    @classmethod
    def get_employee_created(cls, obj):
        return {
            'id': obj.employee_created_id,
            'code': obj.employee_created.code,
            'full_name': obj.employee_created.get_full_name(2),
            'group': {
                'id': obj.employee_created.group_id,
                'title': obj.employee_created.group.title,
                'code': obj.employee_created.group.code
            } if obj.employee_created.group else {}
        } if obj.employee_created else {}


class ProductModificationBOMCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    product_mapped = serializers.UUIDField()
    current_component_data = serializers.JSONField(default=list, required=False)
    added_component_data = serializers.JSONField(default=list, required=False)

    class Meta:
        model = ProductModificationBOM
        fields = (
            'title',
            'product_mapped',
            'base_cost',
            'modified_cost',
            'current_component_data',
            'added_component_data'
        )

    @classmethod
    def validate_product_mapped(cls, value):
        try:
            return Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product_mapped': "Product mapped does not exist."})

    @classmethod
    def validate_current_component_data(cls, current_component_data):
        for item in current_component_data:
            if float(item.get('removed_quantity', 0)) < 0:
                raise serializers.ValidationError({'removed_quantity': "Removed quantity can not < 0."})
            if float(item.get('cost', 0)) < 0:
                raise serializers.ValidationError({'cost': "Cost can not < 0."})
            if float(item.get('removed_quantity', 0)) > float(item.get('base_quantity', 0)):
                raise serializers.ValidationError({'err': "Removed quantity can not > Base quantity."})
            item['subtotal'] = float(item.get('removed_quantity', 0)) * float(item.get('cost', 0))
        return current_component_data

    @classmethod
    def validate_added_component_data(cls, added_component_data):
        for item in added_component_data:
            product_added_obj = Product.objects.filter(id=item.get('product_added_id')).first()
            if not product_added_obj:
                raise serializers.ValidationError({'product_added': "Product added does not exist."})
            item['product_added_id'] = str(product_added_obj.id)
            item['product_added_data'] = {
                'id': str(product_added_obj.id),
                'code': product_added_obj.code,
                'title': product_added_obj.title,
                'description': product_added_obj.description,
                'general_traceability_method': product_added_obj.general_traceability_method,
            }
            if float(item.get('added_quantity', 0)) < 0:
                raise serializers.ValidationError({'added_quantity': "Added quantity can not < 0."})
            if float(item.get('cost', 0)) < 0:
                raise serializers.ValidationError({'cost': "Cost can not < 0."})
            item['subtotal'] = float(item.get('added_quantity', 0)) * float(item.get('cost', 0))
        return added_component_data

    def validate(self, validate_data):
        product_mapped_obj = validate_data.get('product_mapped')
        validate_data['product_mapped_data'] = {
            'id': str(product_mapped_obj.id),
            'code': product_mapped_obj.code,
            'title': product_mapped_obj.title,
            'description': product_mapped_obj.description,
            'general_traceability_method': product_mapped_obj.general_traceability_method,
        } if product_mapped_obj else {}

        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        current_component_data = validated_data.pop('current_component_data', [])
        added_component_data = validated_data.pop('added_component_data', [])

        pm_bom_obj = ProductModificationBOM.objects.create(**validated_data)

        ProductModificationBOMCommonFunction.create_current_component_data(pm_bom_obj, current_component_data)
        ProductModificationBOMCommonFunction.create_added_component_data(pm_bom_obj, added_component_data)

        return pm_bom_obj


class ProductModificationBOMDetailSerializer(AbstractDetailSerializerModel):
    current_component_data = serializers.SerializerMethodField()
    added_component_data = serializers.SerializerMethodField()

    class Meta:
        model = ProductModificationBOM
        fields = (
            'id',
            'code',
            'title',
            'product_mapped_data',
            'base_cost',
            'modified_cost',
            'current_component_data',
            'added_component_data',
            'date_created',
        )

    @classmethod
    def get_current_component_data(cls, obj):
        return [{
            'order': item.order,
            'component_text_data': item.component_text_data,
            'base_quantity': item.base_quantity,
            'removed_quantity': item.removed_quantity,
            'cost': item.cost,
            'subtotal': item.subtotal,
        } for item in obj.current_components.all()]

    @classmethod
    def get_added_component_data(cls, obj):
        return [{
            'order': item.order,
            'product_added_data': item.product_added_data,
            'added_quantity': item.added_quantity,
            'cost': item.cost,
            'subtotal': item.subtotal,
        } for item in obj.added_components.all()]


class ProductModificationBOMUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    product_mapped = serializers.UUIDField()
    current_component_data = serializers.JSONField(default=list, required=False)
    added_component_data = serializers.JSONField(default=list, required=False)

    class Meta:
        model = ProductModificationBOM
        fields = (
            'title',
            'product_mapped',
            'base_cost',
            'modified_cost',
            'current_component_data',
            'added_component_data'
        )

    @classmethod
    def validate_product_mapped(cls, value):
        return ProductModificationBOMCreateSerializer.validate_product_mapped(value)

    @classmethod
    def validate_current_component_data(cls, current_component_data):
        return ProductModificationBOMCreateSerializer().validate_current_component_data(current_component_data)

    @classmethod
    def validate_added_component_data(cls, added_component_data):
        return ProductModificationBOMCreateSerializer().validate_added_component_data(added_component_data)

    def validate(self, validate_data):
        return ProductModificationBOMCreateSerializer().validate(validate_data)

    @decorator_run_workflow
    def update(self, instance, validated_data):
        current_component_data = validated_data.pop('current_component_data', [])
        added_component_data = validated_data.pop('added_component_data', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        ProductModificationBOMCommonFunction.create_current_component_data(instance, current_component_data)
        ProductModificationBOMCommonFunction.create_added_component_data(instance, added_component_data)

        return instance


class ProductModificationBOMCommonFunction:
    @staticmethod
    def create_current_component_data(pm_bom_obj, current_component_data):
        bulk_info = []
        for order, item in enumerate(current_component_data):
            current_component_obj = PMBOMCurrentComponent(product_modified_bom=pm_bom_obj, order=order, **item)
            bulk_info.append(current_component_obj)
        PMBOMCurrentComponent.objects.filter(product_modified_bom=pm_bom_obj).delete()
        PMBOMCurrentComponent.objects.bulk_create(bulk_info)
        return True

    @staticmethod
    def create_added_component_data(pm_bom_obj, added_component_data):
        bulk_info = []
        for order, item in enumerate(added_component_data):
            bulk_info.append(PMBOMAddedComponent(product_modified_bom=pm_bom_obj, order=order, **item))
        PMBOMAddedComponent.objects.filter(product_modified_bom=pm_bom_obj).delete()
        PMBOMAddedComponent.objects.bulk_create(bulk_info)
        return True


# related
class ProductModifiedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'description',
            'general_traceability_method'
        )


class ProductModifiedBeforeListSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    general_traceability_method = serializers.SerializerMethodField()
    serial_number = serializers.SerializerMethodField()
    lot_number = serializers.SerializerMethodField()
    warehouse_data = serializers.SerializerMethodField()

    class Meta:
        model = PWModified
        fields = (
            'id',
            'code',
            'title',
            'description',
            'general_traceability_method',
            'product_warehouse_id',
            'product_warehouse_lot_id',
            'product_warehouse_serial_id',
            'modified_number',
            'new_description',
            'serial_number',
            'lot_number',
            'warehouse_data'
        )

    @classmethod
    def get_id(cls, obj):
        return obj.product_warehouse.product_id if obj.product_warehouse else None

    @classmethod
    def get_code(cls, obj):
        return obj.product_warehouse.product.code if obj.product_warehouse else None

    @classmethod
    def get_title(cls, obj):
        title = ''
        if obj.product_warehouse:
            if obj.product_warehouse.product:
                title = obj.product_warehouse.product.title
        return title

    @classmethod
    def get_description(cls, obj):
        description = ''
        if obj.product_warehouse:
            if obj.product_warehouse.product:
                description = obj.product_warehouse.product.description
        return description

    @classmethod
    def get_general_traceability_method(cls, obj):
        general_traceability_method = None
        if obj.product_warehouse:
            if obj.product_warehouse.product:
                general_traceability_method = obj.product_warehouse.product.general_traceability_method
        return general_traceability_method

    @classmethod
    def get_serial_number(cls, obj):
        if obj.product_warehouse_serial:
            return obj.product_warehouse_serial.serial_number
        return ''

    @classmethod
    def get_lot_number(cls, obj):
        if obj.product_warehouse_lot:
            return obj.product_warehouse_lot.lot_number
        return ''

    @classmethod
    def get_warehouse_data(cls, obj):
        return obj.product_warehouse.warehouse_data if obj.product_warehouse else {}


class ProductComponentListSerializer(serializers.ModelSerializer):
    component_list_data = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'code',
            'title',
            'component_list_data'
        )

    @classmethod
    def get_component_list_data(cls, obj):
        component_list_data = []
        for item in obj.product_components.all():
            component_list_data.append({
                'component_order': item.order,
                'component_id': item.id,
                'component_name': item.component_name,
                'component_des': item.component_des,
                'component_quantity': item.component_quantity
            })
        return component_list_data


class LatestComponentListSerializer(serializers.ModelSerializer):
    current_component_data = serializers.SerializerMethodField()

    class Meta:
        model = PWModified
        fields = (
            'id',
            'code',
            'title',
            'current_component_data'
        )

    @classmethod
    def get_current_component_data(cls, obj):
        current_component_data = []
        for item in obj.pw_modified_components.all():
            current_component_data.append({
                'component_id': str(item.id),
                'order': item.order,
                'component_text_data': item.component_text_data,
                'component_product_data': item.component_product_data,
                'component_quantity': item.component_quantity,
            })
        return current_component_data

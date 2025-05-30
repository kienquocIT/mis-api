from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import ProductWareHouse, ProductWareHouseSerial, Product, ProductWareHouseLot
from apps.sales.productmodification.models import ProductModification
from apps.shared import AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel


__all__ = [
    'ProductModificationListSerializer',
    'ProductModificationCreateSerializer',
    'ProductModificationDetailSerializer',
    'ProductModificationUpdateSerializer',
    'ProductModifiedListSerializer',
    'ProductComponentListSerializer',
    'WarehouseListByProductSerializer',
    'ProductSerialListSerializer',
]

# main
class ProductModificationListSerializer(AbstractListSerializerModel):
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = ProductModification
        fields = (
            'id',
            'title',
            'code',
            'date_created',
            'employee_created'
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


class ProductModificationCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    product_modified = serializers.UUIDField()
    prd_wh = serializers.UUIDField()
    prd_wh_lot = serializers.UUIDField(required=False)
    prd_wh_serial = serializers.UUIDField(required=False)

    class Meta:
        model = ProductModification
        fields = (
            'title',
            'product_modified',
            'prd_wh',
            'prd_wh_lot',
            'prd_wh_serial',
            'detail_product_modified_info'
        )

    @classmethod
    def validate_product_modified(cls, value):
        try:
            return Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product_modified': "Product modification does not exist."})

    @classmethod
    def validate_prd_wh(cls, value):
        try:
            return ProductWareHouse.objects.get(id=value)
        except ProductWareHouse.DoesNotExist:
            raise serializers.ValidationError({'prd_wh': "Product warehouse does not exist."})

    @classmethod
    def validate_prd_wh_lot(cls, value):
        if value:
            try:
                return ProductWareHouseLot.objects.get(id=value)
            except ProductWareHouseLot.DoesNotExist:
                raise serializers.ValidationError({'prd_wh_lot': "Product warehouse lot does not exist."})
        return None

    @classmethod
    def validate_prd_wh_serial(cls, value):
        if value:
            try:
                return ProductWareHouseSerial.objects.get(id=value)
            except ProductWareHouseSerial.DoesNotExist:
                raise serializers.ValidationError({'prd_wh_serial': "Product warehouse serial does not exist."})
        return None

    def validate(self, validate_data):
        product_modified_obj = validate_data.get('product_modified')

        prd_wh_obj = validate_data.get('prd_wh')
        if prd_wh_obj:
            validate_data['prd_wh_data'] = {
                'id': str(prd_wh_obj.id),
                'product': {
                    'id': str(prd_wh_obj.product_id),
                    'code': prd_wh_obj.product.code,
                    'title': prd_wh_obj.product.title,
                    'description': prd_wh_obj.product.description,
                    'general_traceability_method': prd_wh_obj.product.general_traceability_method,
                },
                'warehouse': {
                    'id': str(prd_wh_obj.warehouse_id),
                    'code': prd_wh_obj.warehouse.code,
                    'title': prd_wh_obj.warehouse.title,
                } if prd_wh_obj.warehouse else {}
            }

        if product_modified_obj.general_traceability_method == 0:
            # None
            validate_data['prd_wh_lot'] = None
            validate_data['prd_wh_serial'] = None
        if product_modified_obj.general_traceability_method == 1:
            # Lot
            prd_wh_lot_obj = validate_data.get('prd_wh_lot')
            if prd_wh_lot_obj is None:
                raise serializers.ValidationError({'prd_wh_lot': "Lot is required."})
            validate_data['prd_wh_lot_data'] = {
                'id': str(prd_wh_lot_obj.id),
                'lot_number': prd_wh_lot_obj.lot_number,
                'expire_date': str(prd_wh_lot_obj.expire_date),
                'manufacture_date': str(prd_wh_lot_obj.manufacture_date),
            }
        if product_modified_obj.general_traceability_method == 2:
            # Sn
            prd_wh_serial_obj = validate_data.get('prd_wh_serial')
            if prd_wh_serial_obj is None:
                raise serializers.ValidationError({'prd_wh_serial': "Serial is required."})
            validate_data['prd_wh_serial_data'] = {
                'id': str(prd_wh_serial_obj.id),
                'vendor_serial_number': prd_wh_serial_obj.vendor_serial_number,
                'serial_number': prd_wh_serial_obj.vendor_serial_number,
                'expire_date': str(prd_wh_serial_obj.expire_date),
                'manufacture_date': str(prd_wh_serial_obj.manufacture_date),
                'warranty_start': str(prd_wh_serial_obj.warranty_start),
                'warranty_end': str(prd_wh_serial_obj.warranty_end),
            }
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        pm_obj = ProductModification.objects.create(**validated_data)
        return pm_obj


class ProductModificationDetailSerializer(AbstractDetailSerializerModel):

    class Meta:
        model = ProductModification
        fields = (
            'id',
            'code',
            'title',
            'date_created',
            'prd_wh_data',
            'prd_wh_lot_data',
            'prd_wh_serial_data',
            'detail_product_modified_info'
        )


class ProductModificationUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    product_modified = serializers.UUIDField()
    prd_wh = serializers.UUIDField()
    prd_wh_lot = serializers.UUIDField(required=False)
    prd_wh_serial = serializers.UUIDField(required=False)

    class Meta:
        model = ProductModification
        fields = (
            'title',
            'product_modified',
            'prd_wh',
            'prd_wh_lot',
            'prd_wh_serial',
            'detail_product_modified_info'
        )

    @classmethod
    def validate_product_modified(cls, value):
        return ProductModificationCreateSerializer.validate_product_modified(value)

    @classmethod
    def validate_prd_wh(cls, value):
        return ProductModificationCreateSerializer.validate_prd_wh(value)

    @classmethod
    def validate_prd_wh_lot(cls, value):
        return ProductModificationCreateSerializer.validate_prd_wh_lot(value)

    @classmethod
    def validate_prd_wh_serial(cls, value):
        return ProductModificationCreateSerializer.validate_prd_wh_serial(value)

    def validate(self, validate_data):
        return ProductModificationCreateSerializer().validate(validate_data)

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance


class ProductModificationCommonFunction:
    pass


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
                'order': item.order,
                'id': item.id,
                'component_name': item.component_name,
                'component_des': item.component_des,
                'component_quantity': item.component_quantity
            })
        return component_list_data


class WarehouseListByProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouse
        fields = (
            'id',
            'warehouse_data',
            'uom_data',
            'stock_amount'
        )


class ProductSerialListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouseSerial
        fields = (
            'id',
            'vendor_serial_number',
            'serial_number',
            'expire_date',
            'manufacture_date',
            'warranty_start',
            'warranty_end'
        )

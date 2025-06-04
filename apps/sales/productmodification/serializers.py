from rest_framework import serializers
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import ProductWareHouse, ProductWareHouseSerial, Product, ProductWareHouseLot, \
    WareHouse
from apps.sales.productmodification.models import ProductModification, CurrentComponent, RemovedComponent, \
    CurrentComponentDetail
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
    warehouse_id = serializers.UUIDField()
    prd_wh_lot = serializers.UUIDField(required=False)
    prd_wh_serial = serializers.UUIDField(required=False)
    current_component_data = serializers.JSONField(default=list, required=False)
    removed_component_data = serializers.JSONField(default=list, required=False)

    class Meta:
        model = ProductModification
        fields = (
            'title',
            'product_modified',
            'warehouse_id',
            'prd_wh_lot',
            'prd_wh_serial',
            'current_component_data',
            'removed_component_data'
        )

    @classmethod
    def validate_product_modified(cls, value):
        try:
            return Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product_modified': "Product modification does not exist."})

    @classmethod
    def validate_warehouse_id(cls, value):
        try:
            return value
        except WareHouse.DoesNotExist:
            raise serializers.ValidationError({'warehouse_id': "Warehouse does not exist."})

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

    @classmethod
    def validate_current_component_data(cls, current_component_data):
        for item in current_component_data:
            if float(item.get('component_quantity', 0)) <= 0:
                raise serializers.ValidationError({'component_quantity': "Component quantity must be > 0."})

            if item.get('component_product_id'):
                item['component_text_data'] = {}
                component_product = Product.objects.filter(id=item.get('component_product_id')).first()
                if not component_product:
                    raise serializers.ValidationError({'component_product_id': "Component product does not exist."})
                item['component_product_id'] = str(component_product.id)
                item['component_product_data'] = {
                    'id': str(component_product.id),
                    'code': component_product.code,
                    'title': component_product.title,
                    'description': component_product.description,
                    'general_traceability_method': component_product.general_traceability_method,
                }
            else:
                item['component_product_id'] = None
                item['component_product_data'] = {}
                component_text_data = item.get('component_text_data', {})
                if not component_text_data:
                    raise serializers.ValidationError({'component_text_data': "Component text data is missing."})
                elif 'title' not in component_text_data:
                    raise serializers.ValidationError({'title': "Component text data TITLE is missing."})

        return current_component_data

    @classmethod
    def validate_removed_component_data(cls, removed_component_data):
        for item in removed_component_data:
            if float(item.get('component_quantity', 0)) <= 0:
                raise serializers.ValidationError({'component_quantity': "Component quantity must be > 0."})

            if item.get('component_product_id'):
                item['component_text_data'] = {}
                component_product = Product.objects.filter(id=item.get('component_product_id')).first()
                if not component_product:
                    raise serializers.ValidationError({'component_product_id': "Component product does not exist."})
                item['component_product_id'] = str(component_product.id)
                item['component_product_data'] = {
                    'id': str(component_product.id),
                    'code': component_product.code,
                    'title': component_product.title,
                    'description': component_product.description,
                    'general_traceability_method': component_product.general_traceability_method,
                }
            else:
                item['component_product_id'] = None
                item['component_product_data'] = {}
                component_text_data = item.get('component_text_data', {})
                if not component_text_data:
                    raise serializers.ValidationError({'component_text_data': "Component text data is missing."})
                elif 'title' not in component_text_data:
                    raise serializers.ValidationError({'title': "Component text data TITLE is missing."})

        return removed_component_data

    def validate(self, validate_data):
        product_modified_obj = validate_data.get('product_modified')

        warehouse_id = validate_data.pop('warehouse_id')
        if warehouse_id:
            prd_wh_obj = ProductWareHouse.objects.filter(
                warehouse_id=warehouse_id, product=product_modified_obj
            ).first()
            if prd_wh_obj:
                validate_data['prd_wh'] = prd_wh_obj
                validate_data['prd_wh_data'] = {
                    'id': str(prd_wh_obj.id),
                    'product': {
                        'id': str(prd_wh_obj.product_id),
                        'code': prd_wh_obj.product.code,
                        'title': prd_wh_obj.product.title,
                        'description': prd_wh_obj.product.description,
                        'general_traceability_method': prd_wh_obj.product.general_traceability_method,
                    } if prd_wh_obj.product else {},
                    'warehouse': {
                        'id': str(prd_wh_obj.warehouse_id),
                        'code': prd_wh_obj.warehouse.code,
                        'title': prd_wh_obj.warehouse.title,
                    } if prd_wh_obj.warehouse else {}
                }
            else:
                raise serializers.ValidationError({'prd_wh': "Product warehouse does not exist."})

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
        current_component_data = validated_data.pop('current_component_data', [])
        removed_component_data = validated_data.pop('removed_component_data', [])

        pm_obj = ProductModification.objects.create(**validated_data)

        ProductModificationCommonFunction.create_current_component_data(pm_obj, current_component_data)
        ProductModificationCommonFunction.create_removed_component_data(pm_obj, removed_component_data)

        return pm_obj


class ProductModificationDetailSerializer(AbstractDetailSerializerModel):
    current_component_data = serializers.SerializerMethodField()
    removed_component_data = serializers.SerializerMethodField()

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
            'current_component_data',
            'removed_component_data',
        )

    @classmethod
    def get_current_component_data(cls, obj):
        current_component_data = []
        for item in obj.current_components.all():
            current_component_data.append({
                'id': str(item.id),
                'order': item.order,
                'component_text_data': item.component_text_data,
                'component_product_data': item.component_product_data,
                'component_quantity': item.component_quantity,
                'component_product_none_detail': [{
                    'warehouse_id': child.component_prd_wh.warehouse_id,
                    'picked_quantity': child.component_prd_wh_quantity,
                } for child in item.current_components_detail.filter(
                    current_component=item,
                    component_prd_wh__isnull=False
                )],
                'component_product_sn_detail': item.current_components_detail.filter(
                    current_component=item,
                    component_prd_wh_serial__isnull=False
                ).values_list('component_prd_wh_serial_id', flat=True),
            })
        return current_component_data

    @classmethod
    def get_removed_component_data(cls, obj):
        removed_component_data = []
        for item in obj.removed_components.all():
            removed_component_data.append({
                'id': str(item.id),
                'order': item.order,
                'component_text_data': item.component_text_data,
                'component_product_data': item.component_product_data,
                'component_quantity': item.component_quantity,
            })
        return removed_component_data


class ProductModificationUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    product_modified = serializers.UUIDField()
    warehouse_id = serializers.UUIDField()
    prd_wh_lot = serializers.UUIDField(required=False)
    prd_wh_serial = serializers.UUIDField(required=False)
    current_component_data = serializers.JSONField(default=list, required=False)
    removed_component_data = serializers.JSONField(default=list, required=False)

    class Meta:
        model = ProductModification
        fields = (
            'title',
            'product_modified',
            'warehouse_id',
            'prd_wh_lot',
            'prd_wh_serial',
            'current_component_data',
            'removed_component_data',
        )

    @classmethod
    def validate_product_modified(cls, value):
        return ProductModificationCreateSerializer.validate_product_modified(value)

    @classmethod
    def validate_warehouse_id(cls, value):
        return ProductModificationCreateSerializer.validate_warehouse_id(value)

    @classmethod
    def validate_prd_wh_lot(cls, value):
        return ProductModificationCreateSerializer.validate_prd_wh_lot(value)

    @classmethod
    def validate_prd_wh_serial(cls, value):
        return ProductModificationCreateSerializer.validate_prd_wh_serial(value)

    @classmethod
    def validate_current_component_data(cls, current_component_data):
        return ProductModificationCreateSerializer.validate_current_component_data(current_component_data)

    @classmethod
    def validate_removed_component_data(cls, removed_component_data):
        return ProductModificationCreateSerializer.validate_removed_component_data(removed_component_data)

    def validate(self, validate_data):
        return ProductModificationCreateSerializer().validate(validate_data)

    @decorator_run_workflow
    def update(self, instance, validated_data):
        current_component_data = validated_data.pop('current_component_data', [])
        removed_component_data = validated_data.pop('removed_component_data', [])

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        ProductModificationCommonFunction.create_current_component_data(instance, current_component_data)
        ProductModificationCommonFunction.create_removed_component_data(instance, removed_component_data)

        return instance


class ProductModificationCommonFunction:
    @staticmethod
    def create_current_component_data(pm_obj, current_component_data):
        bulk_info = []
        bulk_info_detail_sn = []
        for order, item in enumerate(current_component_data):
            component_product_none_detail = item.pop('component_product_none_detail', [])
            component_product_lot_detail = item.pop('component_product_lot_detail', [])
            component_product_sn_detail = item.pop('component_product_sn_detail', [])

            current_component_obj = CurrentComponent(product_modified=pm_obj, order=order, **item)
            # none
            bulk_info.append(current_component_obj)
            for child in component_product_none_detail:
                wh_id = child.get('warehouse_id')
                picked_quantity = child.get('picked_quantity', 0)
                prd_wh_obj = ProductWareHouse.objects.filter(
                    warehouse_id=wh_id, product_id=item.get('component_product_id')
                ).first()
                if prd_wh_obj:
                    bulk_info_detail_sn.append(
                        CurrentComponentDetail(
                            current_component=current_component_obj,
                            component_prd_wh=prd_wh_obj,
                            component_prd_wh_quantity=picked_quantity
                        )
                    )
            # lot

            # sn
            for serial_id in component_product_sn_detail:
                serial_obj = ProductWareHouseSerial.objects.filter(id=serial_id).first()
                if serial_obj:
                    bulk_info_detail_sn.append(
                        CurrentComponentDetail(
                            current_component=current_component_obj,
                            component_prd_wh_serial=serial_obj,
                            component_prd_wh_serial_data={
                                'id': str(serial_obj.id),
                                'vendor_serial_number': serial_obj.vendor_serial_number,
                                'serial_number': serial_obj.vendor_serial_number,
                                'expire_date': str(serial_obj.expire_date),
                                'manufacture_date': str(serial_obj.manufacture_date),
                                'warranty_start': str(serial_obj.warranty_start),
                                'warranty_end': str(serial_obj.warranty_end),
                            }
                        )
                    )
        CurrentComponent.objects.filter(product_modified=pm_obj).delete()
        CurrentComponent.objects.bulk_create(bulk_info)
        CurrentComponentDetail.objects.bulk_create(bulk_info_detail_sn)
        return True

    @staticmethod
    def create_removed_component_data(pm_obj, removed_component_data):
        bulk_info = []
        for order, item in enumerate(removed_component_data):
            bulk_info.append(RemovedComponent(product_modified=pm_obj, order=order, **item))
        RemovedComponent.objects.filter(product_modified=pm_obj).delete()
        RemovedComponent.objects.bulk_create(bulk_info)
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

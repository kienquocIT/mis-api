from rest_framework import serializers

from apps.core.company.models import CompanyFunctionNumber
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import (
    ProductWareHouse, ProductWareHouseSerial, Product, ProductWareHouseLot,
    WareHouse, ProductType, ProductCategory, UnitOfMeasureGroup, UnitOfMeasure,
)
from apps.sales.productmodification.models import (
    ProductModification, CurrentComponent, RemovedComponent, CurrentComponentDetail,
)
from apps.shared import (
    AbstractListSerializerModel, AbstractCreateSerializerModel, AbstractDetailSerializerModel,
    ProductMsg, BaseMsg
)

__all__ = [
    'ProductModificationListSerializer',
    'ProductModificationCreateSerializer',
    'ProductModificationDetailSerializer',
    'ProductModificationUpdateSerializer',
    'ProductModifiedListSerializer',
    'ProductComponentListSerializer',
    'WarehouseListByProductSerializer',
    'ProductSerialListSerializer',
    'ProductLotListSerializer',
    'ProductModificationDDListSerializer',
    'ProductModificationProductGRListSerializer',
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
            'created_goods_issue',
            'created_goods_receipt',
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
                if 'title' not in component_text_data:
                    raise serializers.ValidationError({'title': "Component text data TITLE is missing."})

        return current_component_data

    @staticmethod
    def validate_product_mapped_data_new(prd_mapped_dt):
        if prd_mapped_dt.get('code'):
            if Product.objects.filter_on_company(code=prd_mapped_dt.get('code')).exists():
                raise serializers.ValidationError({"code": ProductMsg.CODE_EXIST})
        else:
            code_generated = CompanyFunctionNumber.gen_auto_code(app_code='product')
            if not code_generated:
                raise serializers.ValidationError({
                    "code": f"{ProductMsg.CODE_NOT_NULL}. {BaseMsg.NO_CONFIG_AUTO_CODE}"
                })
            prd_mapped_dt['code'] = code_generated
        if not prd_mapped_dt.get('title'):
            raise serializers.ValidationError({'title': "Product mapping is missing title."})
        if not ProductType.objects.filter_on_company(id=prd_mapped_dt.get('product_type')).exists():
            raise serializers.ValidationError({
                'product_type': "Product mapping is missing Product type."
            })
        if not ProductCategory.objects.filter_on_company(
                id=prd_mapped_dt.get('general_product_category')
        ).exists():
            raise serializers.ValidationError({
                'general_product_category': "Product mapping is missing Product category."
            })
        if not UnitOfMeasureGroup.objects.filter_on_company(
                id=prd_mapped_dt.get('general_uom_group')
        ).exists():
            raise serializers.ValidationError({
                'general_uom_group': "Product mapping is missing UOM group."
            })
        if not UnitOfMeasure.objects.filter_on_company(id=prd_mapped_dt.get('inventory_uom')).exists():
            raise serializers.ValidationError({
                'inventory_uom': "Product mapping is missing Inventory UOM."
            })
        return True

    @staticmethod
    def validate_product_mapped_data_map(prd_mapped_dt):
        if not Product.objects.filter_on_company(id=prd_mapped_dt.get('product_mapped')).exists():
            raise serializers.ValidationError({
                'product_mapped': "Product mapping is missing product mapped."
            })
        return True

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
                if 'title' not in component_text_data:
                    raise serializers.ValidationError({'title': "Component text data TITLE is missing."})

                prd_mapped_dt = item.get('product_mapped_data', {})
                if len(prd_mapped_dt) > 0:
                    if prd_mapped_dt.get('type') == 'new':
                        cls.validate_product_mapped_data_new(prd_mapped_dt)
                    if prd_mapped_dt.get('type') == 'map':
                        cls.validate_product_mapped_data_map(prd_mapped_dt)
                else:
                    raise serializers.ValidationError({'product_mapped_data': "Product mapped data is missing."})

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
                'component_id': str(item.id),
                'order': item.order,
                'component_text_data': item.component_text_data,
                'component_product_data': item.component_product_data,
                'component_quantity': item.component_quantity,
                'is_added_component': item.is_added_component,
                'component_product_none_detail': [{
                    'warehouse_id': child.component_prd_wh.warehouse_id,
                    'picked_quantity': child.component_prd_wh_quantity,
                } for child in item.current_components_detail.filter(
                    current_component=item,
                    component_prd_wh__isnull=False
                )],
                'component_product_lot_detail': [{
                    'lot_id': child.component_prd_wh_lot_id,
                    'picked_quantity': child.component_prd_wh_lot_quantity,
                } for child in item.current_components_detail.filter(
                    current_component=item,
                    component_prd_wh_lot__isnull=False
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
                'is_mapped': item.is_mapped,
                'product_mapped_data': item.product_mapped_data,
                'fair_value': item.fair_value,
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
    def create_current_component_data_sub(
            current_component_obj, current_component_item,
            component_product_none_detail, component_product_lot_detail, component_product_sn_detail
    ):
        bulk_info_detail_sub = []
        # none
        for child in component_product_none_detail:
            prd_wh_obj = ProductWareHouse.objects.filter(
                warehouse_id=child.get('warehouse_id'), product_id=current_component_item.get('component_product_id')
            ).first()
            if prd_wh_obj:
                bulk_info_detail_sub.append(
                    CurrentComponentDetail(
                        current_component=current_component_obj,
                        component_prd_wh=prd_wh_obj,
                        component_prd_wh_quantity=child.get('picked_quantity', 0)
                    )
                )
        # lot
        for child in component_product_lot_detail:
            lot_obj = ProductWareHouseLot.objects.filter(id=child.get('lot_id')).first()
            if lot_obj:
                bulk_info_detail_sub.append(
                    CurrentComponentDetail(
                        current_component=current_component_obj,
                        component_prd_wh_lot=lot_obj,
                        component_prd_wh_lot_data={
                            'id': str(lot_obj.id),
                            'lot_number': lot_obj.lot_number,
                            'expire_date': str(lot_obj.expire_date),
                            'manufacture_date': str(lot_obj.manufacture_date),
                        },
                        component_prd_wh_lot_quantity=child.get('picked_quantity', 0)
                    )
                )
        # sn
        for serial_id in component_product_sn_detail:
            serial_obj = ProductWareHouseSerial.objects.filter(id=serial_id).first()
            if serial_obj:
                bulk_info_detail_sub.append(
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
        return bulk_info_detail_sub

    @staticmethod
    def create_current_component_data(pm_obj, current_component_data):
        bulk_info = []
        bulk_info_detail = []
        for order, current_component_item in enumerate(current_component_data):
            component_product_none_detail = current_component_item.pop('component_product_none_detail', [])
            component_product_lot_detail = current_component_item.pop('component_product_lot_detail', [])
            component_product_sn_detail = current_component_item.pop('component_product_sn_detail', [])

            current_component_obj = CurrentComponent(product_modified=pm_obj, order=order, **current_component_item)
            bulk_info.append(current_component_obj)
            bulk_info_detail += ProductModificationCommonFunction.create_current_component_data_sub(
                current_component_obj,
                current_component_item,
                component_product_none_detail,
                component_product_lot_detail,
                component_product_sn_detail
            )

        CurrentComponent.objects.filter(product_modified=pm_obj).delete()
        CurrentComponent.objects.bulk_create(bulk_info)
        CurrentComponentDetail.objects.bulk_create(bulk_info_detail)
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
            'stock_amount'
        )


class ProductLotListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWareHouseLot
        fields = (
            'id',
            'lot_number',
            'quantity_import',
            'expire_date',
            'manufacture_date'
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


class ProductModificationDDListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModification
        fields = (
            'id',
            'title',
            'code',
            'date_created',
        )


# SERIALIZERS USE FOR GOODS RECEIPT
class ProductModificationProductGRListSerializer(serializers.ModelSerializer):
    product_modification_product_id = serializers.SerializerMethodField()
    product_data = serializers.SerializerMethodField()
    uom_data = serializers.SerializerMethodField()
    # tax_data = serializers.SerializerMethodField()
    product_unit_price = serializers.SerializerMethodField()
    product_quantity_order_actual = serializers.SerializerMethodField()

    class Meta:
        model = RemovedComponent
        fields = (
            'id',
            'product_modification_product_id',
            'product_data',
            'uom_data',
            # 'tax_data',
            'product_unit_price',
            'product_quantity_order_actual',
            'gr_remain_quantity',
        )

    @classmethod
    def get_product_modification_product_id(cls, obj):
        return obj.id

    @classmethod
    def get_product_data(cls, obj):
        return {
            'id': obj.component_product_id,
            'title': obj.component_product.title,
            'code': obj.component_product.code,
            'general_traceability_method': obj.component_product.general_traceability_method,
            'description': obj.component_product.description,
            'product_choice': obj.component_product.product_choice,
        } if obj.component_product else {}

    @classmethod
    def get_uom_data(cls, obj):
        uom_obj = obj.component_product.inventory_uom
        return {
            'id': uom_obj.id,
            'title': uom_obj.title,
            'code': uom_obj.code,
            'uom_group': {
                'id': uom_obj.group_id,
                'title': uom_obj.group.title,
                'code': uom_obj.group.code,
                'uom_reference': {
                    'id': uom_obj.group.uom_reference_id,
                    'title': uom_obj.group.uom_reference.title,
                    'code': uom_obj.group.uom_reference.code,
                    'ratio': uom_obj.group.uom_reference.ratio,
                    'rounding': uom_obj.group.uom_reference.rounding,
                } if uom_obj.group.uom_reference else {},
            } if uom_obj.group else {},
            'ratio': uom_obj.ratio,
            'rounding': uom_obj.rounding,
            'is_referenced_unit': uom_obj.is_referenced_unit,
        } if uom_obj else {}

    # @classmethod
    # def get_tax_data(cls, obj):
    #     return {
    #         'id': obj.tax_id,
    #         'title': obj.tax.title,
    #         'code': obj.tax.code,
    #         'rate': obj.tax.rate,
    #     } if obj.tax else {}

    @classmethod
    def get_product_unit_price(cls, obj):
        return obj.fair_value

    @classmethod
    def get_product_quantity_order_actual(cls, obj):
        return obj.component_quantity

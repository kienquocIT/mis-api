import logging
from django.db import transaction
from rest_framework import serializers

from apps.core.hr.models import Group
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Product, ToolClassification
from apps.sales.apinvoice.models import APInvoice
from apps.sales.asset.models import InstrumentTool, InstrumentToolUseDepartment, InstrumentToolSource, \
    InstrumentToolAPInvoiceItems
from apps.sales.asset.serializers.handler import CommonHandler
from apps.shared import BaseMsg, FixedAssetMsg, AbstractCreateSerializerModel, AbstractDetailSerializerModel, \
    AbstractListSerializerModel

logger = logging.getLogger(__name__)

__all__= [
    'InstrumentToolListSerializer',
    'InstrumentToolCreateSerializer',
    'InstrumentToolDetailSerializer',
    'InstrumentToolUpdateSerializer',
    'ToolForLeaseListSerializer',
    'ToolStatusLeaseListSerializer',
]


class ToolAssetSourcesCreateSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    @classmethod
    def validate_description(cls, value):
        if not value:
            raise serializers.ValidationError({"description": FixedAssetMsg.DESCRIPTION_REQUIRED})
        return value

    class Meta:
        model = InstrumentToolSource
        fields = (
            'description',
            'document_no',
            'transaction_type',
            'code',
            'value'
        )


class InstrumentToolListSerializer(AbstractListSerializerModel):
    product = serializers.SerializerMethodField()
    manage_department = serializers.SerializerMethodField()
    use_department = serializers.SerializerMethodField()
    use_customer = serializers.SerializerMethodField()
    write_off_quantity = serializers.SerializerMethodField()
    class Meta:
        model = InstrumentTool
        fields = (
            'id',
            'code',
            'asset_code',
            'title',
            'status',
            'product',
            'manage_department',
            'use_department',
            'use_customer',
            'date_created',
            'depreciation_time',
            'depreciation_time_unit',
            'write_off_quantity'
        )

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product.id,
            'code': obj.product.code,
            'title': obj.product.title,
        } if obj.product else {}

    @classmethod
    def get_manage_department(cls, obj):
        return {
            'id': obj.manage_department.id,
            'code': obj.manage_department.code,
            'title': obj.manage_department.title,
        } if obj.manage_department else {}

    @classmethod
    def get_use_department(cls, obj):
        data = []
        for use_department_item in obj.use_departments.all():
            data.append({
                'id': use_department_item.use_department_id,
                'title': use_department_item.use_department.title,
                'code': use_department_item.use_department.code,
            })
        return data

    @classmethod
    def get_use_customer(cls, obj):
        return {
            'id': obj.use_customer.id,
            'code': obj.use_customer.code,
            'fullname': obj.use_customer.name,
        } if obj.use_customer else {}

    @classmethod
    def get_write_off_quantity(cls, obj):
        write_off_quantity = 0
        for quantity_item in obj.write_off_quantities.filter(instrument_tool_write_off__system_status=3):
            write_off_quantity += quantity_item.write_off_quantity
        return write_off_quantity


class InstrumentToolCreateSerializer(AbstractCreateSerializerModel):
    classification = serializers.UUIDField()
    product = serializers.UUIDField()
    manage_department = serializers.UUIDField()
    use_department = serializers.ListSerializer(
        child=serializers.UUIDField(required=False)
    )
    asset_sources = ToolAssetSourcesCreateSerializer(many=True)
    increase_fa_list = serializers.JSONField(required=False)
    asset_code = serializers.CharField(required=False)

    class Meta:
        model = InstrumentTool
        fields = (
            'classification',
            'title',
            'asset_code',
            'product',
            'manage_department',
            'use_department',
            'unit_price',
            'quantity',
            'measure_unit',
            'total_value',
            'source_type',
            'asset_sources',
            'depreciation_time',
            'depreciation_time_unit',
            'depreciation_start_date',
            'depreciation_end_date',
            'increase_fa_list',
            'depreciation_data'
        )

    @classmethod
    def validate_classification(cls, value):
        try:
            return ToolClassification.objects.get(id=value)
        except ToolClassification.DoesNotExist:
            raise serializers.ValidationError({'classification': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_product(cls, value):
        try:
            return Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_manage_department(cls, value):
        try:
            return Group.objects.get(id=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError({'manage_department': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_use_department(cls, value):
        if isinstance(value, list):
            department_list = Group.objects.filter(id__in=value)
            if department_list.count() == len(value):
                return department_list
            raise serializers.ValidationError({"use_department": BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({"use_department": BaseMsg.FORMAT_NOT_MATCH})

    @classmethod
    def validate_asset_code(cls, value):
        if value:
            if InstrumentTool.objects.filter_current(fill__tenant=True, fill__company=True, asset_code=value).exists():
                raise serializers.ValidationError({"asset_code": FixedAssetMsg.CODE_EXIST})
            return value
        raise serializers.ValidationError({"asset_code": BaseMsg.REQUIRED})

    def validate(self, validate_data):
        asset_sources = validate_data.get('asset_sources')
        total_value = validate_data.get('total_value')

        total_value_of_asset_source = 0
        for asset_source in asset_sources:
            total_value_of_asset_source += asset_source.get('value', 0)

        if total_value_of_asset_source != total_value:
            raise serializers.ValidationError({"total_value": FixedAssetMsg.TOTAL_VALUE_MUST_MATCH})
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        use_departments = validated_data.pop('use_department')
        asset_sources = validated_data.pop('asset_sources')
        increase_fa_list = validated_data.pop('increase_fa_list')

        try:
            with transaction.atomic():
                instrument_tool = InstrumentTool.objects.create(**validated_data)

                CommonHandler.create_sub_data(
                    instrument_tool,
                    use_departments=use_departments,
                    asset_sources=asset_sources,
                    increase_fa_list=increase_fa_list,
                    use_department_model=InstrumentToolUseDepartment,
                    source_model=InstrumentToolSource,
                    feature_ap_invoice_item_model=InstrumentToolAPInvoiceItems
                )

            return instrument_tool
        except Exception as err:
            logger.error(msg=f'Create instrument tool errors: {str(err)}')
            raise serializers.ValidationError({'asset': FixedAssetMsg.ERROR_CREATE})


class InstrumentToolDetailSerializer(AbstractDetailSerializerModel):
    classification = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    manage_department = serializers.SerializerMethodField()
    use_department = serializers.SerializerMethodField()
    asset_sources = serializers.SerializerMethodField()
    ap_invoice_items = serializers.SerializerMethodField()
    using_quantity = serializers.SerializerMethodField()

    class Meta:
        model = InstrumentTool
        fields = (
            'id',
            'asset_code',
            'title',
            'classification',
            'product',
            'manage_department',
            'use_department',
            'use_customer',
            'status',
            'source_type',
            'unit_price',
            'quantity',
            'total_value',
            'measure_unit',
            'depreciation_time',
            'depreciation_time_unit',
            'depreciation_start_date',
            'depreciation_end_date',
            'asset_sources',
            'ap_invoice_items',
            'using_quantity'
        )

    @classmethod
    def get_classification(cls, obj):
        return {
            'id': obj.classification.id,
            'code': obj.classification.code,
            'title': obj.classification.title,
        } if obj.classification else {}

    @classmethod
    def get_product(cls, obj):
        return {
            'id': obj.product.id,
            'code': obj.product.code,
            'title': obj.product.title,
        } if obj.product else {}

    @classmethod
    def get_manage_department(cls, obj):
        return {
            'id': obj.manage_department.id,
            'code': obj.manage_department.code,
            'title': obj.manage_department.title,
        } if obj.manage_department else {}

    @classmethod
    def get_use_department(cls, obj):
        data=[]
        for use_department_item in obj.use_departments.all():
            data.append({
                'id': use_department_item.use_department_id,
                'title': use_department_item.use_department.title,
                'code': use_department_item.use_department.code,
            })
        return data

    @classmethod
    def get_asset_sources(cls, obj):
        data=[]
        source_id = ''
        for asset_source in obj.asset_sources.all():
            if asset_source.transaction_type == 0:
                source_id = APInvoice.objects.filter_current(fill__company=True).filter(
                    code=asset_source.code).first().id
            data.append({
                'source_id': source_id,
                'description': asset_source.description,
                'document_no': asset_source.document_no,
                'transaction_type': asset_source.transaction_type,
                'value': asset_source.value,
                'code': asset_source.code,
            })
        return data

    @classmethod
    def get_ap_invoice_items(cls, obj):
        return [
            {
                'ap_invoice_item_id': item.ap_invoice_item_id,
                'increased_FA_value': item.increased_FA_value
            } for item in obj.ap_invoice_items.all()
        ]

    @classmethod
    def get_using_quantity(cls, obj):
        using_quantity = obj.quantity
        for write_off_quantity in obj.write_off_quantities.all():
            using_quantity = using_quantity - write_off_quantity.write_off_quantity
        return using_quantity


class InstrumentToolUpdateSerializer(AbstractCreateSerializerModel):
    classification = serializers.UUIDField()
    product = serializers.UUIDField()
    manage_department = serializers.UUIDField()
    use_department = serializers.ListSerializer(
        child=serializers.UUIDField(required=False)
    )
    asset_sources = ToolAssetSourcesCreateSerializer(many=True)
    increase_fa_list = serializers.JSONField(required=False)
    asset_code = serializers.CharField(required=False)

    class Meta:
        model = InstrumentTool
        fields = (
            'classification',
            'title',
            'asset_code',
            'product',
            'manage_department',
            'use_department',
            'unit_price',
            'quantity',
            'measure_unit',
            'total_value',
            'source_type',
            'asset_sources',
            'depreciation_time',
            'depreciation_time_unit',
            'depreciation_start_date',
            'depreciation_end_date',
            'increase_fa_list',
            'depreciation_data'
        )

    @classmethod
    def validate_classification(cls, value):
        try:
            return ToolClassification.objects.get(id=value)
        except ToolClassification.DoesNotExist:
            raise serializers.ValidationError({'classification': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_product(cls, value):
        try:
            return Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_manage_department(cls, value):
        try:
            return Group.objects.get(id=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError({'manage_department': BaseMsg.NOT_EXIST})

    @classmethod
    def validate_use_department(cls, value):
        if isinstance(value, list):
            department_list = Group.objects.filter(id__in=value)
            if department_list.count() == len(value):
                return department_list
            raise serializers.ValidationError({"use_department": BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({"use_department": BaseMsg.FORMAT_NOT_MATCH})

    def validate_asset_code(self, value):
        if value:
            if InstrumentTool.objects.filter_current(fill__tenant=True, fill__company=True, asset_code=value).exclude(
                    id=self.instance.id).exists():
                raise serializers.ValidationError({"asset_code": FixedAssetMsg.CODE_EXIST})
            return value
        raise serializers.ValidationError({"asset_code": BaseMsg.REQUIRED})

    def validate(self, validate_data):
        asset_sources = validate_data.get('asset_sources')
        total_value = validate_data.get('total_value')

        total_value_of_asset_source = 0
        for asset_source in asset_sources:
            total_value_of_asset_source += asset_source.get('value', 0)

        if total_value_of_asset_source != total_value:
            raise serializers.ValidationError({"total_value": FixedAssetMsg.TOTAL_VALUE_MUST_MATCH})
        return validate_data

    @decorator_run_workflow
    def update(self, instrument_tool, validated_data):
        use_departments = validated_data.pop('use_department')
        asset_sources = validated_data.pop('asset_sources')
        increase_fa_list = validated_data.pop('increase_fa_list')

        try:
            with transaction.atomic():
                for key, value in validated_data.items():
                    setattr(instrument_tool, key, value)
                instrument_tool.save()

                InstrumentToolUseDepartment.objects.filter(instrument_tool=instrument_tool).delete()

                InstrumentToolSource.objects.filter(instrument_tool=instrument_tool).delete()

                instrument_tool_apinvoice_items = InstrumentToolAPInvoiceItems.objects.filter(
                    instrument_tool=instrument_tool)

                for instrument_tool_apinvoice_item in instrument_tool_apinvoice_items:
                    apinvoice_item = instrument_tool_apinvoice_item.ap_invoice_item
                    increased_fa_value = apinvoice_item.increased_FA_value
                    apinvoice_item.increased_FA_value = (
                            increased_fa_value - instrument_tool_apinvoice_item.increased_FA_value
                    )
                    apinvoice_item.save()

                instrument_tool_apinvoice_items.delete()

                CommonHandler.create_sub_data(
                    instrument_tool,
                    use_departments=use_departments,
                    asset_sources=asset_sources,
                    increase_fa_list=increase_fa_list,
                    use_department_model=InstrumentToolUseDepartment,
                    source_model=InstrumentToolSource,
                    feature_ap_invoice_item_model=InstrumentToolAPInvoiceItems
                )

            return instrument_tool
        except Exception as err:
            logger.error(msg=f'Create instrument tool errors: {str(err)}')
            raise serializers.ValidationError({'asset': FixedAssetMsg.ERROR_CREATE})


class ToolForLeaseListSerializer(serializers.ModelSerializer):
    tool_id = serializers.SerializerMethodField()
    origin_cost = serializers.SerializerMethodField()
    net_value = serializers.SerializerMethodField()
    depreciation_time = serializers.SerializerMethodField()

    class Meta:
        model = InstrumentTool
        fields = (
            'id',
            'title',
            'code',
            'tool_id',
            'origin_cost',
            'net_value',
            'depreciation_time',
            'depreciation_start_date',
            'depreciation_end_date',
            'depreciation_data',
        )

    @classmethod
    def get_tool_id(cls, obj):
        return str(obj.id)

    @classmethod
    def get_origin_cost(cls, obj):
        return obj.unit_price

    @classmethod
    def get_net_value(cls, obj):
        return 0 if obj else 0

    @classmethod
    def get_depreciation_time(cls, obj):
        return obj.depreciation_time


class ToolStatusLeaseListSerializer(serializers.ModelSerializer):
    quantity_leased = serializers.SerializerMethodField()
    asset_type = serializers.SerializerMethodField()
    lease_order_data = serializers.SerializerMethodField()
    origin_cost = serializers.SerializerMethodField()
    net_value = serializers.SerializerMethodField()

    class Meta:
        model = InstrumentTool
        fields = (
            'id',
            'title',
            'code',
            'quantity',
            'quantity_leased',
            'asset_type',
            'status',
            'lease_order_data',

            'origin_cost',
            'net_value',
            'depreciation_time',
            'depreciation_start_date',
            'depreciation_end_date',
            'depreciation_data',
        )

    @classmethod
    def get_quantity_leased(cls, obj):
        delivery_product_tool = obj.delivery_pt_tool.first()
        if delivery_product_tool:
            return delivery_product_tool.quantity_remain_recovery
        return 0

    @classmethod
    def get_asset_type(cls, obj):
        return 'tool' if obj else ''

    @classmethod
    def get_lease_order_data(cls, obj):
        lease_order = None
        delivery_product_tool = obj.delivery_pt_tool.first()
        if delivery_product_tool and obj.status == 2:
            if delivery_product_tool.delivery_sub:
                if delivery_product_tool.delivery_sub.order_delivery:
                    lease_order = delivery_product_tool.delivery_sub.order_delivery.lease_order
        return {
            'id': lease_order.id,
            'title': lease_order.title,
            'code': lease_order.code,
            'customer': {
                'id': lease_order.customer_id,
                'title': lease_order.customer.name,
                'code': lease_order.customer.code
            } if lease_order.customer else {},
            'product_lease_start_date': delivery_product_tool.product_lease_start_date,
            'product_lease_end_date': delivery_product_tool.product_lease_end_date,
        } if lease_order else {}

    @classmethod
    def get_origin_cost(cls, obj):
        return obj.unit_price

    @classmethod
    def get_net_value(cls, obj):
        return 0 if obj else 0

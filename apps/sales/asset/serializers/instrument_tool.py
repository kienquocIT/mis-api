import logging
from django.db import transaction
from rest_framework import serializers

from apps.core.hr.models import Group
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Product, ToolClassification
from apps.sales.apinvoice.models import APInvoiceItems, APInvoice
from apps.sales.asset.models import InstrumentTool, InstrumentToolUseDepartment, InstrumentToolSource, \
    InstrumentToolAPInvoiceItems
from apps.shared import BaseMsg, FixedAssetMsg, AbstractCreateSerializerModel, AbstractDetailSerializerModel, \
    AbstractListSerializerModel

logger = logging.getLogger(__name__)

__all__= [
    'InstrumentToolListSerializer',
    'InstrumentToolCreateSerializer',
    'InstrumentToolDetailSerializer',
    'InstrumentToolUpdateSerializer'
]


class AssetSourcesCreateSerializer(serializers.ModelSerializer):
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
            'depreciation_time_unit'
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


class InstrumentToolCreateSerializer(AbstractCreateSerializerModel):
    classification = serializers.UUIDField()
    product = serializers.UUIDField()
    manage_department = serializers.UUIDField()
    use_department = serializers.ListSerializer(
        child=serializers.UUIDField(required=False)
    )
    asset_sources = AssetSourcesCreateSerializer(many=True)
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
            'increase_fa_list'
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
    def create(self, validated_data): # pylint: disable=R0914
        use_departments = validated_data.pop('use_department')
        asset_sources = validated_data.pop('asset_sources')
        increase_fa_list = validated_data.pop('increase_fa_list')

        try:
            with transaction.atomic():
                instrument_tool = InstrumentTool.objects.create(**validated_data)

                bulk_data = []
                for use_department in use_departments:
                    bulk_data.append(InstrumentToolUseDepartment(
                        instrument_tool= instrument_tool,
                        use_department= use_department,
                    ))
                InstrumentToolUseDepartment.objects.bulk_create(bulk_data)

                bulk_data = []
                for asset_source in asset_sources:
                    bulk_data.append(InstrumentToolSource(
                        instrument_tool= instrument_tool,
                        description= asset_source.get('description'),
                        code= asset_source.get('code'),
                        document_no= asset_source.get('document_no'),
                        transaction_type= asset_source.get('transaction_type'),
                        value= asset_source.get('value')
                    ))
                InstrumentToolSource.objects.bulk_create(bulk_data)

                bulk_data = []
                # format of increase_fa_list: increase_fa_list = {
                #     apinvoiceid: {
                #         apinvoiceitemid : value
                #     }
                # }
                for ap_invoice_id_key, items in increase_fa_list.items():
                    ap_invoice_items = APInvoiceItems.objects.filter(ap_invoice=ap_invoice_id_key)
                    ap_invoice_items_dict = {str(item.id): item for item in ap_invoice_items}
                    for ap_invoice_item_id_key, value in items.items():
                        bulk_data.append(InstrumentToolAPInvoiceItems(
                            instrument_tool= instrument_tool,
                            ap_invoice_item_id= ap_invoice_item_id_key,
                            increased_FA_value= value
                        ))
                        if ap_invoice_item_id_key in ap_invoice_items_dict:
                            item = ap_invoice_items_dict[ap_invoice_item_id_key]
                            item.increased_FA_value += value
                            item.save()
                InstrumentToolAPInvoiceItems.objects.bulk_create(bulk_data)
        except Exception as err:
            logger.error(msg=f'Create instrument tool errors: {str(err)}')
            raise serializers.ValidationError({'asset': FixedAssetMsg.ERROR_CREATE})

        return instrument_tool


class InstrumentToolDetailSerializer(AbstractDetailSerializerModel):
    classification = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    manage_department = serializers.SerializerMethodField()
    use_department = serializers.SerializerMethodField()
    asset_sources = serializers.SerializerMethodField()
    ap_invoice_items = serializers.SerializerMethodField()

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
            'ap_invoice_items'
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


class InstrumentToolUpdateSerializer(AbstractCreateSerializerModel):
    classification = serializers.UUIDField()
    product = serializers.UUIDField()
    manage_department = serializers.UUIDField()
    use_department = serializers.ListSerializer(
        child=serializers.UUIDField(required=False)
    )
    asset_sources = AssetSourcesCreateSerializer(many=True)
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
            'increase_fa_list'
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
    def update(self, instrument_tool, validated_data): # pylint: disable=R0914
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

                bulk_data = []
                for use_department in use_departments:
                    bulk_data.append(InstrumentToolUseDepartment(
                        instrument_tool= instrument_tool,
                        use_department= use_department,
                    ))
                InstrumentToolUseDepartment.objects.bulk_create(bulk_data)

                bulk_data = []
                for asset_source in asset_sources:
                    bulk_data.append(InstrumentToolSource(
                        instrument_tool= instrument_tool,
                        description= asset_source.get('description'),
                        code= asset_source.get('code'),
                        document_no= asset_source.get('document_no'),
                        transaction_type= asset_source.get('transaction_type'),
                        value= asset_source.get('value')
                    ))
                InstrumentToolSource.objects.bulk_create(bulk_data)

                bulk_data = []
                # format of increase_fa_list: increase_fa_list = {
                #     apinvoiceid: {
                #         apinvoiceitemid : value
                #     }
                # }
                for ap_invoice_id_key, items in increase_fa_list.items():
                    ap_invoice_items = APInvoiceItems.objects.filter(ap_invoice=ap_invoice_id_key)
                    ap_invoice_items_dict = {str(item.id): item for item in ap_invoice_items}
                    for ap_invoice_item_id_key, value in items.items():
                        bulk_data.append(InstrumentToolAPInvoiceItems(
                            instrument_tool= instrument_tool,
                            ap_invoice_item_id= ap_invoice_item_id_key,
                            increased_FA_value= value
                        ))
                        if ap_invoice_item_id_key in ap_invoice_items_dict:
                            item = ap_invoice_items_dict[ap_invoice_item_id_key]
                            item.increased_FA_value += value
                            item.save()
                InstrumentToolAPInvoiceItems.objects.bulk_create(bulk_data)
        except Exception as err:
            logger.error(msg=f'Create instrument tool errors: {str(err)}')
            raise serializers.ValidationError({'asset': FixedAssetMsg.ERROR_CREATE})

        return instrument_tool

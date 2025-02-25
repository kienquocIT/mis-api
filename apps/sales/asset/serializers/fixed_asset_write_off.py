import logging
from django.db import transaction
from rest_framework import serializers

from apps.core.hr.models import Group
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import FixedAssetClassification, Product
from apps.sales.apinvoice.models import APInvoiceItems, APInvoice
from apps.sales.asset.models import FixedAsset, FixedAssetSource, FixedAssetUseDepartment, FixedAssetAPInvoiceItems, \
    FixedAssetWriteOff
from apps.shared import BaseMsg, FixedAssetMsg, AbstractCreateSerializerModel, AbstractDetailSerializerModel, \
    AbstractListSerializerModel

logger = logging.getLogger(__name__)

__all__= [
    'FixedAssetWriteOffListSerializer',
    'FixedAssetWriteOffCreateSerializer',
    'FixedAssetWriteOffDetailSerializer'
]


class AssetSourcesCreateSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    @classmethod
    def validate_description(cls, value):
        if not value:
            raise serializers.ValidationError({"description": FixedAssetMsg.DESCRIPTION_REQUIRED})
        return value

    class Meta:
        model = FixedAssetSource
        fields = (
            'description',
            'document_no',
            'transaction_type',
            'code',
            'value'
        )


class FixedAssetWriteOffListSerializer(AbstractListSerializerModel):
    type = serializers.SerializerMethodField()

    class Meta:
        model = FixedAssetWriteOff
        fields = (
            'id',
            'code',
            'title',
            'document_date',
            'posting_date',
            'type'
        )

    @classmethod
    def get_type(cls, obj):
        return obj.get_type_display()


class FixedAssetWriteOffCreateSerializer(AbstractCreateSerializerModel):
    asset_list = serializers.SerializerMethodField()

    class Meta:
        model = FixedAssetWriteOff
        fields = (
            'note',
            'posting_date',
            'document_date',
            'type',
            'asset_list'
        )

    @classmethod
    def validate_asset_list(cls, value):
        if not value:
            raise serializers.ValidationError({'asset_list': FixedAssetMsg.ASSET_LIST_REQUIRED})
        return value


    @decorator_run_workflow
    def create(self, validated_data): # pylint: disable=R0914
        asset_list = validated_data.pop('asset_list')

        try:
            with transaction.atomic():
                fixed_asset_write_off = FixedAssetWriteOff.objects.create(**validated_data)

        except Exception as err:
            logger.error(msg=f'Create fixed asset write off errors: {str(err)}')
            raise serializers.ValidationError({'asset': FixedAssetMsg.ERROR_CREATE})

        return fixed_asset_write_off


class FixedAssetWriteOffDetailSerializer(AbstractDetailSerializerModel):
    asset_list = serializers.SerializerMethodField()

    class Meta:
        model = FixedAssetWriteOff
        fields = (
            'id',
            'note',
            'posting_date',
            'document_date',
            'type',
            'asset_list'
        )

    @classmethod
    def get_asset_list(cls, obj):
        return {

        }

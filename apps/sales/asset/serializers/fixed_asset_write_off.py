import logging
from django.db import transaction
from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.asset.models import FixedAsset, FixedAssetWriteOff
from apps.shared import BaseMsg, FixedAssetMsg, AbstractCreateSerializerModel, AbstractDetailSerializerModel, \
    AbstractListSerializerModel

logger = logging.getLogger(__name__)

__all__= [
    'FixedAssetWriteOffListSerializer',
    'FixedAssetWriteOffCreateSerializer',
    'FixedAssetWriteOffDetailSerializer',
    'FixedAssetWriteOffUpdateSerializer'
]


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


class AssetListCreateSerializer(AbstractCreateSerializerModel):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = FixedAsset
        fields = ('id', 'asset_code')

    @classmethod
    def validate_id(cls, value):
        if value:
            try:
                return FixedAsset.objects.get(id=value).id
            except FixedAsset.DoesNotExist():
                raise serializers.ValidationError({'asset_list': FixedAssetMsg.ASSET_NOT_FOUND})
        raise serializers.ValidationError({'id': BaseMsg.REQUIRED})

    def validate(self, validate_data): # pylint: disable=C0103
        asset_id = validate_data.get('id', None)
        fa = FixedAsset.objects.filter(id=asset_id).first()

        if fa:
            fa_writeoff = fa.fixed_asset_write_off
            if fa_writeoff:
                raise serializers.ValidationError({'asset_list': FixedAssetMsg.ASSET_ALREADY_WRITTEN_OFF})

        return validate_data


class FixedAssetWriteOffCreateSerializer(AbstractCreateSerializerModel):
    asset_list = AssetListCreateSerializer(many=True)

    class Meta:
        model = FixedAssetWriteOff
        fields = (
            'title',
            'note',
            'posting_date',
            'document_date',
            'type',
            'asset_list'
        )

    @decorator_run_workflow
    def create(self, validated_data):
        asset_list = validated_data.pop('asset_list')

        try:
            with transaction.atomic():
                fixed_asset_write_off = FixedAssetWriteOff.objects.create(**validated_data)

                asset_ids = [asset['id'] for asset in asset_list]
                FixedAsset.objects.filter(id__in=asset_ids).update(fixed_asset_write_off=fixed_asset_write_off)

        except Exception as err:
            logger.error(msg=f'Create fixed asset write off errors: {str(err)}')
            raise serializers.ValidationError({'fixed asset write off': FixedAssetMsg.ERROR_CREATE})

        return fixed_asset_write_off


class AssetListUpdateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = FixedAsset
        fields = ('id','asset_code')

    @classmethod
    def validate_id(cls, value):
        if value:
            try:
                return FixedAsset.objects.get(id=value).id
            except FixedAsset.DoesNotExist():
                raise serializers.ValidationError({'asset_list': FixedAssetMsg.ASSET_NOT_FOUND})
        raise serializers.ValidationError({'id': BaseMsg.REQUIRED})

    def validate(self, validate_data): # pylint: disable=C0103
        asset_id = validate_data.get('id', None)
        fa = FixedAsset.objects.filter(id=asset_id).first()
        current_fa_writeoff_id = self.context.get('fixed_asset_write_off_id', None)
        if fa and fa.fixed_asset_write_off:
            if str(fa.fixed_asset_write_off.id) != current_fa_writeoff_id:
                raise serializers.ValidationError({'asset_list': FixedAssetMsg.ASSET_ALREADY_WRITTEN_OFF})

        return validate_data


class FixedAssetWriteOffUpdateSerializer(AbstractCreateSerializerModel):
    asset_list = AssetListUpdateSerializer(many=True)

    class Meta:
        model = FixedAssetWriteOff
        fields = (
            'title',
            'note',
            'posting_date',
            'document_date',
            'type',
            'asset_list'
        )

    @decorator_run_workflow
    def update(self, fixed_asset_write_off, validated_data):
        asset_list = validated_data.pop('asset_list')

        try:
            with transaction.atomic():
                for key, value in validated_data.items():
                    setattr(fixed_asset_write_off, key, value)
                fixed_asset_write_off.save()

                fixed_asset_write_off.write_off_fixed_assets.update(fixed_asset_write_off=None)

                asset_ids = [asset['id'] for asset in asset_list]
                FixedAsset.objects.filter(id__in=asset_ids).update(fixed_asset_write_off=fixed_asset_write_off)

        except Exception as err:
            logger.error(msg=f'Update fixed asset write off errors: {str(err)}')
            raise serializers.ValidationError({'fixed asset write off': FixedAssetMsg.ERROR_CREATE})

        return fixed_asset_write_off


class FixedAssetWriteOffDetailSerializer(AbstractDetailSerializerModel):
    asset_list = serializers.SerializerMethodField()

    class Meta:
        model = FixedAssetWriteOff
        fields = (
            'id',
            'note',
            'title',
            'posting_date',
            'document_date',
            'type',
            'asset_list'
        )

    @classmethod
    def get_asset_list(cls, obj):
        data = []
        for asset in obj.write_off_fixed_assets.all():
            data.append({
                'id': asset.id,
                'title': asset.title,
                'asset_code': asset.asset_code,
                'fa_status': asset.get_status_display(),
                'manage_department': {
                    'id': asset.manage_department.id,
                    'code': asset.manage_department.code,
                    'title': asset.manage_department.title,
                } if asset.manage_department else {},
                'use_department': [
                    {
                        'id': use_department_item.use_department_id,
                        'title': use_department_item.use_department.title,
                        'code': use_department_item.use_department.code,
                    } for use_department_item in asset.use_departments.all()
                ],
                'depreciation_time': asset.depreciation_time,
                'depreciation_time_unit': asset.depreciation_time_unit,
                'original_cost': asset.original_cost,
                'accumulative_depreciation': asset.accumulative_depreciation,
                'net_book_value': asset.net_book_value,
            })
        return data

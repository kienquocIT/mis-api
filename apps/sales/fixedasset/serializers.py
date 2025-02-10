from rest_framework import serializers

from apps.core.hr.models import Group
from apps.masterdata.saledata.models import FixedAssetClassification, Product
from apps.sales.fixedasset.models import FixedAsset, FixedAssetSource
from apps.shared import BaseMsg


class AssetSourcesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedAssetSource
        fields = (
            'description',
            'document_no',
            'transaction_type',
            'code',
            'value'
        )


class FixedAssetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedAsset
        fields = (
            'code',
            'title'
        )


class FixedAssetCreateSerializer(serializers.ModelSerializer):
    classification = serializers.UUIDField()
    product = serializers.UUIDField()
    manage_department = serializers.UUIDField()
    use_department = serializers.ListSerializer(
        child=serializers.UUIDField(required=False)
    )
    asset_sources = AssetSourcesCreateSerializer(many=True)

    class Meta:
        model = FixedAsset
        fields = (
            'classification',
            'title',
            'code',
            'product',
            'manage_department',
            'use_department',
            'original_cost',
            'source_type',
            'asset_sources',
            'depreciation_method',
            'depreciation_time',
            'depreciation_time_unit',
            'adjustment_factor',
            'depreciation_start_date',
            'depreciation_end_date'
        )

    @classmethod
    def validate_classification(cls, value):
        try:
            return FixedAssetClassification.objects.get(id=value)
        except FixedAssetClassification.DoesNotExist:
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

    # @classmethod
    # def validate_depreciation_time(cls, value):
    #     if isinstance(value, int):
    #     raise serializers.ValidationError({"depreciation_time": BaseMsg.FORMAT_NOT_MATCH})

    def create(self, validated_data):
        fixed_asset = FixedAsset.objects.create(**validated_data)

        return fixed_asset

class FixedAssetDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedAsset
        fields = (
            'code',
            'title'
        )
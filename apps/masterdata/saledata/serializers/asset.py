from rest_framework import serializers

from apps.masterdata.saledata.models import FixedAssetClassification, ToolClassification

__all__ = [
    'FixedAssetClassificationGroupListSerializer',
    'FixedAssetClassificationListSerializer',
    'ToolClassificationCreateSerializer',
    'ToolClassificationDetailSerializer',
    'ToolClassificationUpdateSerializer',
    'ToolClassificationListSerializer'
]

from apps.shared import BaseMsg, FixedAssetMsg


class FixedAssetClassificationGroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedAssetClassification
        fields = (
            'id',
            'title',
            'code',
            'is_default'
        )


class FixedAssetClassificationListSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()

    class Meta:
        model = FixedAssetClassification
        fields = (
            'id',
            'title',
            'code',
            'group',
            'is_default'
        )

    @classmethod
    def get_group(cls, obj):
        return {
            'id': obj.group.id,
            'title': obj.group.title,
            'code': obj.group.code,
        } if obj.group else {}


class ToolClassificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolClassification
        fields = (
            'id',
            'title',
            'code',
            'is_default'
        )


class ToolClassificationCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100)

    class Meta:
        model = ToolClassification
        fields = (
            'title',
            'code'
        )

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": BaseMsg.REQUIRED})

    @classmethod
    def validate_code(cls, value):
        if value:
            if ToolClassification.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError(FixedAssetMsg.CODE_EXIST)
            return value
        raise serializers.ValidationError({"code": BaseMsg.REQUIRED})


class ToolClassificationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolClassification
        fields = (
            'id',
            'title',
            'code',
        )


class ToolClassificationUpdateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100)

    class Meta:
        model = ToolClassification
        fields = ('code', 'title')

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": BaseMsg.REQUIRED})

    def validate_code(self, value):
        if value:
            if ToolClassification.objects.filter_current(
                    fill__tenant=True, fill__company=True, code=value
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(FixedAssetMsg.CODE_EXIST)
            return value
        raise serializers.ValidationError({"code": BaseMsg.REQUIRED})

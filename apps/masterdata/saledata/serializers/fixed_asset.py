from rest_framework import serializers

from apps.masterdata.saledata.models import FixedAssetClassification

__all__ = [
    'FixedAssetClassificationGroupListSerializer',
    'FixedAssetClassificationListSerializer',
]

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

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from apps.accounting.accountingsettings.models import Dimension, DimensionValue

__all__ = [
    'DimensionDefinitionListSerializer',
    'DimensionDefinitionCreateSerializer',
    'DimensionDefinitionDetailSerializer',
    'DimensionDefinitionUpdateSerializer',
    'DimensionDefinitionWithValuesSerializer',
    'DimensionWithSyncConfigListSerializer'
]


class DimensionDefinitionListSerializer(serializers.ModelSerializer):
    related_app = SerializerMethodField()

    class Meta:
        model = Dimension
        fields = (
            'id',
            'title',
            'code',
            'related_app',
        )

    @classmethod
    def get_related_app(cls, obj):
        return {
            'title': obj.related_app.title,
            'code': obj.related_app.code,
        } if obj.related_app else None


class DimensionDefinitionCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(error_messages={
        'required': _('Title is required')
    })
    code = serializers.CharField()

    class Meta:
        model = Dimension
        fields = (
            'title',
            'code',
        )

    @classmethod
    def validate_code(cls, value):
        if not value:
            raise serializers.ValidationError({"code": _("Code is required")})

        if Dimension.objects.filter_on_company(code=value).exists():
            raise serializers.ValidationError({"code": _("Code already exists")})

        return value


class DimensionDefinitionDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dimension
        fields = (
            'id',
            'title',
            'code',
        )


class DimensionDefinitionUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(error_messages={
        'required': _('Title is required')
    })
    code = serializers.CharField()

    class Meta:
        model = Dimension
        fields = (
            'title',
            'code',
        )

    def validate_code(self, value):
        if not value:
            raise serializers.ValidationError({"code": _("Code is required")})

        if Dimension.objects.filter_on_company(code=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError({"code": _("Code already exists")})

        return value

    def validate(self, validated_data):
        related_app = self.instance.related_app
        if related_app:
            title = related_app.title
            raise serializers.ValidationError({"dimension": _(f"Dimension is sync with {title}")})
        return validated_data


class DimensionDefinitionWithValuesSerializer(serializers.ModelSerializer):
    values = serializers.SerializerMethodField()
    is_system_dimension = SerializerMethodField()

    class Meta:
        model = Dimension
        fields = (
            'id',
            'title',
            'code',
            'values',
            'is_system_dimension'
        )

    def get_values(self, obj):
        """Return all DimensionValues under this definition."""
        values = DimensionValue.objects.filter(dimension=obj).select_related('parent')

        result = []
        for item in values:
            level = 0
            parent = item.parent
            while parent:
                level += 1
                parent = parent.parent

            result.append({
                "id": item.id,
                "code": item.code,
                "title": item.title,
                "allow_posting": item.allow_posting,
                "parent_id": item.parent.id if item.parent else None,
                "has_children": item.child_values.exists(),
                "children_ids": list(item.child_values.values_list("id", flat=True)),
                "level": level,
                "related_app_id": item.related_app_id,
                'is_system_created': True if item.related_app else False,
            })

        return result

    def get_is_system_dimension(self, obj):
        return True if obj.related_app else False

class DimensionWithSyncConfigListSerializer(serializers.ModelSerializer):
    related_app = SerializerMethodField()
    sync_status = SerializerMethodField()
    record_number = SerializerMethodField()

    class Meta:
        model = Dimension
        fields = (
            'id',
            'title',
            'code',
            'related_app',
            'sync_status',
            'record_number'
        )

    @classmethod
    def get_related_app(cls, obj):
        return {
            'title': obj.related_app.get('title', ''),
            'code': obj.related_app.get('code', ''),
        } if obj.related_app else None

    @classmethod
    def get_sync_status(cls, obj):
        if obj.configs:
            return ''
        return True

    @classmethod
    def get_record_number(cls, obj):
        return obj.dimension_values.count()


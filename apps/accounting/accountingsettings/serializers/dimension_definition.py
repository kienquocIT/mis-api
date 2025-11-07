from django.db import transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounting.accountingsettings.models import DimensionDefinition, DimensionValue

__all__ = [
    'DimensionDefinitionListSerializer',
    'DimensionDefinitionCreateSerializer',
    'DimensionDefinitionDetailSerializer',
    'DimensionDefinitionUpdateSerializer',
    'DimensionDefinitionWithValuesSerializer'
]

class DimensionDefinitionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = DimensionDefinition
        fields = (
            'id',
            'title',
            'code',
        )


class DimensionDefinitionCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(error_messages={
        'required': _('Title is required')
    })
    code = serializers.CharField()

    class Meta:
        model = DimensionDefinition
        fields = (
            'title',
            'code',
        )

    @classmethod
    def validate_code(cls, value):
        if not value:
            raise serializers.ValidationError({"code": _("Code is required")})

        if DimensionDefinition.objects.filter_on_company(code=value).exists():
            raise serializers.ValidationError({"code": _("Code already exists")})

        return value


class DimensionDefinitionDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DimensionDefinition
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
        model = DimensionDefinition
        fields = (
            'title',
            'code',
        )


    def validate_code(self, value):
        if not value:
            raise serializers.ValidationError({"code": _("Code is required")})

        if DimensionDefinition.objects.filter_on_company(code=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError({"code": _("Code already exists")})

        return value



class DimensionDefinitionWithValuesSerializer(serializers.ModelSerializer):
    values = serializers.SerializerMethodField()

    class Meta:
        model = DimensionDefinition
        fields = (
            'id',
            'title',
            'code',
            'values',
        )

    def get_values(self, obj):
        """Return all DimensionValues under this definition."""
        values = DimensionValue.objects.filter(dimension=obj).select_related('parent')

        result = []
        for v in values:
            level = 0
            parent = v.parent
            while parent:
                level += 1
                parent = parent.parent

            result.append({
                "id": v.id,
                "code": v.code,
                "title": v.title,
                "allow_posting": v.allow_posting,
                "parent_id": v.parent.id if v.parent else None,
                "has_children": v.child_values.exists(),
                "children_ids": list(v.child_values.values_list("id", flat=True)),
                "level": level,
                "related_app_id": v.related_app_id,
                "related_app_code": v.related_app_code,
            })

        return result

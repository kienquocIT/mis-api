from django.db import transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.accounting.accountingsettings.models import DimensionValue, DimensionDefinition

__all__ = [
    'DimensionValueListSerializer',
    'DimensionValueCreateSerializer',
    'DimensionValueDetailSerializer',
    'DimensionValueUpdateSerializer'
]

class DimensionValueDetailSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(source="parent.id", read_only=True)
    has_children = serializers.SerializerMethodField()
    children_ids = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    class Meta:
        model = DimensionValue
        fields = (
            "id",
            "code",
            "title",
            "allow_posting",
            "dimension",
            "parent_id",
            "has_children",
            "children_ids",
            "level",
            "related_app_id",
            "related_app_code",
        )

    @classmethod
    def get_has_children(cls, obj):
        return obj.child_values.exists()

    @classmethod
    def get_children_ids(cls, obj):
        return list(obj.child_values.values_list("id", flat=True))

    @classmethod
    def get_level(cls, obj):
        level = 0
        current = obj.parent
        while current:
            level += 1
            current = current.parent
        return level


class DimensionValueListSerializer(serializers.ModelSerializer):
    parent_id = serializers.UUIDField(source="parent.id")
    has_children = serializers.SerializerMethodField()
    children_ids = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    class Meta:
        model = DimensionValue
        fields = (
            "id",
            "code",
            "title",
            "allow_posting",
            "dimension",
            "parent_id",
            "has_children",
            "children_ids",
            "level",
            "related_app_id",
            "related_app_code",
        )

    @classmethod
    def get_has_children(cls, obj):
        return obj.child_values.exists()

    @classmethod
    def get_children_ids(cls, obj):
        return list(obj.child_values.values_list("id", flat=True))

    @classmethod
    def get_level(cls, obj):
        level = 0
        current = obj.parent
        while current:
            level += 1
            current = current.parent
        return level


class DimensionValueCreateSerializer(serializers.ModelSerializer):
    dimension_id = serializers.UUIDField(error_messages={
        'required': _("Dimension is required."),
    })
    parent_id = serializers.UUIDField(allow_null=True)

    class Meta:
        model = DimensionValue
        fields = (
            "code",
            "title",
            "allow_posting",
            "dimension_id",
            "parent_id",
            "related_app_id",
            "related_app_code",
        )

    @classmethod
    def validate_parent_id(cls, value):
        if value:
            try:
                dimension_value = DimensionValue.objects.get_on_company(id=value)
                return dimension_value.id
            except DimensionValue.DoesNotExist:
                raise serializers.ValidationError(_("Parent does not exist"))
        return value

    @classmethod
    def validate_dimension_id(cls, value):
        if value:
            try:
                dimension = DimensionDefinition.objects.get_on_company(id=value)
                return dimension.id
            except DimensionDefinition.DoesNotExist:
                raise serializers.ValidationError(_("Dimension definition does not exist"))
        return value

class DimensionValueUpdateSerializer(serializers.ModelSerializer):
    dimension_id = serializers.UUIDField(error_messages={
        'required': _("Dimension is required."),
    })
    parent_id = serializers.UUIDField(allow_null=True)

    class Meta:
        model = DimensionValue
        fields = (
            "code",
            "title",
            "allow_posting",
            "dimension_id",
            "parent_id",
            "related_app_id",
            "related_app_code",
        )

    @classmethod
    def validate_parent_id(cls, value):
        if value:
            try:
                dimension_value = DimensionValue.objects.get_on_company(id=value)
                return dimension_value.id
            except DimensionValue.DoesNotExist:
                raise serializers.ValidationError(_("Parent does not exist"))
        return value

    @classmethod
    def validate_dimension_id(cls, value):
        if value:
            try:
                dimension = DimensionDefinition.objects.get_on_company(id=value)
                return dimension.id
            except DimensionDefinition.DoesNotExist:
                raise serializers.ValidationError(_("Dimension definition does not exist"))
        return value

    def validate(self, attrs):
        new_parent_id = attrs.get("parent_id", None)
        parent = DimensionValue.objects.filter_on_company(id=new_parent_id).first()
        if parent and parent == self.instance:
            raise serializers.ValidationError(
                {"parent": _("A value cannot be its own parent.")}
            )
        return attrs

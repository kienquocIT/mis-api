from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from apps.accounting.accountingsettings.models import Dimension, DimensionValue, DimensionSplitTemplate, \
    DimensionSplitTemplateLine, ChartOfAccounts

__all__ = [
    'DimensionSplitTemplateListSerializer',
    'DimensionSplitTemplateCreateSerializer',
    'DimensionSplitTemplateDetailSerializer',
    'DimensionSplitTemplateUpdateSerializer'
]

class DimensionSplitTemplateListSerializer(serializers.ModelSerializer):
    line_count = serializers.SerializerMethodField()
    dimension = serializers.SerializerMethodField()
    line_data = serializers.SerializerMethodField()

    class Meta:
        model = DimensionSplitTemplate
        fields = (
            "id",
            "code",
            "title",
            "dimension",
            "line_count",
            'is_active',
            'line_data'
        )

    @classmethod
    def get_line_count(cls, obj):
        return obj.split_template_lines.count()

    @classmethod
    def get_dimension(cls, obj):
        return {
            'id': obj.dimension.id,
            'title': obj.dimension.title,
            'code': obj.dimension.code,
        } if obj.dimension else None

    @classmethod
    def get_line_data(cls, obj):
        return [{
            'id': item.id,
            'dimension_value_data': {
                'id': item.dimension_value.id,
                'title': item.dimension_value.title,
                'code': item.dimension_value.code,
            } if item.dimension_value else {},
            'overwrite_account_data': {
                'id': item.overwrite_account.id,
                'acc_name': item.overwrite_account.acc_name,
                'acc_code': item.overwrite_account.acc_code,
            } if item.overwrite_account else {},
            'percent': item.percent,
        } for item in obj.split_template_lines.all()]


class DimensionSplitTemplateLineSerializer(serializers.ModelSerializer):
    dimension_value_id = serializers.UUIDField(error_messages={
        'required': _('Dimension value is required'),
        'null': _('Dimension value must not be null'),
    })
    overwrite_account_id = serializers.UUIDField()

    class Meta:
        model = DimensionSplitTemplateLine
        fields = (
            "order",
            "dimension_value_id",
            "overwrite_account_id",
            "percent",
        )

    @classmethod
    def validate_dimension_value_id(cls, value):
        try:
            return DimensionValue.objects.get(id=value).id
        except DimensionValue.DoesNotExist:
            raise serializers.ValidationError({'dimension_value': _('Dimension value does not exist')})

    @classmethod
    def validate_overwrite_account_id(cls, value):
        if value:
            try:
                return ChartOfAccounts.objects.get(id=value).id
            except ChartOfAccounts.DoesNotExist:
                raise serializers.ValidationError({'overwrite_account_id': _('ChartOfAccounts does not exist')})
        return value


class DimensionSplitTemplateCreateSerializer(serializers.ModelSerializer):
    line_data = DimensionSplitTemplateLineSerializer(many=True)
    dimension_id = serializers.UUIDField(error_messages={
        'required': _('Dimension is required'),
        'null': _('Dimension must not be null'),
    })

    class Meta:
        model = DimensionSplitTemplate
        fields = (
            "code",
            "title",
            "dimension_id",
            "line_data",
        )

    @classmethod
    def validate_dimension_id(cls, value):
        try:
            return Dimension.objects.get(id=value).id
        except Dimension.DoesNotExist:
            raise serializers.ValidationError({'dimension_id': _('Dimension does not exist')})

    def validate_line_data(self, line_data):
        if line_data:
            total_percent = sum(line.get('percent', 0) for line in line_data)
            if total_percent != 100:
                raise serializers.ValidationError({'lines': _("Total percent of all lines must equal 100")})
        return line_data

    @transaction.atomic
    def create(self, validated_data):
        line_data = validated_data.pop('line_data', [])
        split_template = DimensionSplitTemplate.objects.create(**validated_data)

        bulk_data = []
        for line in line_data:
            bulk_data.append(
                DimensionSplitTemplateLine(
                    split_template=split_template,
                    order=line.get('order', 0),
                    percent=line.get('percent', 0),
                    dimension_value_id=line.get('dimension_value_id', None),
                    overwrite_account_id=line.get('overwrite_account_id', None),
                ))

        DimensionSplitTemplateLine.objects.bulk_create(bulk_data)

        return split_template


class DimensionSplitTemplateDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DimensionSplitTemplate
        fields = (
            'id',
            'title'
        )


class DimensionSplitTemplateUpdateSerializer(serializers.ModelSerializer):
    line_data = DimensionSplitTemplateLineSerializer(many=True)
    dimension_id = serializers.UUIDField(error_messages={
        'required': _('Dimension is required'),
        'null': _('Dimension must not be null'),
    })

    class Meta:
        model = DimensionSplitTemplate
        fields = (
            "code",
            "title",
            "dimension_id",
            "line_data",
        )

    @classmethod
    def validate_dimension_id(cls, value):
        try:
            return Dimension.objects.get(id=value).id
        except Dimension.DoesNotExist:
            raise serializers.ValidationError({'dimension_id': _('Dimension does not exist')})

    def validate_line_data(self, line_data):
        if line_data:
            total_percent = sum(line.get('percent', 0) for line in line_data)
            if total_percent != 100:
                raise serializers.ValidationError({'lines': _("Total percent of all lines must equal 100")})
        return line_data

    @transaction.atomic
    def update(self, instance, validated_data):
        line_data = validated_data.pop('line_data', [])

        instance.split_template_lines.all().delete()

        bulk_data = []
        for line in line_data:
            bulk_data.append(
                DimensionSplitTemplateLine(
                    split_template=instance,
                    order=line.get('order', 0),
                    percent=line.get('percent', 0),
                    dimension_value_id=line.get('dimension_value_id', None),
                    overwrite_account_id=line.get('overwrite_account_id', None),
                ))

        DimensionSplitTemplateLine.objects.bulk_create(bulk_data)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from apps.accounting.accountingsettings.models import Dimension, DimensionValue, DimensionSyncConfig

__all__ = [
    'DimensionSyncConfigListSerializer',
    'DimensionSyncConfigCreateSerializer',
    'DimensionSyncConfigUpdateSerializer',
    'DimensionSyncConfigDetailSerializer',
    'DimensionSyncConfigApplicationListSerializer'
]

from apps.core.base.models import Application


class DimensionSyncConfigListSerializer(serializers.ModelSerializer):
    related_app = SerializerMethodField()
    dimension = SerializerMethodField()
    record_number = SerializerMethodField()

    class Meta:
        model = DimensionSyncConfig
        fields = (
            'id',
            'dimension',
            'related_app',
            'record_number'
        )

    @classmethod
    def get_dimension(cls, obj):
        return {
            'id': obj.dimension.id,
            'title': obj.dimension.title,
            'code': obj.dimension.code,
        } if obj.dimension else None

    @classmethod
    def get_related_app(cls, obj):
        return {
            'id': obj.related_app.id,
            'title': obj.related_app.title,
            'code': obj.related_app.code,
        } if obj.related_app else None

    @classmethod
    def get_record_number(cls, obj):
        if obj.dimension:
            return obj.dimension.dimension_values.count()
        return 0


class DimensionSyncConfigCreateSerializer(serializers.ModelSerializer):
    related_app_id = serializers.UUIDField(error_messages={
        'required': _('Application mapping is required')
    })
    dimension_id = serializers.UUIDField(error_messages={
        'required': _('Dimension mapping is required')
    })

    class Meta:
        model = DimensionSyncConfig
        fields = (
            'related_app_id',
            'dimension_id',
            'sync_on_create',
            'sync_on_update',
            'sync_on_delete'
        )

    @classmethod
    def get_dimension_id(cls, value):
        if value:
            try:
                if DimensionSyncConfig.objects.filter_on_company(dimension_id=value).exists():
                    raise serializers.ValidationError({'dimension': _('Dimension is already used for mapping')})
                return Dimension.objects.get(id=value).id
            except Dimension.DoesNotExist:
                raise serializers.ValidationError({'dimension': _('Dimension does not exist')})
        return value

    @classmethod
    def get_related_app_id(cls, value):
        if value:
            try:
                if DimensionSyncConfig.objects.filter_on_company(related_app_id=value).exists():
                    raise serializers.ValidationError({'related_app': _('Application is already mapped')})
                return Application.objects.get(id=value).id
            except Application.DoesNotExist:
                raise serializers.ValidationError({'related_app': _('Application does not exist')})
        return value


class DimensionSyncConfigUpdateSerializer(serializers.ModelSerializer):
    ...


class DimensionSyncConfigDetailSerializer(serializers.ModelSerializer):
    related_app = SerializerMethodField()
    dimension = SerializerMethodField()

    class Meta:
        model = DimensionSyncConfig
        fields = (
            'related_app',
            'dimension',
            'sync_on_create',
            'sync_on_update',
            'sync_on_delete'
        )

    @classmethod
    def get_dimension(cls, obj):
        return {
            'id': obj.dimension.id,
            'title': obj.dimension.title,
            'code': obj.dimension.code,
        } if obj.dimension else None

    @classmethod
    def get_related_app(cls, obj):
        return {
            'id': obj.related_app.id,
            'title': obj.related_app.title,
            'code': obj.related_app.code,
        } if obj.related_app else None


class DimensionSyncConfigApplicationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = (
            'id',
            'title',
            'code'
        )


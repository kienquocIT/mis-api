from typing import Literal

from django.db import models

from rest_framework import serializers

from .util import PermissionController

__all__ = [
    'PermissionDetailSerializer',
    'PermissionsUpdateSerializer',
]

BASTION_FROM_TYPE = Literal['opp', 'prj']  # pylint: disable=C0103


class PermissionDetailSerializer(serializers.ModelSerializer):
    cls_of_plan: models.Model = None
    cls_key_filter: str = None

    class Meta:
        fields = ()
        abstract = True

    def __init__(self, *args, **kwargs):
        old_fields = self.Meta.fields
        for key in ('permission_by_configured', 'plan_app'):
            if key not in old_fields:
                old_fields += (key,)
        setattr(self.Meta, 'fields', old_fields)
        super().__init__(*args, **kwargs)

    permissions_parsed = serializers.SerializerMethodField()
    plan_app = serializers.SerializerMethodField()

    @classmethod
    def get_permissions_parsed(cls, obj):
        if obj.permissions_parsed:
            return obj.permissions_parsed[""]
        return {}

    def kwargs_plan_app(self, obj) -> dict:
        return {self.cls_key_filter: obj}

    def get_plan_app(self, obj):
        result = []
        data_of_plan = self.cls_of_plan.objects.select_related('plan').filter(**self.kwargs_plan_app(obj))
        if data_of_plan:
            for item in data_of_plan:
                app_list = []
                if item.application and isinstance(item.application, list):
                    application_list = PermissionController.application_cls().objects.filter(
                        id__in=item.application
                    ).values(
                        'id', 'title', 'code', 'model_code', 'app_label', 'option_permission', 'option_allowed',
                        'permit_mapping',
                    )
                    if application_list:
                        for application in application_list:
                            app_list.append(
                                {
                                    'id': application['id'],
                                    'title': application['title'],
                                    'code': application['code'],
                                    'model_code': application['model_code'],
                                    'app_label': application['app_label'],
                                    'option_permission': application['option_permission'],
                                    # 'range_allow': Application.get_range_allow(application['option_permission']),
                                    'option_allowed': application['option_allowed'],
                                    'permit_mapping': application['permit_mapping'],
                                }
                            )
                result.append(
                    {
                        'id': item.plan_id,
                        'title': item.plan.title,
                        'code': item.plan.code,
                        'application': app_list
                    }
                )
        return result


class PermissionsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ()
        abstract = True

    def __init__(self, *args, **kwargs):
        old_fields = self.Meta.fields
        for key in ('permission_by_configured',):
            if key not in old_fields:
                old_fields += (key,)
        setattr(self.Meta, 'fields', old_fields)
        super().__init__(*args, **kwargs)

    permission_by_configured = serializers.JSONField(
        required=False,
        help_text=str(
            [{
                "id": "UUID or None",
                "app_id": "UUID",
                "plan_data": "UUID",
                "create": bool,
                "view": bool,
                "edit": bool,
                "delete": bool,
                "range": 'CHOICE("1", "2", "3", "4")',
            }]
        ),
    )

    def validate_permission_by_configured(self, attrs):
        return PermissionController(tenant_id=self.instance.get_tenant_id()).valid(attrs=attrs)

    @classmethod
    def force_permissions(cls, instance, validated_data):
        permissions_data = validated_data.pop('permission_by_configured', None)
        if permissions_data is not None and isinstance(permissions_data, list):
            setattr(instance, 'permission_by_configured', permissions_data)
            setattr(
                instance,
                'permissions_parsed',
                PermissionController(tenant_id=instance.get_tenant_id()).get_permission_parsed(instance=instance)
            )
        return instance, validated_data, permissions_data

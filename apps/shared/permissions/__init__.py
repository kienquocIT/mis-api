from uuid import uuid4

from django.db import models
from rest_framework import serializers

from apps.core.base.models import SubscriptionPlan, Application
from apps.shared import TypeCheck, PermissionMsg

__all__ = [
    'PermissionController',
    'PermissionDetailSerializer',
    'PermissionsUpdateSerializer',
]


class PermissionController:
    def __init__(self):
        ...

    @classmethod
    def valid(cls, attrs):  # pylint: disable=R0914,R0912
        """
        {
            "id": "UUID or None",
            "app_id": "UUID",
            "plan_data": "UUID",
            "create": bool,
            "view": bool,
            "edit": bool,
            "delete": bool,
            "range": CHOICE("1", "2", "3", "4"),
        }
        Args:
            attrs:

        Returns:
            {
                "id": "",
                "app_data": {
                    "id": "1",
                    "title": "Employee",
                    "code": "employee",
                },
                "plan_data": {
                    "id": "2",
                    "title": "HRM title",
                    "code": "hrm",
                },
                "create": true,
                "view": true,
                "edit": false,
                "delete": true,
                "range": "3",
            }
        """
        if attrs and isinstance(attrs, list):
            plan_id_arr, plan_data_by_id = [], {}
            app_id_arr, app_data_by_id = [], {}
            checked_data, result_data = [], []

            for item in attrs:
                if item and isinstance(item, dict):
                    _id = item.get('id', None)
                    app_id = item.get('app_id', None)
                    plan_id = item.get('plan_id', None)
                    allow_create = item.get('create', None)
                    allow_view = item.get('view', None)
                    allow_edit = item.get('edit', None)
                    allow_delete = item.get('delete', None)
                    allow_range = item.get('range', None)

                    if (  # pylint: disable=R0916
                            (_id or TypeCheck.check_uuid(_id)) or not _id
                    ) and app_id and TypeCheck.check_uuid(
                        app_id
                    ) and plan_id and TypeCheck.check_uuid(
                        plan_id
                    ) and isinstance(allow_create, bool) and isinstance(allow_view, bool) and isinstance(
                        allow_edit, bool
                    ) and isinstance(allow_delete, bool) and allow_range in ['1', '2', '3', '4']:
                        app_id_arr.append(app_id)
                        plan_id_arr.append(plan_id)
                        if not _id:
                            _id = uuid4()
                        checked_data.append(
                            {
                                'id': str(_id),
                                'app_id': str(app_id),
                                'plan_id': str(plan_id),
                                'create': bool(allow_create),
                                'view': bool(allow_view),
                                'edit': bool(allow_edit),
                                'delete': bool(allow_delete),
                                'range': allow_range,
                            }
                        )
                    else:
                        raise serializers.ValidationError({'permissions': PermissionMsg.PERMISSION_INCORRECT})
                else:
                    raise serializers.ValidationError({'permissions': PermissionMsg.PERMISSION_INCORRECT})

            # check plan
            plan_id_arr = list(set(plan_id_arr))
            plan_check_objs = SubscriptionPlan.objects.filter(id__in=plan_id_arr)
            if plan_check_objs.count() != len(plan_id_arr):
                raise serializers.ValidationError({'permissions': PermissionMsg.PERMISSION_INCORRECT})
            for obj in plan_check_objs:
                plan_data_by_id[str(obj.id)] = {
                    'id': str(obj.id),
                    'title': str(obj.title),
                    'code': str(obj.code).lower(),
                }

            # check app
            app_id_arr = list(set(app_id_arr))
            app_check_objs = Application.objects.filter(id__in=app_id_arr)
            if app_check_objs.count() == len(app_id_arr):
                for obj in app_check_objs:
                    app_data_by_id[str(obj.id)] = {
                        'id': str(obj.id),
                        'title': str(obj.title),
                        'code': str(obj.code).lower(),
                        'model_code': str(obj.model_code).lower(),
                        'app_label': str(obj.app_label).lower(),
                        'option_permission': obj.option_permission,
                    }
            else:
                raise serializers.ValidationError({'permissions': PermissionMsg.PERMISSION_INCORRECT})

            for item in checked_data:
                if app_data_by_id[item['app_id']]['option_permission'] == 0:
                    if item['range'] not in ['1', '2', '3', '4']:
                        raise serializers.ValidationError({'permissions': PermissionMsg.PERMISSION_INCORRECT})
                elif app_data_by_id[item['app_id']]['option_permission'] == 1:
                    if item['range'] not in ['4']:
                        raise serializers.ValidationError({'permissions': PermissionMsg.PERMISSION_INCORRECT})

                result_data.append(
                    {
                        **item,
                        'app_data': app_data_by_id[item['app_id']],
                        'plan_data': plan_data_by_id[item['plan_id']],
                    }
                )

            return result_data
        return []

    @classmethod
    def convert_permission_all_to_simple(cls, permissions_all: list[dict[str, any]]):  # pylint: disable=R0912
        result = {}
        for item in permissions_all:
            app_label = item['app_data']['app_label']
            model_code = item['app_data']['model_code']
            allow_range = item['range']

            prefix_key = f'{app_label}.{model_code}'

            is_create = item['create']
            if is_create is True:
                result[f'{prefix_key}.create'] = {allow_range: {}}

            is_view = item['view']
            if is_view is True:
                result[f'{prefix_key}.view'] = {allow_range: {}}

            is_edit = item['edit']
            if is_edit is True:
                result[f'{prefix_key}.edit'] = {allow_range: {}}

            is_delete = item['delete']
            if is_delete is True:
                result[f'{prefix_key}.delete'] = {allow_range: {}}

        return result


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

    def get_plan_app(self, obj):
        result = []
        data_of_plan = self.cls_of_plan.objects.select_related('plan').filter(**{self.cls_key_filter: obj})
        if data_of_plan:
            for item in data_of_plan:
                app_list = []
                if item.application and isinstance(item.application, list):
                    application_list = Application.objects.filter(
                        id__in=item.application
                    ).values('id', 'title', 'code', 'model_code', 'app_label', 'option_permission')
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
                                    'range_allow': Application.get_range_allow(application['option_permission']),
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

    @classmethod
    def validate_permission_by_configured(cls, attrs):
        return PermissionController.valid(attrs)

    @classmethod
    def force_permissions(cls, instance, validated_data):
        permissions_data = validated_data.pop('permission_by_configured', None)
        if permissions_data is not None and isinstance(permissions_data, list):
            permissions_simple = PermissionController.convert_permission_all_to_simple(
                permissions_all=permissions_data,
            )
            setattr(instance, 'permission_by_configured', permissions_data)
            setattr(instance, 'permissions_parsed', permissions_simple)
        return instance, validated_data, permissions_data

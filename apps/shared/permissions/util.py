from uuid import uuid4

from typing import Literal

from django.apps import apps

from rest_framework import serializers

from ..extends.utils import TypeCheck
from ..translations.base import PermissionMsg

__all__ = [
    'PermissionController',
]

BASTION_FROM_TYPE = Literal['opp', 'prj']  # pylint: disable=C0103

PERMIT_FROM_TYPE = Literal['general', 'ids', 'opp', 'prj']  # pylint: disable=C0103


class PermissionController:
    ALLOWED_RANGE_DEFAULT = ['1', '2', '3', '4']

    @staticmethod
    def application_cls():
        return apps.get_model(app_label='base', model_name='Application'.lower())

    @staticmethod
    def tenant_plan_cls():
        return apps.get_model(app_label='tenant', model_name='TenantPlan'.lower())

    def __init__(self, tenant_id: uuid4):
        self.tenant_id: uuid4 = tenant_id

    @staticmethod
    def _valid_allow_option(item, app_data_by_id, bastion_from: BASTION_FROM_TYPE = None):  # pylint: disable=R0914
        app_id = item['app_id']
        with_range = str(item['range']) if item['range'] is not None else None

        def __check_allow(config):
            if with_range is not None and isinstance(with_range, str):
                if '*' in config:
                    return True
                if with_range in config:
                    return True
            raise serializers.ValidationError({'permissions': PermissionMsg.PERMISSION_INCORRECT})

        [is_view, is_create, is_edit, is_delete] = [
            item['view'],
            item['create'],
            item['edit'],
            item['delete'],
        ]
        app_config = app_data_by_id[app_id].get('permit_mapping', {})

        if is_view is True:
            permit_view = app_config.get('view', {})
            if bastion_from:
                bastion_from_data = permit_view.get(bastion_from, {})
                permit_view.update(
                    {
                        **(bastion_from_data if isinstance(bastion_from_data, dict) else {})
                    }
                )

            permit_view_range = permit_view.get('range', [])
            __check_allow(permit_view_range)

        if is_create is True:
            permit_create = app_config.get('create', {})
            if bastion_from:
                bastion_from_data = permit_create.get(bastion_from, {})
                permit_create.update(
                    {
                        **(bastion_from_data if isinstance(bastion_from_data, dict) else {})
                    }
                )

            permit_create_range = permit_create.get('range', [])
            __check_allow(permit_create_range)

        if is_edit is True:
            permit_edit = app_config.get('edit', {})
            if bastion_from:
                bastion_from_data = permit_edit.get(bastion_from, {})
                permit_edit.update(
                    {
                        **(bastion_from_data if isinstance(bastion_from_data, dict) else {})
                    }
                )

            permit_edit_range = permit_edit.get('range', [])
            __check_allow(permit_edit_range)

        if is_delete is True:
            permit_delete = app_config.get('delete', {})
            if bastion_from:
                bastion_from_data = permit_delete.get(bastion_from, {})
                permit_delete.update(
                    {
                        **(bastion_from_data if isinstance(bastion_from_data, dict) else {})
                    }
                )

            permit_delete_range = permit_delete.get('range', [])
            __check_allow(permit_delete_range)

        return True

    @staticmethod
    def _main_valid_sub(item, sub_item_arr, app_data_by_id):
        app_id = item['app_id']
        app_depend_on = app_data_by_id[app_id].get('app_depend_on', [])
        for sub_data in sub_item_arr:
            sub_app_id = sub_data['app_id']
            if app_id != sub_app_id and str(sub_app_id) not in app_depend_on:
                raise serializers.ValidationError({'permissions': PermissionMsg.PERMISSION_INCORRECT})

        return True

    def valid_config(
            self, config_data, plan_id_arr: list = None, app_id_arr: list = None, checked_data: list = None
    ):  # pylint: disable=R0914
        if not config_data:
            config_data = []

        if not plan_id_arr:
            plan_id_arr = []
        if not app_id_arr:
            app_id_arr = []
        if not checked_data:
            checked_data = []

        for item in config_data:
            if item and isinstance(item, dict):
                _id = item.get('id', None)
                app_id = item.get('app_id', None)
                plan_id = item.get('plan_id', None)
                allow_create = item.get('create', None)
                allow_view = item.get('view', None)
                allow_edit = item.get('edit', None)
                allow_delete = item.get('delete', None)
                allow_range = item.get('range', None)
                sub = item.get('sub', None)

                if (
                        (  # pylint: disable=R0916
                                (
                                        _id or TypeCheck.check_uuid(_id)
                                ) or not _id
                        ) and app_id and TypeCheck.check_uuid(app_id) and
                        plan_id and TypeCheck.check_uuid(plan_id) and
                        isinstance(allow_create, bool) and
                        isinstance(allow_view, bool) and
                        isinstance(allow_edit, bool) and
                        isinstance(allow_delete, bool) and
                        allow_range in self.ALLOWED_RANGE_DEFAULT
                ):
                    if not _id:
                        _id = uuid4()

                    (sub_plan_id_arr, sub_app_id_arr, sub_checked_data) = self.valid_config(sub)
                    app_id_arr += sub_app_id_arr + [app_id]
                    plan_id_arr += sub_plan_id_arr + [plan_id]

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
                            'sub': sub_checked_data,
                        }
                    )
                else:
                    raise serializers.ValidationError({'permissions': PermissionMsg.PERMISSION_INCORRECT})
            else:
                raise serializers.ValidationError({'permissions': PermissionMsg.PERMISSION_INCORRECT})
        return plan_id_arr, app_id_arr, checked_data

    def valid(self, attrs, bastion_from: BASTION_FROM_TYPE = None):  # pylint: disable=R0914,R0912
        """
        {
            "id": "UUID or None",
            "app_id": "UUID",
            "plan_id": "UUID",
            "create": bool,
            "view": bool,
            "edit": bool,
            "delete": bool,
            "range": CHOICE("1", "2", "3", "4"),
        }
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
            plan_id_arr, app_id_arr, checked_data = self.valid_config(config_data=attrs)

            # check plan
            plan_id_arr = list(set(plan_id_arr))
            t_p_objs = self.tenant_plan_cls().objects.select_related('plan').filter(
                plan_id__in=plan_id_arr, tenant_id=self.tenant_id, is_expired=False
            )
            plan_check_objs = [obj.plan for obj in t_p_objs]
            if len(plan_check_objs) != len(plan_id_arr):
                raise serializers.ValidationError({'permissions': PermissionMsg.SOME_PLAN_WAS_EXPIRED_OR_NOT_FOUND})
            plan_data_by_id = {
                str(obj.id): {
                    'id': str(obj.id),
                    'title': str(obj.title),
                    'code': str(obj.code).lower(),
                }
                for obj in plan_check_objs
            }

            # check app
            app_id_arr = list(set(app_id_arr))
            app_check_objs = self.application_cls().objects.filter(id__in=app_id_arr)
            if app_check_objs.count() != len(app_id_arr):
                raise serializers.ValidationError({'permissions': PermissionMsg.PERMISSION_INCORRECT})
            app_data_by_id = {
                str(obj.id): {
                    'id': str(obj.id),
                    'title': str(obj.title),
                    'code': str(obj.code).lower(),
                    'model_code': str(obj.model_code).lower(),
                    'app_label': str(obj.app_label).lower(),
                    'option_permission': obj.option_permission,
                    'permit_mapping': obj.permit_mapping,
                    'app_depend_on': obj.app_depend_on,
                }
                for obj in app_check_objs
            }

            result_data = []
            for item in checked_data:
                self._valid_allow_option(item=item, app_data_by_id=app_data_by_id, bastion_from=bastion_from)
                self._main_valid_sub(item=item, sub_item_arr=item['sub'], app_data_by_id=app_data_by_id)

                sub_result = []
                for sub_item in item['sub']:
                    self._valid_allow_option(item=sub_item, app_data_by_id=app_data_by_id, bastion_from=bastion_from)

                    sub_result.append(
                        {
                            **sub_item,
                            'app_data': app_data_by_id[sub_item['app_id']],
                            'plan_data': plan_data_by_id[sub_item['plan_id']],
                        }
                    )

                result_data.append(
                    {
                        **item,
                        'app_data': app_data_by_id[item['app_id']],
                        'plan_data': plan_data_by_id[item['plan_id']],
                        'sub': sub_result,
                    }
                )

            return result_data
        return []

    @classmethod
    def push_range_to_key(
            cls,
            result, key, allow_range_or_id,
            config_by_id=None, data_of_range=None, permit_from: PERMIT_FROM_TYPE = None,
    ):
        """
        Support update range config to storage with any permit_from
        OVERRIDE ALLOW RANGE DATA IF ALLOW RANGE IS EXIST!
        Args:
            result:
            key:
            allow_range_or_id:
            config_by_id:
            data_of_range:
            permit_from:

        Returns:

        """

        if not data_of_range:
            data_of_range = {}

        if key not in result:
            result[key] = {}

        data_getter = result[key]
        if permit_from is not None:
            if permit_from not in result[key]:
                result[key][permit_from] = {}
            data_getter = result[key][permit_from]

            # get special for ids of opp, project (None is skip)
            # variable data_getter related to physical location of result, not has value of result
            if config_by_id:
                if config_by_id not in result[key][permit_from]:
                    result[key][permit_from][config_by_id] = {}
                data_getter = result[key][permit_from][config_by_id]
            elif permit_from in ['opp', 'prj']:
                raise ValueError(
                    '[PermissionController][push_range_to_key] Opp and Prj are required field config_by_id'
                )

        # push range allow config to storage permit
        if allow_range_or_id not in data_getter:
            data_getter[allow_range_or_id] = data_of_range
        else:
            for key_2, value_2 in data_of_range.items():
                data_getter[allow_range_or_id][key_2] = value_2

        return result

    def parse_from_config_to_simple(self, permit_config_arr: list[dict[str, any]], result=None):
        """
        Support parse from config data (send by UI) to simple before was forced save to storage
        Args:
            permit_config_arr:
            result:

        Returns:
            {'hr.employee.view': { 'range': {} }
        """
        if not result:
            result = {}

        data_converted = self.valid(attrs=permit_config_arr)
        for item in data_converted:
            app_label = item['app_data']['app_label']
            model_code = item['app_data']['model_code']
            allow_range = item['range']

            prefix_key = f'{app_label}.{model_code}'

            is_create = item['create']
            if is_create is True:
                key = f'{prefix_key}.create'
                self.push_range_to_key(result, key, allow_range)

            is_view = item['view']
            if is_view is True:
                key = f'{prefix_key}.view'
                self.push_range_to_key(result, key, allow_range)

            is_edit = item['edit']
            if is_edit is True:
                key = f'{prefix_key}.edit'
                self.push_range_to_key(result, key, allow_range)

            is_delete = item['delete']
            if is_delete is True:
                key = f'{prefix_key}.delete'
                self.push_range_to_key(result, key, allow_range)

            item_sub = item.get('sub', [])
            result = {
                **result,
                **(
                    self.parse_from_config_to_simple(permit_config_arr=item_sub, result=result)
                    if len(item_sub) > 0 else {}
                )
            }

        return result

    def push_general(self, result, data):
        """
        Push data general to storage
        """
        if isinstance(data, list):
            permit_configured_parsed = self.parse_from_config_to_simple(
                permit_config_arr=data,
                result=result
            )
            for key_permit, value_permit in permit_configured_parsed.items():
                for allow_range, range_data in value_permit.items():
                    self.push_range_to_key(
                        result=result,
                        key=key_permit,
                        allow_range_or_id=allow_range, data_of_range=range_data,
                        permit_from='general',
                    )
        return result

    @classmethod
    def push_ids(cls, result, data):
        """
        Push data IDS to storage
        """
        if isinstance(data, dict):
            for key_perm, value_perm in data.items():
                # key_perm:     'hr.employee.view'
                # value_perm:   ['id', 'id', 'id']
                if isinstance(value_perm, list):
                    for doc_id in value_perm:
                        cls.push_range_to_key(
                            result=result,
                            key=key_perm,
                            allow_range_or_id=doc_id, data_of_range={},
                            permit_from='ids'
                        )
        return result

    @classmethod
    def push_opp(cls, result, data):
        """
        Push data OPP to storage
        """
        if isinstance(data, dict):
            for opp_id, config_perm in data.items():
                # opp_id:       Opportunity ID is UUID4
                # config_perm:  'hr.employee.view': { 'me': {}, 'all': {} }
                for key_permit, value_permit in config_perm.items():
                    for allow_range, range_data in value_permit.items():
                        cls.push_range_to_key(
                            result=result,
                            key=key_permit,
                            config_by_id=opp_id,
                            allow_range_or_id=allow_range,
                            data_of_range=range_data,
                            permit_from='opp',
                        )
        return result

    @classmethod
    def push_prj(cls, result, data):
        """
        Push Project data to storage
        """
        if isinstance(data, dict):
            for prj_id, config_perm in data.items():
                # prj_id:       Project ID is UUID4
                # config_perma: 'hr.employee.view': { 'me': {}, 'all': {} }
                for key_permit, value_permit in config_perm.items():
                    for allow_range, range_data in value_permit.items():
                        cls.push_range_to_key(
                            result=result,
                            key=key_permit,
                            config_by_id=prj_id,
                            allow_range_or_id=allow_range,
                            data_of_range=range_data,
                            permit_from='prj',
                        )
        return result

    def get_permission_parsed(self, instance):  # pylint: disable=R0912
        result = {}
        if instance and hasattr(instance, 'id'):
            #
            # parse for general
            #
            self.push_general(result=result, data=instance.permission_by_configured)

            #
            # parse for by ID
            #
            self.push_ids(result=result, data=instance.permission_by_id)

            #
            # parse for opp
            #
            self.push_opp(result=result, data=instance.permission_by_opp)

            #
            # parse for prj
            #
            self.push_prj(result=result, data=instance.permission_by_project)

        return result

from uuid import uuid4

from typing import Literal, Union

from django.apps import apps
from django.conf import settings

from rest_framework import serializers

from ..extends.utils import TypeCheck
from ..translations.base import PermissionMsg
from ..extends.models import DisperseModel

__all__ = [
    'PermissionController',
    'PermissionParsedTool',
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

    def plan_check_and_get(self, plan_id_arr: list):
        plan_id_arr = list(set(plan_id_arr))
        plan_check_objs = [
            obj.plan for obj in self.tenant_plan_cls().objects.select_related('plan').filter(
                plan_id__in=plan_id_arr, tenant_id=self.tenant_id, is_expired=False
            )
        ]
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
        return plan_data_by_id

    def app_check_and_get(self, app_id_arr: list, call_ext_app_depend=True):
        app_id_arr = list(set(app_id_arr))
        app_check_objs = self.application_cls().objects.filter(id__in=app_id_arr)
        if app_check_objs.count() != len(app_id_arr):
            raise serializers.ValidationError({'permissions': PermissionMsg.PERMISSION_INCORRECT})

        ext_app_depend = []
        app_data_by_id = {}
        for obj in app_check_objs:
            if call_ext_app_depend is True and obj.app_depend_on and isinstance(obj.app_depend_on, dict):
                ext_app_depend += list(obj.app_depend_on.keys())
            app_data_by_id[str(obj.id)] = {
                'id': str(obj.id),
                'title': str(obj.title),
                'code': str(obj.code).lower(),
                'model_code': str(obj.model_code).lower(),
                'app_label': str(obj.app_label).lower(),
                'option_permission': obj.option_permission,
                'permit_mapping': obj.permit_mapping,
                'app_depend_on': obj.app_depend_on,
            }
        return {
            **app_data_by_id,
            **(
                self.app_check_and_get(app_id_arr=ext_app_depend, call_ext_app_depend=False)
                if call_ext_app_depend is True else {}
            ),
        }

    def valid_config(self, config_data):  # pylint: disable=R0914
        app_id_arr = []
        checked_data = []
        if not config_data:
            config_data = []

        for item in config_data:
            if item and isinstance(item, dict):
                _id = item.get('id', None)
                app_id = item.get('app_id', None)
                allow_create = item.get('create', None)
                allow_view = item.get('view', None)
                allow_edit = item.get('edit', None)
                allow_delete = item.get('delete', None)
                allow_range = item.get('range', None)

                _id_check = (_id or TypeCheck.check_uuid(_id)) or not _id
                _app_check = app_id and TypeCheck.check_uuid(app_id)
                _state_allow_check = (
                        isinstance(allow_create, bool)
                        and isinstance(allow_view, bool)
                        and isinstance(allow_edit, bool)
                        and isinstance(allow_delete, bool)
                )
                _range_allow_check = allow_range in self.ALLOWED_RANGE_DEFAULT
                if _id_check and _app_check and _state_allow_check and _range_allow_check:
                    app_id_arr.append(str(app_id))
                    checked_data.append(
                        {
                            'id': str(_id if _id else uuid4()),
                            'app_id': str(app_id),
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

        app_data_by_id = self.app_check_and_get(app_id_arr=app_id_arr)
        return app_data_by_id, checked_data

    def valid(self, attrs, bastion_from: BASTION_FROM_TYPE = None):  # pylint: disable=R0914,R0912
        """
        {
            "id": "UUID or None",
            "app_id": "UUID",
            "create": bool,
            "view": bool,
            "edit": bool,
            "delete": bool,
            "range": CHOICE("1", "2", "3", "4"),
        }
        Returns:
            {
                "id": "",
                "app_id": "UUID",
                "create": true,
                "view": true,
                "edit": false,
                "delete": true,
                "range": "3",
            }
        """
        if attrs and isinstance(attrs, list):
            app_data_by_id, checked_data = self.valid_config(config_data=attrs)
            result_data = []
            for item in checked_data:
                self._valid_allow_option(item=item, app_data_by_id=app_data_by_id, bastion_from=bastion_from)
                result_data.append(
                    {
                        **item,
                    }
                )
            return result_data
        return []

    @classmethod
    def get_permission_parsed(cls, instance):  # pylint: disable=R0912
        return PermissionParsedTool().get_permission_parsed(instance)


class PermissionParsedTool:
    def __init__(self, **kwargs):
        self.app_list_by_id = kwargs.get('app_list_by_id', self.get_all_application_by_id())
        self.app_prefix_by_id = kwargs.get(
            'app_prefix_by_id', self.get_app_prefix_by_id(app_list_by_id=self.app_list_by_id)
        )
        self.app_ids_allowed = []  # app ids for method parse_to_simple check app is allowed
        self.app_prefix_allowed = []  # app prefix for method parse_to_simple check app is allowed

    @classmethod
    def get_all_application_by_id(cls):
        from apps.core.base.models import Application

        return {  # caching for db, timeout: default * 10
            str(item.id): item
            for item in Application.objects.filter().cache(timeout=settings.CACHE_EXPIRES_DEFAULT * 10)
        }

    @classmethod
    def get_app_prefix_by_id(cls, app_list_by_id):
        return {
            str(idx): obj.get_prefix_permit() for idx, obj in app_list_by_id.items()
        }

    @classmethod
    def push_range_to_key(cls, result, key, allow_range_or_id, **kwargs):
        """
            Support update range config to storage with any permit_from
            OVERRIDE ALLOW RANGE DATA IF ALLOW RANGE IS EXIST!
        """

        config_by_id = kwargs.get('config_by_id', None)

        data_of_range = kwargs.get('data_of_range', {})
        if not data_of_range:
            data_of_range = {}

        permit_from: PERMIT_FROM_TYPE = kwargs.get('permit_from', None)

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

    def push_general(self, result, data):
        """
        Push data general to storage
        """
        if isinstance(data, list):
            permit_configured_parsed, permit_general = self.parse_to_simple(data=data)

            for key_permit, value_permit in permit_configured_parsed.items():
                for allow_range, range_data in value_permit.items():
                    self.push_range_to_key(
                        result=result, key=key_permit,
                        allow_range_or_id=allow_range, data_of_range=range_data, permit_from='general',
                    )

            for key_permit, value_permit in permit_general.items():
                for allow_range, range_data in value_permit.items():
                    self.push_range_to_key(
                        result=result, key=key_permit,
                        allow_range_or_id=allow_range, data_of_range=range_data, permit_from='general',
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

    def push_opp(self, result, data):
        """
        Push data OPP to storage
        """
        if isinstance(data, dict):
            for opp_id, config_perm in data.items():
                # opp_id:       Opportunity ID is UUID4
                # config_perm:  ... same general!

                skip_with_prefix = 'opportunity.opportunity'
                permit_configured_parsed, permit_general = self.parse_to_simple(data=config_perm)

                for key_permit, value_permit in permit_configured_parsed.items():
                    if key_permit.startswith(skip_with_prefix):
                        if settings.DEBUG_PERMIT:
                            print('=> skip opp in push opp    :', key_permit, value_permit)

                    for allow_range, range_data in value_permit.items():
                        self.push_range_to_key(
                            result=result, key=key_permit, config_by_id=opp_id,
                            allow_range_or_id=allow_range, data_of_range=range_data, permit_from='opp',
                        )

                for key_permit, value_permit in permit_general.items():
                    if key_permit.startswith(skip_with_prefix):
                        if settings.DEBUG_PERMIT:
                            print('=> skip opp in push opp    :', key_permit, value_permit)

                    for allow_range, range_data in value_permit.items():
                        self.push_range_to_key(
                            result=result, key=key_permit,
                            allow_range_or_id=allow_range, data_of_range=range_data, permit_from='general',
                        )
        return result

    def push_prj(self, result, data):
        """
        Push Project data to storage
        """
        if isinstance(data, dict):
            for prj_id, config_perm in data.items():
                # prj_id:       Project ID is UUID4
                # config_perma: ...same general

                skip_with_prefix = 'project.project'
                permit_configured_parsed, permit_general = self.parse_to_simple(data=config_perm)

                for key_permit, value_permit in permit_configured_parsed.items():
                    if key_permit.startswith(skip_with_prefix):
                        if settings.DEBUG_PERMIT:
                            print('=> skip opp in push opp    :', key_permit, value_permit)

                    for allow_range, range_data in value_permit.items():
                        self.push_range_to_key(
                            result=result, key=key_permit, config_by_id=prj_id,
                            allow_range_or_id=allow_range, data_of_range=range_data, permit_from='prj',
                        )

                for key_permit, value_permit in permit_general.items():
                    if key_permit.startswith(skip_with_prefix):
                        if settings.DEBUG_PERMIT:
                            print('=> skip opp in push opp    :', key_permit, value_permit)

                    for allow_range, range_data in value_permit.items():
                        self.push_range_to_key(
                            result=result, key=key_permit,
                            allow_range_or_id=allow_range, data_of_range=range_data, permit_from='general',
                        )

        return result

    @classmethod
    def push_update_range(cls, result, code_full, range_allowed, main_range=None):
        code_full = code_full.lower()
        range_got = cls.confirm_range(range_check=range_allowed, main_range=main_range if main_range else range_allowed)
        if code_full in result:
            result[code_full].update({range_got: {}})
        else:
            result[code_full] = {range_got: {}}

    @classmethod
    def confirm_range(cls, range_check, main_range):
        if range_check == '==':
            return main_range
        return range_check

    @classmethod
    def parse_item(cls, item_data, app_obj) -> Union[None, dict[str, bool]]:
        has_allow_view = bool(item_data.get('view', False))
        has_allow_create = bool(item_data.get('create', False))
        has_allow_edit = bool(item_data.get('edit', False))
        has_allow_delete = bool(item_data.get('delete', False))
        has_allow_range = item_data.get('range', None)

        config_range_allowed = app_obj.permit_mapping
        if not (
                (
                        has_allow_view is True
                        and 'view' in config_range_allowed
                        and 'range' in config_range_allowed['view']
                        and has_allow_range in config_range_allowed['view']['range']
                )
                or (
                        has_allow_create is True
                        and 'create' in config_range_allowed
                        and 'range' in config_range_allowed['create']
                        and has_allow_range in config_range_allowed['create']['range']
                )
                or (
                        has_allow_edit is True
                        and 'edit' in config_range_allowed
                        and 'range' in config_range_allowed['edit']
                        and has_allow_range in config_range_allowed['edit']['range']
                )
                or (
                        has_allow_delete
                        and 'delete' in config_range_allowed
                        and 'range' in config_range_allowed['delete']
                        and has_allow_range in config_range_allowed['delete']['range']
                )
        ):
            return None

        return {
            'view': has_allow_view,
            'create': has_allow_create,
            'edit': has_allow_edit,
            'delete': has_allow_delete,
            'range': has_allow_range,
        }

    @classmethod
    def app_allow_from_instance(cls, instance) -> tuple[list[str], list[str]]:
        distribution_app_cls_code = getattr(instance, 'distribution_app_cls_code', None)
        get_app_allowed = getattr(instance, 'get_app_allowed', None)
        if callable(get_app_allowed) and distribution_app_cls_code:
            app_ids_or_employee_id = get_app_allowed()
            if isinstance(app_ids_or_employee_id, tuple) and len(app_ids_or_employee_id) == 2:
                return app_ids_or_employee_id
            elif isinstance(app_ids_or_employee_id, str) and TypeCheck.check_uuid(app_ids_or_employee_id):
                app_ids, app_prefix = [], []
                dis_app_cls = DisperseModel(app_model=instance.distribution_app_cls_code).get_model()
                for obj in dis_app_cls.objects.select_related('app').filter(employee_id=app_ids_or_employee_id):
                    app_ids.append(str(obj.app_id))
                    app_prefix.append(str(obj.app.get_prefix_permit()))
                return app_ids, app_prefix
        return [], []

    def parse_to_simple(self, data) -> tuple[dict, dict]:
        """
        Parse config permit to simple for push to field permission_parsed in DB
        Args:
            result: [push from calling]
            data: [{
              "id":"a482a93f-9665-45d4-b147-9da41245f82e",
              "view":true,  "create": true, "edit":true, "delete": true, "range":"1",
              "app_id":"4e48c863-861b-475a-aa5e-97a4ed26f294",
              "plan_id":"4e082324-45e2-4c27-a5aa-e16a758d5627"
            }]

        Returns:
            {"q.q.view": {"range": {}}
        """
        result = {}
        result_general = {}
        if isinstance(data, list):
            for item in data:
                if 'app_id' in item and TypeCheck.check_uuid(item['app_id']) and item['app_id'] in self.app_list_by_id:
                    app_obj = self.app_list_by_id[item['app_id']]
                    app_prefix = app_obj.get_prefix_permit()
                    if item['app_id'] not in self.app_ids_allowed:
                        if settings.DEBUG_PERMIT:
                            print('=> parsed to simple skip   :', app_prefix, item['app_id'], item)
                    else:
                        parse_item = self.parse_item(item_data=item, app_obj=app_obj)
                        if parse_item is None:
                            # skip permit parsed is failure!
                            if settings.DEBUG_PERMIT:
                                print('=> Skip parse to simple of :', item)
                            continue

                        for key_check in ['view', 'create', 'edit', 'delete']:
                            if parse_item[key_check] is True:
                                # append main app
                                self.push_update_range(
                                    result=result,
                                    code_full=f"{app_prefix}.{key_check}".lower(),
                                    range_allowed=parse_item['range'],
                                )

                                # append depend local
                                local_depends_on = app_obj.permit_mapping[key_check].get('local_depends_on', {})
                                for permit_code, permit_range in local_depends_on.items():
                                    self.push_update_range(
                                        result=result,
                                        code_full=f"{app_prefix}.{permit_code}",
                                        range_allowed=permit_range, main_range=parse_item['range'],
                                    )

                                # append depend app
                                app_depends_on = app_obj.permit_mapping[key_check].get('app_depends_on', {})
                                for depend_app_id, depend_on_data in app_depends_on.items():
                                    depend_app_obj = self.app_list_by_id.get(depend_app_id, None)
                                    if depend_app_obj:
                                        depend_app_prefix = depend_app_obj.get_prefix_permit()
                                        for permit_code, permit_range in depend_on_data.items():
                                            # is_main
                                            #   True: push permit to APP_ID group
                                            #   False: push permit to general group
                                            is_main = depend_app_obj.depend_follow_main
                                            self.push_update_range(
                                                result=result if is_main is True else result_general,
                                                code_full=f"{depend_app_prefix}.{permit_code}",
                                                range_allowed=permit_range, main_range=parse_item['range'],
                                            )
        return result, result_general

    def get_permission_parsed(self, instance):  # pylint: disable=R0912
        result = {}
        if instance and hasattr(instance, 'id'):
            self.app_ids_allowed, self.app_prefix_allowed = self.app_allow_from_instance(instance=instance)
            if not isinstance(self.app_ids_allowed, list) or not isinstance(self.app_prefix_allowed, list):
                raise ValueError('App allowed return data type not support!')

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

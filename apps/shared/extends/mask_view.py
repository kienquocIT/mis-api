from collections.abc import Iterable
from copy import deepcopy
from functools import wraps
from typing import Union, Literal
from uuid import uuid4

import numpy as np

import rest_framework.exceptions
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.http import HttpResponse
from django.utils import translation

from rest_framework import status, serializers
from rest_framework.response import Response

from .controllers import ResponseController
from .utils import TypeCheck, ListHandler
from .models import DisperseModel
from .exceptions import Empty200, handle_exception_all_view
from ..permissions import FilterComponent, FilterComponentList
from ..translations.base import PermissionMsg

__all__ = [
    'mask_view',
    'EmployeeAttribute',
    'ViewChecking',
    'ViewAttribute',
    'ViewConfigDecorator',
]


class HttpReturn:
    @classmethod
    def error_not_found(cls):
        return ResponseController.notfound_404()

    @classmethod
    def error_employee_require(cls, error_employee_require: Union[callable, None]):
        if error_employee_require and callable(error_employee_require):
            return error_employee_require()
        return ResponseController.forbidden_403()

    @classmethod
    def error_login_require(cls, error_login_require: Union[callable, None]):
        if error_login_require and callable(error_login_require):
            return error_login_require()
        return ResponseController.unauthorized_401()

    @classmethod
    def error_auth_require(cls, request_method, has_dropdown_list, error_auth_require):
        if request_method.upper() == 'GET' and has_dropdown_list:
            return cls.success_empty_list()

        if request_method.upper() == 'GET' and error_auth_require:
            if callable(error_auth_require):
                return error_auth_require()
        return ResponseController.forbidden_403()

    @classmethod
    def error_config_view_incorrect(cls):
        return ResponseController.internal_server_error_500(
            msg=PermissionMsg.CONFIG_AUTH_VIEW_INCORRECT
        )

    @classmethod
    def success_empty_list(cls):
        return ResponseController.success_200(data=[])

    @classmethod
    def success_empty_dict(cls):
        return ResponseController.success_200(data={})

    def __init__(self):
        ...


class ViewConfigDecorator:
    _opp_enabled = False
    _prj_enabled = False
    _login_require = True  # require request.user is User Object
    _auth_require = False  # require setup filter query then add view for MIXIN
    _employee_require = False  # require request.user.employee is Employee Object
    _allow_admin_tenant = False  # allow admin tenant skip filter query
    _allow_admin_company = False  # allow admin company skip filter query
    _label_code = None  # App code need call for filter query
    _model_code = None  # Model code need call for filter query
    _perm_code = None  # Permit code need call from filter query
    _bastion_field_require = False  #
    _use_custom_get_filter_auth = False  # using function manual filter auth (overrode def get_filter_auth in view)
    _config_check_permit = {}
    _has_allow_admin = False

    @property
    def has_allow_admin(self):
        if not self._has_allow_admin:
            self._has_allow_admin = self.allow_admin_tenant or self.allow_admin_company
        return self._has_allow_admin

    @property
    def config_check_permit(self) -> dict:
        if not self._config_check_permit and self.label_code and self.model_code and self.perm_code:
            self._config_check_permit = {
                'label_code': self.label_code.lower(),
                'model_code': self.model_code.lower(),
                'perm_code': self.perm_code.lower(),
            }
        return self._config_check_permit

    def __init__(self, parent_kwargs):
        self.employee_require = parent_kwargs.get('employee_require', self._employee_require)
        self.login_require = parent_kwargs.get('login_require', self._login_require)
        self.auth_require = parent_kwargs.get('auth_require', self._auth_require)
        self.bastion_field_require = parent_kwargs.get('bastion_field_require', self._bastion_field_require)
        self.use_custom_get_filter_auth = parent_kwargs.get(
            'use_custom_get_filter_auth', self._use_custom_get_filter_auth
        )
        self.allow_admin_tenant: bool = parent_kwargs.get('allow_admin_tenant', self._allow_admin_tenant)
        self.allow_admin_company: bool = parent_kwargs.get('allow_admin_company', self._allow_admin_company)
        self.label_code: str = parent_kwargs.get('label_code', self._label_code)
        self.model_code: str = parent_kwargs.get('model_code', self._model_code)
        self.perm_code: str = parent_kwargs.get('perm_code', self._perm_code)
        self.opp_enabled: bool = parent_kwargs.get('opp_enabled', self._opp_enabled)
        self.prj_enabled: bool = parent_kwargs.get('prj_enabled', self._prj_enabled)
        self.skip_filter_employee: bool = parent_kwargs.get('skip_filter_employee', False)


class EmployeeAttribute:
    """
    Get some data of Employee Objects support for permission or another.
    """

    @property
    def model_hr_group(self):
        if not self._model_hr_group:
            self._model_hr_group = DisperseModel(app_model='hr.group').get_model()
        return self._model_hr_group

    @property
    def model_hr_employee(self):
        if not self._model_hr_employee:
            self._model_hr_employee = DisperseModel(app_model='hr.employee').get_model()
        return self._model_hr_employee

    @property
    def tenant_id(self):
        if self.employee_current and hasattr(self.employee_current, 'id'):
            self._tenant_id = self.employee_current.tenant_id
        return self._tenant_id

    @property
    def company_id(self):
        if not self._company_id and self.employee_current and hasattr(self.employee_current, 'company_id'):
            self._company_id = self.employee_current.company_id
        return self._company_id

    @property
    def group_id_of_employee_current(self) -> str:
        if not self._group_id_of_employee_current and self.employee_current and self.employee_current.group_id:
            self._group_id_of_employee_current = str(self.employee_current.group_id)
        return self._group_id_of_employee_current

    @property
    def manager_of_group_ids(self) -> list[str]:
        if not self._manager_of_group_ids and self.model_hr_group:
            self._manager_of_group_ids = [
                str(x) for x in self.model_hr_group.objects.filter(
                    Q(first_manager_id=self.employee_current_id)
                ).filter_current(fill__tenant=True, fill__company=True).values_list('id', flat=True).cache()
            ]
        return self._manager_of_group_ids

    @property
    def employee_staff_ids(self) -> list[str]:
        if (
                not self._employee_staff_ids
                and self.employee_current
                and self.manager_of_group_ids
                and len(self.manager_of_group_ids) > 0
        ):
            employee_ids = self.model_hr_employee.objects.filter(
                group_id__in=self.manager_of_group_ids,
            ).filter_current(fill__tenant=True, fill__company=True).values_list('id', flat=True).cache()
            self._employee_staff_ids = list(
                set(
                    [
                        str(x) for x in employee_ids
                    ]
                )
            )
        return self._employee_staff_ids

    def employee_staff_ids__exclude_me(self):
        employee_staff_ids = list(self.employee_staff_ids)
        if self.employee_current_id and str(self.employee_current_id) in employee_staff_ids:
            employee_staff_ids.remove(str(self.employee_current_id))
        return employee_staff_ids

    def employee_staff_ids__append_me(self):
        employee_staff_ids = list(self.employee_staff_ids)
        if self.employee_current_id and str(self.employee_current_id) not in employee_staff_ids:
            employee_staff_ids.append(
                str(self.employee_current_id)
            )
        return employee_staff_ids

    @property
    def employee_same_group_ids(self) -> list[str]:
        if not self._employee_same_group_ids and self.group_id_of_employee_current:
            employee_ids = self.model_hr_employee.objects.filter(
                group_id=self.group_id_of_employee_current
            ).filter_current(fill__tenant=True, fill__company=True).values_list('id', flat=True).cache()
            self._employee_same_group_ids = list(
                set(
                    [
                        str(x) for x in employee_ids
                    ]
                )
            )
        return self._employee_same_group_ids

    def employee_same_group_ids__exclude_me(self):
        employee_same_group_ids = list(self.employee_same_group_ids)
        if employee_same_group_ids and isinstance(employee_same_group_ids, list):
            if self.employee_current_id and str(self.employee_current_id) in employee_same_group_ids:
                employee_same_group_ids.remove(str(self.employee_current_id))
            return employee_same_group_ids
        return []

    def employee_same_group_ids__append_me(self):
        employee_same_group_ids = list(self.employee_same_group_ids)
        if self.employee_current_id and str(self.employee_current_id) not in employee_same_group_ids:
            employee_same_group_ids.append(
                str(self.employee_current_id)
            )
        return employee_same_group_ids

    @property
    def roles(self):
        if self._roles is None and self.employee_current and hasattr(self.employee_current, 'role'):
            self._roles = [
                {
                    'id': obj.id,
                    'title': obj.title,
                    'permissions_parsed': obj.permissions_parsed if obj.permissions_parsed else {},
                }
                for obj in self.employee_current.role.all().cache()
            ]
        return self._roles

    def __init__(self, employee_obj, **kwargs):
        self._model_hr_group = None
        self._model_hr_employee = None
        self._tenant_id = None
        self._company_id = None
        self._group_id_of_employee_current = None
        self._manager_of_group_ids = []
        self._employee_staff_ids = []
        self._employee_same_group_ids = []
        self._employee_in_company_ids = []
        self._roles: list[dict] = None

        self.employee_current = employee_obj
        self.employee_current_id = employee_obj.id if employee_obj and hasattr(employee_obj, 'id') else None
        self.is_append_me: bool = kwargs.get('is_append_me', False)


class ViewAttribute:
    """
    Support getter of attribute request view or attribute request user:
    - Permit check config
    - User info: is admin, tenant current, company current,...
    - Set data to attribute of view for check in MIXINS
    """

    #######################################
    # Properties from User Object
    #######################################

    @property
    def user(self):
        if not self._user:
            cond_state = (
                    self.request
                    and hasattr(self.request, 'user')
                    and hasattr(self.request.user, 'id')
                    and not isinstance(self.request.user, AnonymousUser)
            )
            self._user = self.request.user if cond_state else None
        return self._user

    @property
    def employee_current_id(self):
        if not self._employee_current_id:
            if self.user and hasattr(self.user, 'employee_current_id'):
                self._employee_current_id = self.user.employee_current_id
        return self._employee_current_id

    @property
    def employee_current(self):
        if not self._employee_current:
            emp_obj_tmp = getattr(self.user, 'employee_current', None)
            if emp_obj_tmp and hasattr(emp_obj_tmp, 'id'):
                self._employee_current = emp_obj_tmp
        return self._employee_current

    @property
    def is_admin_tenant(self) -> bool:
        if not self._is_admin_tenant:
            if self.user:
                self._is_admin_tenant = self.user.is_admin_tenant
        return self._is_admin_tenant

    @property
    def is_admin_company(self) -> bool:
        if not self._is_admin_company:
            if self.user and hasattr(self.user, 'employee_current') and hasattr(self.user.employee_current, 'id'):
                self._is_admin_company = self.user.employee_current.is_admin_company
        return self._is_admin_company

    #######################################
    # Properties from Request View Object
    #######################################

    @property
    def has_dropdown_list(self):
        if not self._has_dropdown_list:
            if self.request.method == 'GET':
                self._has_dropdown_list = self.request.META.get(
                    'HTTP_DATAISDD',
                    None
                ) == 'true'
        return self._has_dropdown_list

    @property
    def has_check_perm(self):
        if not self._has_check_perm:
            if self.request.META.get('HTTP_DATAHASPERM', False) == 'true':
                self._has_check_perm = True
        return self._has_check_perm

    @property
    def view_args(self):
        if not self._view_args:
            self._view_args = self.view_this.args
        return self._view_args

    @property
    def view_kwargs(self):
        if not self._view_kwargs:
            self._view_kwargs = self.view_this.kwargs
        return self._view_kwargs

    @property
    def error_auth_require(self):
        if not self._error_auth_require and self.view_this and hasattr(self.view_this, 'error_auth_require'):
            func_call = getattr(self.view_this, 'error_auth_require')
            if callable(func_call):
                self._error_auth_require = func_call
        return self._error_auth_require

    @property
    def error_employee_require(self):
        if not self._error_auth_require and self.view_this and hasattr(self.view_this, 'error_employee_require'):
            func_call = getattr(self.view_this, 'error_employee_require')
            if callable(func_call):
                self._error_employee_require = func_call
        return self._error_employee_require

    @property
    def error_login_require(self):
        if not self._error_login_require and self.view_this and hasattr(self.view_this, 'error_login_require'):
            func_call = getattr(self.view_this, 'error_login_require')
            if callable(func_call):
                self._error_employee_require = func_call
        return self._error_employee_require

    @property
    def request_method(self):
        if self._request_method is None and self.request:
            self._request_method = self.request.method.upper()
        return self._request_method

    @property
    def list_hidden_field(self) -> list[str]:
        if self._list_hidden_field is None:
            data_tmp = getattr(self.view_this, 'list_hidden_field', [])
            self._list_hidden_field = data_tmp if data_tmp and isinstance(data_tmp, Iterable) else []
        return self._list_hidden_field

    @property
    def list_hidden_field_mapping(self) -> dict[str, any]:
        if self._list_hidden_field_mapping is None:
            data_list = getattr(self.view_this, 'list_hidden_field_mapping', None)
            self._list_hidden_field_mapping = data_list if isinstance(data_list, dict) else {}
        return self._list_hidden_field_mapping

    @property
    def list_hidden_field_manual_before(self) -> dict[str, any]:
        """
        Manual fill some value (of dict) to setup_hidden
        Override function "append_list_hidden_field_manual" with kwargs: cls_self
            - cls_self : ViewAttribute
        """
        if self._list_hidden_field_manual_before is None:
            list_hidden_field_manual = {}
            func_call = getattr(self.view_this, 'list_hidden_field_manual_before', None)
            if callable(func_call):
                list_hidden_field_manual = func_call()
            self._list_hidden_field_manual_before = list_hidden_field_manual
        return self._list_hidden_field_manual_before

    @property
    def list_hidden_field_manual_after(self) -> dict[str, any]:
        """
        Manual fill some value (of dict) to setup_hidden
        Override function "append_list_hidden_field_manual" with kwargs: cls_self
            - cls_self : ViewAttribute
        """
        if self._list_hidden_field_manual_after is None:
            list_hidden_field_manual = {}
            func_call = getattr(self.view_this, 'list_hidden_field_manual_after', None)
            if callable(func_call):
                list_hidden_field_manual = func_call()
            self._list_hidden_field_manual_after = list_hidden_field_manual
        return self._list_hidden_field_manual_after

    @property
    def create_hidden_field(self) -> list[str]:
        if self._create_hidden_field is None:
            data_tmp = getattr(self.view_this, 'create_hidden_field', [])
            self._create_hidden_field = data_tmp if data_tmp and isinstance(data_tmp, Iterable) else []
        return self._create_hidden_field

    @property
    def create_hidden_field_mapping(self) -> dict[str, any]:
        if self._create_hidden_field_mapping is None:
            data_list = getattr(self.view_this, 'create_hidden_field_mapping', None)
            self._create_hidden_field_mapping = data_list if isinstance(data_list, dict) else {}
        return self._create_hidden_field_mapping

    @property
    def create_hidden_field_manual_before(self):
        if self._create_hidden_field_manual_before is None:
            create_hidden_field_manual = {}
            func_call = getattr(self.view_this, 'create_hidden_field_manual_before', None)
            if callable(func_call):
                create_hidden_field_manual = func_call()
            self._create_hidden_field_manual_before = create_hidden_field_manual
        return self._create_hidden_field_manual_before

    @property
    def create_hidden_field_manual_after(self):
        if self._create_hidden_field_manual_after is None:
            create_hidden_field_manual = {}
            func_call = getattr(self.view_this, 'create_hidden_field_manual_after', None)
            if callable(func_call):
                create_hidden_field_manual = func_call()
            self._create_hidden_field_manual_after = create_hidden_field_manual
        return self._create_hidden_field_manual_after

    @property
    def retrieve_hidden_field(self) -> list[str]:
        if self._retrieve_hidden_field is None:
            data_tmp = getattr(self.view_this, 'retrieve_hidden_field', [])
            self._retrieve_hidden_field = data_tmp if data_tmp and isinstance(data_tmp, Iterable) else []
        return self._retrieve_hidden_field

    @property
    def retrieve_hidden_field_mapping(self) -> dict[str, any]:
        if self._retrieve_hidden_field_mapping is None:
            data_list = getattr(self.view_this, 'retrieve_hidden_field_mapping', None)
            self._retrieve_hidden_field_mapping = data_list if isinstance(data_list, dict) else {}
        return self._retrieve_hidden_field_mapping

    @property
    def retrieve_hidden_field_manual_before(self) -> dict[str, any]:
        """
        Manual fill some value (of dict) to setup_hidden
        Override function "append_retrieve_hidden_field_manual" with kwargs: cls_self
            - cls_self : ViewAttribute
        """
        if self._retrieve_hidden_field_manual_before is None:
            retrieve_hidden_field_manual = {}
            func_call = getattr(self.view_this, 'retrieve_hidden_field_manual_before', None)
            if callable(func_call):
                retrieve_hidden_field_manual = func_call()
            self._retrieve_hidden_field_manual_before = retrieve_hidden_field_manual
        return self._retrieve_hidden_field_manual_before

    @property
    def retrieve_hidden_field_manual_after(self) -> dict[str, any]:
        """
        Manual fill some value (of dict) to setup_hidden
        Override function "append_retrieve_hidden_field_manual" with kwargs: cls_self
            - cls_self : ViewAttribute
        """
        if self._retrieve_hidden_field_manual_after is None:
            retrieve_hidden_field_manual = {}
            func_call = getattr(self.view_this, 'retrieve_hidden_field_manual_after', None)
            if callable(func_call):
                retrieve_hidden_field_manual = func_call()
            self._retrieve_hidden_field_manual_after = retrieve_hidden_field_manual
        return self._retrieve_hidden_field_manual_after

    @property
    def update_hidden_field(self) -> list[str]:
        if self._update_hidden_field is None:
            data_tmp = getattr(self.view_this, 'update_hidden_field', [])
            self._update_hidden_field = data_tmp if data_tmp and isinstance(data_tmp, Iterable) else []
        return self._update_hidden_field

    @property
    def update_hidden_field_mapping(self) -> dict[str, any]:
        if self._update_hidden_field_mapping is None:
            data_list = getattr(self.view_this, 'update_hidden_field_mapping', None)
            self._update_hidden_field_mapping = data_list if isinstance(data_list, dict) else {}
        return self._update_hidden_field_mapping

    @property
    def update_hidden_field_manual_before(self) -> dict[str, any]:
        if self._update_hidden_field_manual_before is None:
            update_hidden_field_manual = {}
            func_call = getattr(self.view_this, 'update_hidden_field_manual_before', None)
            if callable(func_call):
                update_hidden_field_manual = func_call()
            self._update_hidden_field_manual_before = update_hidden_field_manual
        return self._update_hidden_field_manual_before

    @property
    def update_hidden_field_manual_after(self) -> dict[str, any]:
        if self._update_hidden_field_manual_after is None:
            update_hidden_field_manual = {}
            func_call = getattr(self.view_this, 'update_hidden_field_manual_after', None)
            if callable(func_call):
                update_hidden_field_manual = func_call()
            self._update_hidden_field_manual_after = update_hidden_field_manual
        return self._update_hidden_field_manual_after

    def __init__(self, view_this, **kwargs):
        self._user = None
        self._employee_current_id: uuid4 = None
        self._employee_current = None
        self._is_admin_tenant: bool = False
        self._is_admin_company: bool = False
        self._has_dropdown_list: bool = False
        self._has_check_perm: bool = False
        self._view_args: list = []
        self._view_kwargs: dict = {}
        self._error_auth_require: callable = None
        self._error_employee_require: callable = None
        self._error_login_require: callable = None
        self._request_method = None
        self._list_hidden_field: list[str] = None
        self._list_hidden_field_mapping: dict[str, any] = {}
        self._list_hidden_field_manual_before: dict[str, any] = None
        self._list_hidden_field_manual_after: dict[str, any] = None
        self._create_hidden_field: list[str] = None
        self._create_hidden_field_mapping: dict[str, any] = None
        self._create_hidden_field_manual_before: dict[str, any] = None
        self._create_hidden_field_manual_after: dict[str, any] = None
        self._retrieve_hidden_field: list[str] = None
        self._retrieve_hidden_field_mapping: dict[str, any] = None
        self._retrieve_hidden_field_manual_before: dict[str, any] = None
        self._retrieve_hidden_field_manual_after: dict[str, any] = None
        self._update_hidden_field: list[str] = None
        self._update_hidden_field_mapping: dict[str, any] = None
        self._update_hidden_field_manual_before: dict[str, any] = None
        self._update_hidden_field_manual_after: dict[str, any] = None

        # autofill data to attribute when init | *** Caution must be exercised, not recommend ***
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.view_this = view_this
        self.request = view_this.request

    def setup_hidden(self, from_view: Literal['list', 'create', 'retrieve', 'update']) -> dict:
        # get field list
        if from_view == 'list':
            fields = self.list_hidden_field
            field_map = self.list_hidden_field_mapping
            ctx_before = self.list_hidden_field_manual_before
            ctx_after = self.list_hidden_field_manual_after
        elif from_view == 'create':
            fields = self.create_hidden_field
            field_map = self.create_hidden_field_mapping
            ctx_before = self.create_hidden_field_manual_before
            ctx_after = self.create_hidden_field_manual_after
        elif from_view == 'retrieve':
            fields = self.retrieve_hidden_field
            field_map = self.retrieve_hidden_field_mapping
            ctx_before = self.retrieve_hidden_field_manual_before
            ctx_after = self.retrieve_hidden_field_manual_after
        elif from_view == 'update':
            fields = self.update_hidden_field
            field_map = self.update_hidden_field_mapping
            ctx_before = self.update_hidden_field_manual_before
            ctx_after = self.update_hidden_field_manual_after
        else:
            raise ValueError('View "%s" not support setup hidden! ' % (str(from_view)))

        # get request user object
        user = self.user

        # parsing...
        ctx = {}
        if isinstance(ctx_before, dict):
            ctx = ctx_before

        if fields and user and hasattr(user, 'id'):
            for key in fields:
                if key in field_map:
                    data = field_map[key]
                else:
                    match key:
                        case 'tenant_id':
                            data = str(user.tenant_current_id)
                        case 'tenant':
                            data = user.tenant_current
                        case 'company_id':
                            data = str(user.company_current_id)
                        case 'company':
                            data = user.company_current
                        case 'space_id':
                            data = str(user.space_current_id)
                        case 'space':
                            data = user.space_current
                        case 'mode_id':
                            data = getattr(user, 'mode_id', 0)
                        case 'mode':
                            data = getattr(user, 'mode', 0)
                        case 'employee_created_id':
                            data = str(user.employee_current_id)
                        case 'employee_modified_id':
                            data = str(user.employee_current_id)
                        case 'employee_id':
                            data = str(user.employee_current_id)
                        case 'user_id':
                            data = str(user.id)
                        case 'employee_inherit_id':
                            data = str(user.employee_current_id)
                        case 'is_delete':
                            data = True
                        case 'is_active':
                            data = True
                        case _:
                            data = None
                if data is not None:
                    ctx[key] = data

        if isinstance(ctx_after, dict):
            ctx.update(ctx_after)
        return ctx

    def header_language(self):
        if self.request:
            head_lang = self.request.headers.get('Accept-Language', '').lower()
            if head_lang:
                if ',' in head_lang:
                    head_lang = head_lang.split(",")[0]

                if ';' in head_lang:
                    head_lang = head_lang.split(";")

                if '-' in head_lang:
                    head_lang = head_lang.split('-')[0]

                if head_lang in settings.LANGUAGE_CHOICE_CODE:
                    return head_lang
        return settings.LANGUAGE_CODE


class PermissionController:
    @classmethod
    def compare_special_permit_with_range_allowed(cls, data_permit, employee_current_id, employee_inherit_id, **kwargs):
        """
        # check for opp or prj
        """
        compare_main_id = kwargs.get('compare_main_id', None)
        has_from = kwargs.get('has_from', None)
        if compare_main_id and TypeCheck.check_uuid(compare_main_id) and (has_from == 'opp' or has_from == 'prj'):
            if isinstance(data_permit, dict) and data_permit:
                if '4' in data_permit and '1' not in data_permit and employee_current_id == employee_inherit_id:
                    # not '1' -> not create for Themselves
                    return False

                filter_kw_for_member = {
                    'fill__tenant': True, 'fill__company': True,
                }

                if has_from == 'opp':
                    filter_kw_for_member['opportunity_id'] = compare_main_id
                    filter_kw_for_member['member_id__in'] = [employee_current_id, employee_inherit_id]

                    cls_model = DisperseModel(app_model='opportunity.OpportunitySaleTeamMember').get_model()
                    cls_objs = cls_model.objects.filter_current(**filter_kw_for_member)

                    if cls_objs.count() == len({str(employee_current_id), str(employee_inherit_id)}):
                        if '4' in data_permit and '1' in data_permit:
                            # check member success -> pass with full range by 1 + 4
                            return True
                        elif '4' in data_permit:
                            if str(employee_current_id) == str(employee_inherit_id):
                                # not allow to create for themselves
                                return False
                            # allow to create for opp members
                            return True
                        elif '1' in data_permit:
                            if str(employee_current_id) == str(employee_inherit_id):
                                # allow to create only for themselves
                                return True
                            # not allow to create for opp members
                            return False
                    # not belong to one Opp | not support another range | another case
                    return False

                elif has_from == 'prj':
                    filter_kw_for_member['project_id'] = compare_main_id
                    filter_kw_for_member['member_id__in'] = [employee_current_id, employee_inherit_id]

                    cls_model = DisperseModel(app_model='project.ProjectMapMember').get_model()
                    cls_objs = cls_model.objects.filter_current(**filter_kw_for_member)

                    if cls_objs.count() == len({str(employee_current_id), str(employee_inherit_id)}):
                        if '4' in data_permit and '1' in data_permit:
                            # check member success -> pass with full range by 1 + 4
                            return True
                        elif '4' in data_permit:
                            if str(employee_current_id) == str(employee_inherit_id):
                                # not allow to create for themselves
                                return False
                            # allow to create for prj members
                            return True
                        elif '1' in data_permit:
                            if str(employee_current_id) == str(employee_inherit_id):
                                # allow to create only for themselves
                                return True
                            # not allow to create for prj members
                            return False
                    # not belong to one Prj | not support another range | another case
                    return False

        return False

    @classmethod
    def parse_config_permit_check_to_string(cls, config_permit_check: dict):
        if (
                config_permit_check
                and isinstance(config_permit_check, dict)
                and 'label_code' in config_permit_check
                and 'model_code' in config_permit_check
                and 'perm_code' in config_permit_check
        ):
            label_code = config_permit_check['label_code']
            model_code = config_permit_check['model_code']
            perm_code = config_permit_check['perm_code']
            return f'{label_code}.{model_code}.{perm_code}'
        return ''

    @classmethod
    def config_data__get_by_config(cls, app_obj, perm_code, permissions_parsed: dict, state_depend_on: bool = None):
        # state_depend_on = None: not check is_depend_on

        default_data = {'general': {}, 'ids': {}, 'opp': {}, 'prj': {}, 'app_obj': app_obj}
        key = f'{app_obj.app_label}.{app_obj.model_code}.{perm_code}'.lower()
        if key in permissions_parsed:
            perm = permissions_parsed[key]
            if perm and isinstance(perm, dict):
                if 'general' in perm and isinstance(perm['general'], dict):
                    if state_depend_on is not None:
                        result_tmp = {}
                        for perm_code, perm_config in perm['general'].items():
                            if isinstance(perm_config, dict):
                                if perm_config.get('is_depend_on', False) == state_depend_on:
                                    result_tmp[perm_code] = perm_config
                                else:
                                    if settings.DEBUG_PERMIT:
                                        print(
                                            '* [GENERAL - depend] skip  :', 'state_depend_on =', state_depend_on,
                                            ',', 'is_depend_on =', perm_config.get('is_depend_on', False),
                                            ',', 'perm_config =', perm_config,
                                        )
                        default_data['general'] = result_tmp
                    else:
                        default_data['general'] = perm['general']

                if 'ids' in perm and isinstance(perm['ids'], dict):
                    if state_depend_on in (None, False):
                        default_data['ids'] = perm['ids']
                    else:
                        if settings.DEBUG_PERMIT:
                            print('* [IDS - depend] skip      :', 'state_depend_on =', state_depend_on)

                if 'opp' in perm and isinstance(perm['opp'], dict):
                    if state_depend_on in (None, False):
                        default_data['opp'] = perm['opp']
                    else:
                        if settings.DEBUG_PERMIT:
                            print('* [OPP - depend] skip      :', 'state_depend_on =', state_depend_on)

                if 'prj' in perm and isinstance(perm['prj'], dict):
                    if state_depend_on in (None, False):
                        default_data['prj'] = perm['prj']
                    else:
                        if settings.DEBUG_PERMIT:
                            print('* [PRJ - depend] skip      :', 'state_depend_on =', state_depend_on)

        return default_data

    KEY_STORAGE_PERMISSION_IN_MODEL = 'permissions_parsed'
    KEY_FILTER_INHERITOR_ID_IN_MODEL = 'employee_inherit_id'
    KEY_FILTER_COMPANY_ID_IN_MODEL = 'company_id'
    ALLOWED_RANGE__GENERAL = ['1', '2', '3', '4']

    KEY_FILTER_OPP_ID_IN_MODEL = 'opportunity_id'
    ALLOWED_RANGE__OPP = ['1', '4']

    KEY_FILTER_PRJ_ID_IN_MODEL = 'project_id'
    ALLOWED_RANGE___PRJ = ['1', '4']

    def get_config_data(self, config_check_permit, has_roles=True, state_depend_on=None):
        config_tmp = {'employee': {}, 'roles': []}
        # get from employee
        if config_check_permit:
            # get app obj
            label_code = config_check_permit.get('label_code', None)
            model_code = config_check_permit.get('model_code', None)
            perm_code = config_check_permit.get('perm_code', None)
            application_obj = None
            if label_code and model_code and perm_code:
                app_obj_tmp = DisperseModel(app_model='base.application').get_model().objects.filter(
                    app_label=label_code, model_code=model_code,
                ).cache(timeout=settings.CACHE_EXPIRES_DEFAULT * 10).first()
                if settings.DEBUG_PERMIT:
                    print('=> Application Object      :', app_obj_tmp, label_code, model_code, perm_code)
                if app_obj_tmp and app_obj_tmp.permit_mapping and perm_code in app_obj_tmp.permit_mapping:
                    application_obj = app_obj_tmp

            # get employee obj
            employee_obj = self.employee_attr.employee_current
            if employee_obj and application_obj:
                permissions_parsed = getattr(employee_obj, self.KEY_STORAGE_PERMISSION_IN_MODEL, {})
                if permissions_parsed:
                    config_tmp['employee'] = self.config_data__get_by_config(
                        app_obj=application_obj,
                        perm_code=perm_code,
                        permissions_parsed=permissions_parsed,
                        state_depend_on=state_depend_on,
                    )

                # get from role
                if has_roles is True:
                    for role_data in self.employee_attr.roles:
                        permissions_parsed = role_data[self.KEY_STORAGE_PERMISSION_IN_MODEL]
                        if permissions_parsed:
                            config_tmp['roles'].append(
                                self.config_data__get_by_config(
                                    app_obj=application_obj,
                                    perm_code=perm_code,
                                    permissions_parsed=permissions_parsed,
                                    state_depend_on=state_depend_on,
                                )
                            )
        return config_tmp

    @property
    def config_data(self):
        if not self._config_data:
            config_tmp = self.get_config_data(
                self.config_check_permit, state_depend_on=self.state_depend_on
            )
            code = self.parse_config_permit_check_to_string(self.config_check_permit)
            if code:
                self._config_data__by_code[code] = config_tmp
            self._config_data = config_tmp
            if settings.DEBUG_PERMIT:
                print('* _config_data             :', self._config_data)
        return self._config_data

    def config_data__by_code(self, label_code, model_code, perm_code, has_roles: bool):
        config_check_permit = {'label_code': label_code, 'model_code': model_code, 'perm_code': perm_code}
        code = self.parse_config_permit_check_to_string(config_check_permit)
        if code and code not in self._config_data__by_code:
            config_tmp = self.get_config_data(config_check_permit, has_roles=has_roles)
            self._config_data__by_code[code] = config_tmp

        if settings.DEBUG_PERMIT:
            print('* _config_data__by_code    :', code, self._config_data__by_code[code])
        return self._config_data__by_code[code]

    @property
    def config_data__exist(self) -> False:
        if not self._has_permit_exist and self.config_data:
            if self.config_data['employee']:
                # {'general': {}, 'ids': {}, 'opp': {}, 'prj': {}}
                if isinstance(self.config_data['employee'], dict) and (
                        self.config_data['employee']['general']
                        or self.config_data['employee']['ids']
                        or self.config_data['employee']['opp']
                        or self.config_data['employee']['prj']
                ):
                    self._has_permit_exist = True
            if not self._has_permit_exist and self.config_data['roles']:
                for item in self.config_data['roles']:
                    if isinstance(item, dict) and (
                            item['general']
                            or item['ids']
                            or item['opp']
                            or item['prj']
                    ):
                        self._has_permit_exist = True
                        break
        return self._has_permit_exist

    def get_config_data__simple_list(self, config_data):
        config_parse_or = []
        if config_data and isinstance(config_data, dict):
            if 'employee' in config_data:
                tmp = self.config_data__simple_list__item(item_data=config_data['employee'])
                if tmp:
                    config_parse_or += tmp

            if 'roles' in config_data:
                for role_data in config_data['roles']:
                    tmp = self.config_data__simple_list__item(item_data=role_data)
                    if tmp:
                        config_parse_or += tmp

            config_parse_or = ListHandler.distant_dict_in_list(dict_in_list=config_parse_or)

        return config_parse_or

    @property
    def config_data__simple_list(self):
        """
        Support collect data parsed from permit configured of current user
        """
        # sample = sample = {
        #     'employee': {'{config_data__simple_list__item}'},
        #     'roles': [{'{config_data__simple_list__item}'}],
        # }
        if not self._config_data__simple_list:
            self._config_data__simple_list = self.get_config_data__simple_list(config_data=self.config_data)
            if settings.DEBUG_PERMIT:
                print('* _config_data__simple_list:', self._config_data__simple_list)
        return self._config_data__simple_list

    def get_config_data__to_q(self, config_data__simple_list):
        if config_data__simple_list and isinstance(config_data__simple_list, list):
            return FilterComponentList(
                main_data=[
                    FilterComponent(
                        main_data=item,
                        logic_next='or',
                        skip_filter_employee=self.cls_decor.skip_filter_employee,
                    ) for item in config_data__simple_list
                ]
            ).django_q
        return Q()

    @property
    def config_data__to_q(self) -> Union[Q, None]:
        """
        Convert config simple list to django.db.models.Q
        """
        if not self._config_data__to_q and self.config_data__simple_list:
            self._config_data__to_q = self.get_config_data__to_q(config_data__simple_list=self.config_data__simple_list)
            if settings.DEBUG_PERMIT:
                print('* _config_data__to_q       :', self._config_data__to_q)
        return self._config_data__to_q

    @classmethod
    def check_permit_each_item(cls, key_full, data, obj_or_dict):
        # cho trường hợp elif nếu key là company_id và obj là models Company thì trả về id của models Company đó
        def get_value_special_key_for_obj(_key1):
            if _key1 in ['employee_inherit', 'opportunity', 'project']:
                return getattr(obj_or_dict, _key1 + '_id', None)
            if _key1 == 'company_id':
                company_model = DisperseModel(app_model='company.company').get_model()
                if isinstance(obj_or_dict, company_model):  # noqa
                    return getattr(obj_or_dict, 'id', None)
            return getattr(obj_or_dict, _key1, None)

        def get_value_special_key_for_dict(_key2):
            if _key2 == 'opportunity_id':
                if 'opportunity_id' in obj_or_dict:
                    return obj_or_dict['opportunity_id']
                if 'opportunity' in obj_or_dict:
                    return obj_or_dict['opportunity']

            if _key2 == 'project_id':
                if 'project_id' in obj_or_dict:
                    return obj_or_dict['project_id']
                if 'project' in obj_or_dict:
                    return obj_or_dict['project']

            if _key2 == 'employee_inherit_id':
                if 'employee_inherit_id' in obj_or_dict:
                    return obj_or_dict['employee_inherit_id']
                if 'employee_inherit' in obj_or_dict:
                    return obj_or_dict['employee_inherit']

            return obj_or_dict.get(_key2, None)

        key_arr = key_full.split("__")
        if len(key_arr) == 1:
            main_key, lookup_key = key_arr[0], None
        else:
            main_key, lookup_key = "__".join(key_arr[0:-1]), key_arr[-1]

        # True when All item in data_item is True, because operator is "AND"
        if main_key:
            if isinstance(obj_or_dict, dict):
                data_obj_key = get_value_special_key_for_dict(main_key)
            elif isinstance(obj_or_dict, object) and hasattr(obj_or_dict, 'id'):
                data_obj_key = get_value_special_key_for_obj(main_key)
            else:
                # out of support type
                return None

            if lookup_key is None:
                if str(data_obj_key) == str(data):
                    one_item_allow = True
                else:
                    # operator "AND" so one False is all False
                    one_item_allow = False
            elif lookup_key == 'isnull':
                if data_obj_key is None:
                    one_item_allow = True
                else:
                    # operator "AND" so one False is all False
                    one_item_allow = False
            elif lookup_key == 'in':
                if data and isinstance(data, list) and str(data_obj_key) in [str(x) for x in data]:
                    one_item_allow = True
                else:
                    # operator "AND" so one False is all False
                    one_item_allow = False
            elif lookup_key == '_exclude':
                if not data or (data and str(data_obj_key) != str(data)):
                    one_item_allow = True
                else:
                    # operator "AND" so one False is all False
                    one_item_allow = False
            else:
                # lookup not support --> auto False
                one_item_allow = False
        else:
            # key not support --> auto False
            one_item_allow = False
        return one_item_allow

    def config_data__check_obj(self, obj) -> bool:
        """
        """
        if obj and hasattr(obj, 'id'):
            if self._config_data__check_obj is None:
                if self.config_data__simple_list and isinstance(self.config_data__simple_list, list):
                    is_allow = False
                    for data_item in self.config_data__simple_list:
                        one_item_allow = None
                        for key_full, data in data_item.items():
                            if is_allow is True:
                                break

                            one_item_allow = self.check_permit_each_item(key_full=key_full, data=data, obj_or_dict=obj)
                            if one_item_allow is True:
                                one_item_allow = True
                                continue
                            else:
                                one_item_allow = False
                                break

                        if one_item_allow is True:
                            # Operator is "OR" so one child is True so All is True
                            is_allow = True
                            break

                    self._config_data__check_obj = is_allow
                else:
                    self._config_data__check_obj = False
        else:
            self._config_data__check_obj = False
        return self._config_data__check_obj

    def config_data__check_obj_on_id_list(self, obj):  # check perm on DOC_ID (workflow)
        try:
            data_check_id_list = {}
            for data_item in self.config_data__simple_list:
                if 'id__in' in data_item:
                    data_check_id_list = data_item
                    break
        except Exception as err:
            return False
        is_allow = False
        one_item_allow = None
        for key_full, data in data_check_id_list.items():
            if is_allow is True:
                break

            one_item_allow = self.check_permit_each_item(key_full=key_full, data=data, obj_or_dict=obj)
            if one_item_allow is True:
                one_item_allow = True
                continue
            else:
                one_item_allow = False
                break

        if one_item_allow is True:
            return True
        return False

    def config_data__check_by_opp(self, opp_id: Union[str, uuid4], employee_inherit_id: Union[str, uuid4]) -> bool:
        if opp_id and self.config_data and employee_inherit_id:
            try:
                # check perm on space global
                data_space_1 = []
                general_perm = self.config_data.get('employee', {}).get('general', {}).items()
                if general_perm:
                    for range_code, value in general_perm:
                        if value and isinstance(value, dict) and value.get('space', None) == '1':
                            data_space_1.append(range_code)
                    if data_space_1:
                        np_all_key = np.array(list(data_space_1))
                        if np.array_equal(np_all_key, np.array(['1'])):
                            if str(employee_inherit_id) == str(self.employee_attr.employee_current_id):
                                return True
                        elif np.array_equal(np_all_key, np.array(['2'])):
                            if str(employee_inherit_id) in self.employee_attr.employee_staff_ids__exclude_me():
                                return True
                        elif np.array_equal(np_all_key, np.array(['3'])):
                            if str(employee_inherit_id) in self.employee_attr.employee_same_group_ids__exclude_me():
                                return True
                        elif np.array_equal(np_all_key, np.array(['1', '2'])):
                            if str(employee_inherit_id) in self.employee_attr.employee_staff_ids__append_me():
                                return True
                        elif np.array_equal(np_all_key, np.array(['1', '3'])):
                            if str(employee_inherit_id) in self.employee_attr.employee_same_group_ids__append_me():
                                return True
                        elif (
                                np.array_equal(np_all_key, np.array(['1', '4']))
                                or np.array_equal(np_all_key, np.array(['1', '2', '4']))
                                or np.array_equal(np_all_key, np.array(['1', '3', '4']))
                                or np.array_equal(np_all_key, np.array(['1', '2', '3', '4']))
                        ):
                            return True
                        elif np.array_equal(np_all_key, np.array(['2', '3'])):
                            if str(employee_inherit_id) in (
                                    self.employee_attr.employee_staff_ids__exclude_me() +
                                    self.employee_attr.employee_same_group_ids__exclude_me()
                            ):
                                return True
                        elif (
                                np.array_equal(np_all_key, np.array(['4']))
                                or np.array_equal(np_all_key, np.array(['2', '4']))
                                or np.array_equal(np_all_key, np.array(['3', '4']))
                                or np.array_equal(np_all_key, np.array(['2', '3', '4']))
                        ):
                            if str(employee_inherit_id) != str(self.employee_attr.employee_current_id):
                                return True
                        elif np.array_equal(np_all_key, np.array(['1', '2', '3'])):
                            if str(employee_inherit_id) in (
                                    self.employee_attr.employee_staff_ids__append_me() +
                                    self.employee_attr.employee_same_group_ids__exclude_me()
                            ):
                                return True

                data = self.config_data.get('employee', {}).get('opp', {}).get(str(opp_id), {})
                if data:
                    return self.compare_special_permit_with_range_allowed(
                        data_permit=data, employee_current_id=self.employee_attr.employee_current_id,
                        employee_inherit_id=employee_inherit_id,
                        compare_main_id=opp_id,
                        has_from='opp',
                    )
            except Exception as err:
                print('[config_data__check_by_opp]', err)
        return False

    def config_data__check_by_prj(self, prj_id: Union[str, uuid4], employee_inherit_id: Union[str, uuid4]) -> bool:
        if prj_id and self.config_data and employee_inherit_id:
            try:
                data = self.config_data.get('employee', {}).get('prj', {}).get(str(prj_id), {})
            except Exception as err:
                return False

            return self.compare_special_permit_with_range_allowed(
                data_permit=data, employee_current_id=self.employee_attr.employee_current_id,
                employee_inherit_id=employee_inherit_id,
                compare_main_id=prj_id,
                has_from='prj',
            )
        return False

    def config_data__check_body_data(self, body_data: dict[str, any]) -> bool:
        """
        """
        if self._config_data__check_body_data is None:
            if body_data and isinstance(body_data, dict):
                if self.config_data__simple_list and isinstance(self.config_data__simple_list, list):
                    is_allow = False
                    for data_item in self.config_data__simple_list:
                        one_item_allow = None
                        for key_full, data in data_item.items():
                            if is_allow is True:
                                break

                            one_item_allow = self.check_permit_each_item(
                                key_full=key_full,
                                data=data,
                                obj_or_dict=body_data,
                            )
                            if one_item_allow is True:
                                one_item_allow = True
                                continue
                            else:
                                one_item_allow = False
                                break

                        if one_item_allow is True:
                            # Operator is "OR" so one child is True so All is True
                            is_allow = True
                            break

                    self._config_data__check_body_data = is_allow
                else:
                    self._config_data__check_body_data = False
            else:
                # auto allow = True when body_data check is dict empty
                self._config_data__check_body_data = True
        else:
            self._config_data__check_body_data = False
        return self._config_data__check_body_data

    def config_data__check_obj_and_body_data(self, obj, body_data) -> bool:
        if not self._config_data__check_obj_and_body_data:
            if obj and hasattr(obj, 'id') and body_data and isinstance(body_data, dict):
                obj_copy = deepcopy(obj)
                if 'employee_inherit' in body_data:
                    setattr(obj_copy, self.KEY_FILTER_INHERITOR_ID_IN_MODEL, body_data['employee_inherit'])
                if 'opportunity' in body_data:
                    setattr(obj_copy, self.KEY_FILTER_OPP_ID_IN_MODEL, body_data['opportunity'])
                if 'project' in body_data:
                    setattr(obj_copy, self.KEY_FILTER_PRJ_ID_IN_MODEL, body_data['project'])
                self._config_data__check_obj_and_body_data = self.config_data__check_obj(obj=obj_copy)
            else:
                self._config_data__check_obj_and_body_data = False
        return self._config_data__check_obj_and_body_data

    def __init__(self, cls_employee_attr: EmployeeAttribute, cls_decor: ViewConfigDecorator, **kwargs):
        self._config_data: dict = None
        self._config_data__by_code: dict[str, dict] = {}
        self._has_permit_exist = None
        self._config_data__simple_list = []
        self._config_data__to_q: Q = Q()
        self._config_data__check_obj = None
        self._config_data__check_body_data = None
        self._config_data__check_obj_and_body_data = None

        # config_check_permit sample:
        # {
        #     'label_code': self.label_code.lower(),
        #     'model_code': self.model_code.lower(),
        #     'perm_code': self.perm_code.lower(),
        # }

        self.employee_attr = cls_employee_attr
        self.cls_decor = cls_decor
        self.config_check_permit = cls_decor.config_check_permit
        # opp_enabled: bool = False, prj_enabled: bool = False,
        self.opp_enabled: bool = kwargs.get('opp_enabled', False)
        self.prj_enabled: bool = kwargs.get('prj_enabled', False)

        self.state_depend_on = kwargs.get('state_depend_on', None)

    def config_data__simple_list__item(self, item_data) -> list[dict]:
        """
        Support convert one item config of permit code
        """
        # sample = {
        #     'general': {'4': {}},
        #     'ids': {'{id}': {}},
        #     'opp': {'{id}': {}},
        #     'prj': {'{id}': {}},
        # }

        result_or = []

        app_obj = item_data.get('app_obj', None)
        if app_obj:
            general_data = item_data.get('general', {})
            if general_data:
                tmp = self.config_data__simple_list__item__parse_range(
                    allowed_range_or_ids_data=general_data,
                    filtering_inheritor=app_obj.filtering_inheritor,
                    from_permit='general',
                )
                if tmp:
                    if isinstance(tmp, dict):
                        result_or.append(tmp)
                    elif isinstance(tmp, list):
                        result_or += tmp

            ids_data = item_data.get('ids', {})
            if ids_data:
                tmp = self.config_data__simple_list__item__parse_range(
                    allowed_range_or_ids_data=ids_data,
                    filtering_inheritor=app_obj.filtering_inheritor,
                    from_permit='ids',
                )
                if tmp:
                    if isinstance(tmp, dict):
                        result_or.append(tmp)
                    elif isinstance(tmp, list):
                        result_or += tmp

            if self.opp_enabled is True:
                opp_data = item_data.get('opp', {})
                if opp_data:
                    for opp_id, opp_value in opp_data.items():
                        tmp = self.config_data__simple_list__item__parse_range(
                            allowed_range_or_ids_data=opp_value,
                            filtering_inheritor=app_obj.filtering_inheritor,
                            from_permit='opp',
                            from_id=opp_id,
                        )
                        if tmp:
                            if isinstance(tmp, dict):
                                result_or.append(tmp)
                            elif isinstance(tmp, list):
                                result_or += tmp

            if self.prj_enabled is True:
                prj_data = item_data.get('prj', {})
                if prj_data:
                    for prj_id, prj_value in prj_data.items():
                        tmp = self.config_data__simple_list__item__parse_range(
                            allowed_range_or_ids_data=prj_value,
                            filtering_inheritor=app_obj.filtering_inheritor,
                            from_permit='prj',
                            from_id=prj_id
                        )
                        if tmp:
                            if isinstance(tmp, dict):
                                result_or.append(tmp)
                            elif isinstance(tmp, list):
                                result_or += tmp
        else:
            if settings.DEBUG_PERMIT:
                print('=> skip parse simple       :', 'Application Object is not found', item_data)
        return result_or

    @classmethod
    def parse_space_from_general_config(cls, allowed_range, group_to_space=False):
        result = {}
        for key, value in allowed_range.items():
            if isinstance(value, dict):
                if value and 'space' in value:
                    result[key] = value['space']
                else:
                    result[key] = '0'  # default

        if group_to_space is True:
            space_group = {}
            for permit, space in result.items():
                if space in space_group:
                    space_group[space].append(permit)
                else:
                    space_group[space] = [permit]
            return space_group

        return result

    @classmethod
    def parse_general_from_custom_key(cls, permit_of_space: list[str], **kwargs):
        employee_attr: EmployeeAttribute = kwargs.get('employee_attr')
        key_inheritor_filter: str = kwargs.get('key_inheritor_filter', 'employee_inherit_id')
        key_company_filter: str = kwargs.get('key_company_filter', 'company_id')
        is_filtering_inheritor: bool = kwargs.get('is_filtering_inheritor', True)

        np_all_key = np.array(list(permit_of_space))
        if settings.DEBUG_PERMIT:
            print(
                '* [custom_key] np_all_key  :',
                'np_all_key = ', np_all_key,
                ',', 'key_inheritor_filter =', key_inheritor_filter,
                ',', 'key_company_filter =', key_company_filter,
                ',', 'is_filtering_inheritor =', is_filtering_inheritor,
                ',', 'employee_current_id =', employee_attr.employee_current_id,
            )

        if np.array_equal(np_all_key, np.array([])):
            # empty keep default
            pass

        if np.array_equal(np_all_key, np.array(['1'])):
            # only me | keep default if current user haven't employee related!
            if employee_attr.employee_current_id:
                return {key_inheritor_filter: str(employee_attr.employee_current_id)}
            return {key_inheritor_filter + '__in': []}

        if np.array_equal(np_all_key, np.array(['2'])):
            # staff + exclude me
            return {key_inheritor_filter + '__in': employee_attr.employee_staff_ids__exclude_me()}

        if np.array_equal(np_all_key, np.array(['3'])):
            # same group + exclude me
            return {key_inheritor_filter + '__in': employee_attr.employee_same_group_ids__exclude_me()}

        if np.array_equal(np_all_key, np.array(['4'])):
            # everybody + exclude me if current user has employee related!
            data = {key_company_filter: employee_attr.company_id}
            if is_filtering_inheritor is True and employee_attr.employee_current_id:
                # push exclude me to data
                data[key_inheritor_filter + '___exclude'] = str(employee_attr.employee_current_id)
            return data

        if np.array_equal(np_all_key, np.array(['1', '2'])):
            # staff + append me
            return {key_inheritor_filter + '__in': employee_attr.employee_staff_ids__append_me()}

        if np.array_equal(np_all_key, np.array(['1', '3'])):
            # same group + append me
            return {key_inheritor_filter + '__in': employee_attr.employee_same_group_ids__append_me()}

        if np.array_equal(np_all_key, np.array(['1', '4'])):
            # everybody + append me (append me in here is not append filter exclude me to data)
            return {key_company_filter: employee_attr.company_id}

        if np.array_equal(np_all_key, np.array(['2', '3'])):
            # staff + same group + exclude me
            return {
                key_inheritor_filter + '__in': (
                        employee_attr.employee_staff_ids__exclude_me() +
                        employee_attr.employee_same_group_ids__exclude_me()
                )
            }

        if np.array_equal(np_all_key, np.array(['2', '4'])):
            # everybody + skip staff + exclude me if current user has employee related!
            data = {key_company_filter: employee_attr.company_id}
            if is_filtering_inheritor is True and employee_attr.employee_current_id:
                # push exclude me to data
                data[key_inheritor_filter + '___exclude'] = str(employee_attr.employee_current_id)
            return data

        if np.array_equal(np_all_key, np.array(['3', '4'])):
            # everybody + skip same group + exclude me if current user has employee related!
            data = {
                key_company_filter: employee_attr.company_id
            }
            if is_filtering_inheritor is True and employee_attr.employee_current_id:
                # push exclude me to data
                data[key_inheritor_filter + '___exclude'] = str(employee_attr.employee_current_id)
            return data

        if np.array_equal(np_all_key, np.array(['1', '2', '3'])):
            # staff + same group + append me
            return {
                key_inheritor_filter + '__in': (
                        employee_attr.employee_staff_ids__append_me() +
                        employee_attr.employee_same_group_ids__exclude_me()
                )
            }

        if np.array_equal(np_all_key, np.array(['1', '2', '4'])):
            # everybody + skip staff + skip exclude me
            return {key_company_filter: employee_attr.company_id}

        if np.array_equal(np_all_key, np.array(['1', '3', '4'])):
            # everybody + skip same group + skip exclude me
            return {key_company_filter: employee_attr.company_id}

        if np.array_equal(np_all_key, np.array(['2', '3', '4'])):
            # everybody + skip staff + skip same group + exclude me
            data = {key_company_filter: employee_attr.company_id}
            if is_filtering_inheritor is True and employee_attr.employee_current_id:
                # push exclude me to data
                data[key_inheritor_filter + '___exclude'] = str(employee_attr.employee_current_id)
            return data

        if np.array_equal(np_all_key, np.array(['1', '2', '3', '4'])):
            # everybody + skip staff + skip same group + skip exclude me
            return {key_company_filter: employee_attr.company_id}

        return {}

    def parse_general_with_space(self, permit_of_space, space_config_code, filtering_inheritor):
        # key_filter = self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '__in'
        # value_filter = []

        # data = {}
        # np_all_key = np.array(list(permit_of_space))
        #
        # if settings.DEBUG_PERMIT:
        #     print('* [GENERAL] np_all_key     :', np_all_key, space_config_code, filtering_inheritor)
        #
        # if np.array_equal(np_all_key, np.array([])):
        #     # empty keep default
        #     pass
        # elif np.array_equal(np_all_key, np.array(['1'])):
        #     # only me | keep default if current user haven't employee related!
        #     if self.employee_attr.employee_current_id:
        #         data = {
        #             self.KEY_FILTER_INHERITOR_ID_IN_MODEL: str(self.employee_attr.employee_current_id)
        #         }
        # elif np.array_equal(np_all_key, np.array(['2'])):
        #     # staff + exclude me
        #     data = {
        #         self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '__in': self.employee_attr.employee_staff_ids__exclude_me()
        #     }
        # elif np.array_equal(np_all_key, np.array(['3'])):
        #     # same group + exclude me
        #     data = {
        #         self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '__in': self.employee_attr.employee_same_group_ids__exclude_me()
        #     }
        # elif np.array_equal(np_all_key, np.array(['4'])):
        #     # everybody + exclude me if current user has employee related!
        #     data = {
        #         self.KEY_FILTER_COMPANY_ID_IN_MODEL: self.employee_attr.company_id
        #     }
        #     if filtering_inheritor is True and self.employee_attr.employee_current_id:
        #         # push exclude me to data
        #         data[self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '___exclude'] = str(self.employee_attr.employee_current_id)
        # elif np.array_equal(np_all_key, np.array(['1', '2'])):
        #     # staff + append me
        #     data = {
        #         self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '__in': self.employee_attr.employee_staff_ids__append_me()
        #     }
        # elif np.array_equal(np_all_key, np.array(['1', '3'])):
        #     # same group + append me
        #     data = {
        #         self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '__in': self.employee_attr.employee_same_group_ids__append_me()
        #     }
        # elif np.array_equal(np_all_key, np.array(['1', '4'])):
        #     # everybody + append me (append me in here is not append filter exclude me to data)
        #     data = {
        #         self.KEY_FILTER_COMPANY_ID_IN_MODEL: self.employee_attr.company_id
        #     }
        # elif np.array_equal(np_all_key, np.array(['2', '3'])):
        #     # staff + same group + exclude me
        #     data = {
        #         self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '__in': (
        #                 self.employee_attr.employee_staff_ids__exclude_me() +
        #                 self.employee_attr.employee_same_group_ids__exclude_me()
        #         )
        #     }
        # elif np.array_equal(np_all_key, np.array(['2', '4'])):
        #     # everybody + skip staff + exclude me if current user has employee related!
        #     data = {
        #         self.KEY_FILTER_COMPANY_ID_IN_MODEL: self.employee_attr.company_id
        #     }
        #     if filtering_inheritor is True and self.employee_attr.employee_current_id:
        #         # push exclude me to data
        #         data[self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '___exclude'] = str(self.employee_attr.employee_current_id)
        # elif np.array_equal(np_all_key, np.array(['3', '4'])):
        #     # everybody + skip same group + exclude me if current user has employee related!
        #     data = {
        #         self.KEY_FILTER_COMPANY_ID_IN_MODEL: self.employee_attr.company_id
        #     }
        #     if filtering_inheritor is True and self.employee_attr.employee_current_id:
        #         # push exclude me to data
        #         data[self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '___exclude'] = str(
        #             self.employee_attr.employee_current_id
        #         )
        # elif np.array_equal(np_all_key, np.array(['1', '2', '3'])):
        #     # staff + same group + append me
        #     data = {
        #         self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '__in': (
        #                 self.employee_attr.employee_staff_ids__append_me() +
        #                 self.employee_attr.employee_same_group_ids__exclude_me()
        #         )
        #     }
        # elif np.array_equal(np_all_key, np.array(['1', '2', '4'])):
        #     # everybody + skip staff + skip exclude me
        #     data = {
        #         self.KEY_FILTER_COMPANY_ID_IN_MODEL: self.employee_attr.company_id
        #     }
        # elif np.array_equal(np_all_key, np.array(['1', '3', '4'])):
        #     # everybody + skip same group + skip exclude me
        #     data = {
        #         self.KEY_FILTER_COMPANY_ID_IN_MODEL: self.employee_attr.company_id
        #     }
        # elif np.array_equal(np_all_key, np.array(['2', '3', '4'])):
        #     # everybody + skip staff + skip same group + exclude me
        #     data = {
        #         self.KEY_FILTER_COMPANY_ID_IN_MODEL: self.employee_attr.company_id
        #     }
        #     if filtering_inheritor is True and self.employee_attr.employee_current_id:
        #         # push exclude me to data
        #         data[self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '___exclude'] = str(
        #             self.employee_attr.employee_current_id
        #         )
        # elif np.array_equal(np_all_key, np.array(['1', '2', '3', '4'])):
        #     # everybody + skip staff + skip same group + skip exclude me
        #     data = {
        #         self.KEY_FILTER_COMPANY_ID_IN_MODEL: self.employee_attr.company_id
        #     }
        # else:
        #     print('[General] Unbelievable! **Auto filter inherit id in empty list**')

        data = self.parse_general_from_custom_key(
            permit_of_space=permit_of_space,
            employee_attr=self.employee_attr,
            key_inheritor_filter=self.KEY_FILTER_INHERITOR_ID_IN_MODEL,
            key_company_filter=self.KEY_FILTER_COMPANY_ID_IN_MODEL,
            is_filtering_inheritor=filtering_inheritor,
        )
        if data and space_config_code == '0':
            if self.opp_enabled:
                data.update({self.KEY_FILTER_OPP_ID_IN_MODEL + '__isnull': True})
            if self.prj_enabled:
                data.update({self.KEY_FILTER_PRJ_ID_IN_MODEL + '__isnull': True})
        return data

    def config_data__simple_list__item__parse_range(  # pylint: disable=R0915
            self, allowed_range_or_ids_data, filtering_inheritor, from_permit='general', from_id=None
    ) -> dict | list[dict]:
        """
        Support convert a item config of zone in permit code to data filter
            - Zone in permit code: 'general', 'ids', 'opp', 'prj'
        allowed_range_or_ids_data: support in ["1", "2", "3", "4"]
        ```python
            from itertools import combinations
            numbers = ["1", "2", "3", "4"]
            for combination in combinations(numbers, r=None):
                print(combination)
        ```
        ```output.txt
            ()
            (1)
            (2)
            (3)
            (4)
            (1, 2)
            (1, 3)
            (1, 4)
            (2, 3)
            (2, 4)
            (3, 4)
            (1, 2, 3)
            (1, 2, 4)
            (1, 3, 4)
            (2, 3, 4)
        ```
        """
        data = {}

        if from_permit == 'ids':
            ids_data = list(allowed_range_or_ids_data.keys())
            if ids_data:
                data = {'id__in': ids_data}
            return data

        if from_permit == 'general':
            data_general = []

            # space of permit
            space_of_permit = self.parse_space_from_general_config(
                allowed_range=allowed_range_or_ids_data,
                group_to_space=True,
            )
            if space_of_permit and isinstance(space_of_permit, dict):
                if '0' in space_of_permit:
                    data_tmp = self.parse_general_with_space(
                        permit_of_space=space_of_permit['0'],
                        space_config_code='0',
                        filtering_inheritor=filtering_inheritor,
                    )
                    if data_tmp and isinstance(data_tmp, dict):
                        data_general.append(data_tmp)

                if '1' in space_of_permit:
                    data_tmp = self.parse_general_with_space(
                        permit_of_space=space_of_permit['1'],
                        space_config_code='1',
                        filtering_inheritor=filtering_inheritor,
                    )
                    if data_tmp and isinstance(data_tmp, dict):
                        data_general.append(data_tmp)

            return data_general

        if from_id:
            # keep default filter return to empty with "id__in=[]"
            key_filter = self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '__in'
            value_filter = []

            np_all_key = np.array(list(allowed_range_or_ids_data.keys()))
            if from_permit == 'opp':
                if settings.DEBUG_PERMIT:
                    print(f'* [OPP] np_all_key         :', np_all_key)
                # auto filter opp
                data.update(
                    {self.KEY_FILTER_OPP_ID_IN_MODEL: from_id}
                )
                if np.array_equal(np_all_key, np.array(['1'])):
                    # only me
                    if self.employee_attr.employee_current_id:
                        data.update(
                            {
                                self.KEY_FILTER_INHERITOR_ID_IN_MODEL: self.employee_attr.employee_current_id
                            }
                        )
                    else:
                        # force query return empty!
                        data.update(
                            {
                                self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '__in': []
                            }
                        )
                elif np.array_equal(np_all_key, np.array(['4'])):
                    # all member + exclude me if current user has employee related!
                    if filtering_inheritor is True and self.employee_attr.employee_current_id:
                        data.update(
                            {
                                self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '___exclude':
                                    self.employee_attr.employee_current_id
                            }
                        )
                    else:
                        # force query return empty!
                        data.update(
                            {
                                self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '__in': []
                            }
                        )
                elif np.array_equal(np_all_key, np.array(['1', '4'])):
                    # all member + me | skip because auto filter opp above is enough!
                    pass
                else:
                    # force query return empty!
                    data.update(
                        {
                            self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '__in': []
                        }
                    )
                    print('[Opp] Unbelievable! **Auto filter inherit id in empty list**')
            elif from_permit == 'prj':
                if settings.DEBUG_PERMIT:
                    print(f'* [PRJ] np_all_key         :', np_all_key)
                # auto filter opp
                data.update(
                    {self.KEY_FILTER_PRJ_ID_IN_MODEL: from_id}
                )
                if np.array_equal(np_all_key, np.array(['1'])):
                    # only me
                    if self.employee_attr.employee_current_id:
                        data.update(
                            {
                                self.KEY_FILTER_INHERITOR_ID_IN_MODEL: self.employee_attr.employee_current_id
                            }
                        )
                    else:
                        # force query return empty!
                        data.update(
                            {
                                self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '__in': []
                            }
                        )
                elif np.array_equal(np_all_key, np.array(['4'])):
                    # all member + exclude me if current user has employee related!
                    if filtering_inheritor is True and self.employee_attr.employee_current_id:
                        data.update(
                            {
                                self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '___exclude':
                                    self.employee_attr.employee_current_id
                            }
                        )
                    else:
                        # force query return empty!
                        data.update(
                            {
                                self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '__in': []
                            }
                        )
                elif np.array_equal(np_all_key, np.array(['1', '4'])):
                    # all member + me | skip because auto filter opp above is enough!
                    pass
                else:
                    # force query return empty!
                    data.update(
                        {
                            self.KEY_FILTER_INHERITOR_ID_IN_MODEL + '__in': []
                        }
                    )
                    print('[Opp] Unbelievable! **Auto filter inherit id in empty list**')
        return data


class ViewChecking:
    @property
    def skip_because_match_with_admin(self):
        """
        Check config and info of current user for skip auth_require step

        Returns:
            True if allow skip by current user has permit.
            False if config not allow or current user not match config.
        """
        if not self._skip_because_match_with_admin:
            if self.decor.has_allow_admin:
                if self.decor.allow_admin_tenant and self.attr.is_admin_tenant:
                    self._skip_because_match_with_admin = True
                if self.decor.allow_admin_company and self.attr.is_admin_company:
                    self._skip_because_match_with_admin = True
        return self._skip_because_match_with_admin

    def __init__(self, cls_attr: ViewAttribute, cls_decor: ViewConfigDecorator):
        self.filter_from_config = None
        self.filter_parse_to_cls = None
        self.filter_parse_to_q = None
        self._skip_because_match_with_admin: bool = False

        self.attr = cls_attr
        self.decor = cls_decor
        self.employee_attr = EmployeeAttribute(employee_obj=cls_attr.employee_current)

        state_depend_on = False if self.attr.request_method == 'GET' and self.attr.has_dropdown_list is True else None

        self.permit_cls = PermissionController(
            cls_employee_attr=self.employee_attr,
            cls_decor=cls_decor,
            opp_enabled=self.decor.opp_enabled,
            prj_enabled=self.decor.prj_enabled,
            state_depend_on=state_depend_on,
        )

    def always_check(self) -> Union[True, ResponseController]:
        """
        This function is checking overview some require of all requests
        """

        # check pk in url is UUID
        for key, value in self.attr.view_kwargs.items():
            if key.startswith('pk_'):
                if not TypeCheck.check_uuid(value):
                    return HttpReturn.error_not_found()

        # check login_require | check user in request is exist and not Anonymous
        if self.decor.auth_require or self.decor.employee_require:
            self.decor.login_require = True
        if self.decor.login_require and not self.attr.user:
            return HttpReturn.error_login_require(error_login_require=self.attr.error_login_require)

        # check employee object required in request.user
        if self.decor.employee_require is True and not self.attr.employee_current_id:
            return HttpReturn.error_employee_require(error_employee_require=self.attr.error_employee_require)

        return True

    def permit_check(self) -> Union[True, ResponseController]:
        """
        This function is check, get, fill data for Mixin working
        """
        # *************************************************************
        # * : required  |   [] : optional
        # Some variable must/should update data before the MIXIN was called
        #       1. *    self.permit_cls.config_data
        #       2. []   self.permit_cls.config_data__simple_list
        #       3. []   self.permit_cls.config_data__to_q
        #       4. []   self.permit_cls.config_data__check_obj_and_body_data
        # *************************************************************

        state_tmp = False
        if self.decor.config_check_permit:
            # auto setup permit if config is exists
            state_tmp = self.permit_cls.config_data and self.permit_cls.config_data__exist

        if self.skip_because_match_with_admin:
            # view allow admin and request.user.is_admin are True
            pass_auth_permit = True
        else:
            if self.decor.auth_require is True:
                # always check by permit config
                if not self.decor.config_check_permit:
                    return HttpReturn.error_config_view_incorrect()
                pass_auth_permit = state_tmp
            else:
                pass_auth_permit = True

        if not pass_auth_permit:
            return HttpReturn.error_auth_require(
                request_method=self.attr.request_method,
                has_dropdown_list=self.attr.has_dropdown_list,
                error_auth_require=self.attr.error_auth_require,
            )

        # fake call API check perm | return status = 200
        if self.attr.has_check_perm is True:
            return HttpReturn.success_empty_dict()

        return True


def mask_view(**parent_kwargs):
    if not isinstance(parent_kwargs, dict):
        parent_kwargs = {}

    # fake typehint for parent_kwargs
    decor_kwargs = {
        **parent_kwargs,
        'employee_require': parent_kwargs.get('employee_require', False),
        'login_require': parent_kwargs.get('login_require', True),
        'auth_require': parent_kwargs.get('auth_require', False),
        'bastion_field_require': parent_kwargs.get('bastion_field_require', False),
        'use_custom_get_filter_auth': parent_kwargs.get('use_custom_get_filter_auth', False),
        'allow_admin_tenant': parent_kwargs.get('allow_admin_tenant', False),
        'allow_admin_company': parent_kwargs.get('allow_admin_company', False),
        'label_code': parent_kwargs.get('label_code', None), 'model_code': parent_kwargs.get('model_code', None),
        'perm_code': parent_kwargs.get('perm_code', None), 'opp_enabled': parent_kwargs.get('opp_enabled', False),
        'prj_enabled': parent_kwargs.get('prj_enabled', False),
        'skip_filter_employee': parent_kwargs.get('skip_filter_employee', False),
    }

    # -- fake typehint for parent_kwargs

    def decorated(func_view):
        def wrapper(self, *args, **kwargs):  # pylint: disable=R0911
            # init cls checking
            _cls_attr = ViewAttribute(view_this=self)
            _cls_decor = ViewConfigDecorator(parent_kwargs=decor_kwargs)
            cls_check = ViewChecking(cls_attr=_cls_attr, cls_decor=_cls_decor)
            setattr(self, 'cls_check', cls_check)  # save cls to view for view using it get some data

            # check for all request
            always_check = cls_check.always_check()
            if always_check is True:
                # check & get * fill some data to self for MIXINS working
                permit_check = cls_check.permit_check()
                if permit_check is True:
                    # active translate if request.user is anonymous
                    if self.request.user is AnonymousUser or self.request.user.is_authenticated is False:
                        if settings.DEBUG_PERMIT:
                            print(
                                'active language [mask_view]:',
                                self.request.headers.get('Accept-Language', settings.LANGUAGE_CODE),
                                _cls_attr.header_language()
                            )
                        translation.activate(_cls_attr.header_language())

                    # call view when access login and auth permission | Data returned is three case:
                    #   1. ValidateError from valid --> convert to HTTP 400
                    #   2. Exception another: Return 500 with msg is errors
                    #   3. Tuple: (data, status)
                    try:
                        view_return = func_view(self, *args, **kwargs)  # --> {'user_list': user_list}
                        if isinstance(view_return, HttpResponse):
                            return view_return
                        if isinstance(view_return, Exception):
                            return view_return
                        if isinstance(view_return, (list, tuple)) and len(view_return) == 2:
                            data, http_status = view_return
                            match http_status:
                                case status.HTTP_401_UNAUTHORIZED:
                                    return ResponseController.unauthorized_401()
                                case status.HTTP_500_INTERNAL_SERVER_ERROR:
                                    return ResponseController.internal_server_error_500()
                                case status.HTTP_400_BAD_REQUEST:
                                    return ResponseController.bad_request_400(msg=data)
                                case _:
                                    return Response({'data': data, 'status': http_status}, status=http_status)
                    except serializers.ValidationError as err:
                        raise err
                    except rest_framework.exceptions.PermissionDenied as err:
                        return ResponseController.forbidden_403(msg=str(err.detail))
                    except rest_framework.exceptions.AuthenticationFailed as err:
                        return ResponseController.unauthorized_401(msg=str(err.detail))
                    except rest_framework.exceptions.NotFound:
                        return ResponseController.notfound_404()
                    except Empty200:
                        return ResponseController.success_200(data=[])
                    except Exception as err:
                        handle_exception_all_view(err, self)
                        return ResponseController.internal_server_error_500(msg=str(err) if settings.DEBUG else '')
                    raise ValueError('Return not map happy case.')

                return permit_check

            return always_check

        return wraps(func_view)(wrapper)

    return decorated

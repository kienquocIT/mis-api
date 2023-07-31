import sys
from functools import wraps
from typing import Union
import numpy as np

import rest_framework.exceptions
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse

from rest_framework import status, serializers
from rest_framework.response import Response

from .controllers import ResponseController
from .utils import TypeCheck

__all__ = ['mask_view']


class PermissionChecking:  # pylint: disable=R0902
    def __init__(self, user_obj, employee_obj, plan_code, app_code, perm_code, space_code=''):
        self.plan_code = plan_code.lower()
        self.app_code = app_code.lower()
        self.perm_code = perm_code.lower()

        self.user_obj = user_obj
        self.employee_obj = employee_obj
        if self.employee_obj:
            self.tenant_id = self.employee_obj.tenant_id
            self.company_id = self.employee_obj.company_id
        elif self.user_obj:
            self.tenant_id = self.user_obj.tenant_current_id
            self.company_id = self.user_obj.company_current_id

        self.permissions_parsed = getattr(self.employee_obj, 'permissions_parsed', {})

        self.permission_by_id = getattr(self.employee_obj, 'permission_by_id', {})
        if not isinstance(self.permission_by_id, dict):
            self.permission_by_id = {}

        if not isinstance(self.permissions_parsed, dict):
            self.permissions_parsed = {}
        self.permissions_parsed = self.permissions_parsed.get(space_code, {})

    def _parse_config_append_filter(self, config_data):
        filter_dict = {}
        if "4" in config_data:
            filter_dict['company_id'] = str(self.employee_obj.company_id)
        else:
            np_all_key = np.array(config_data.keys())
            if np.array_equal(np_all_key, np.array([1])):
                filter_dict['employee_created_id'] = str(self.employee_obj.id)
            elif np.array_equal(np_all_key, np.array([2])):
                filter_dict['employee_created_id__in'] = []  # append staff
            elif np.array_equal(np_all_key, np.array([3])):
                filter_dict['employee_created_id__in'] = []  # append same group
            elif np.array_equal(np_all_key, np.array([1, 2])):
                filter_dict['employee_created_id__in'] = [str(self.employee_obj.id)]  # append staff
            elif np.array_equal(np_all_key, np.array([1, 3])):
                filter_dict['employee_created_id__in'] = [str(self.employee_obj.id)]  # append same group
            elif np.array_equal(np_all_key, np.array([2, 3])):
                filter_dict['employee_created_id__in'] = []  # same group + staff
            elif np.array_equal(np_all_key, np.array([1, 2, 3])):
                # append same group + staff
                filter_dict['employee_created_id__in'] = [str(self.employee_obj.id)]
        return filter_dict

    def check_and_get_filter(self) -> (Union[None, dict], Union[None, dict]):
        if self.plan_code in self.permissions_parsed:
            if self.app_code in self.permissions_parsed[self.plan_code]:
                if self.perm_code in self.permissions_parsed[self.plan_code][self.app_code]:
                    config_data = self.permissions_parsed[self.plan_code][self.app_code][self.perm_code]
                    filter_dict = self._parse_config_append_filter(config_data=config_data)
                    if filter_dict:
                        return (
                            config_data,
                            {
                                'tenant_id': str(self.tenant_id),
                                **filter_dict
                            }
                        )
                    print('[Permission][Valid] Generate filter was return empty.')
        return None, None

    def get_filter_of_admin(self) -> (Union[None, dict], Union[None, dict]):
        if self.tenant_id and self.company_id:
            return (
                {"4": {}},  # everyone in company
                {'tenant_id': str(self.tenant_id), 'company_id': str(self.company_id)}
            )
        return None, None


class AuthPermission:
    @property
    def _has_dropdown_list(self):
        if self.request.method == 'GET':
            return self.request.META.get(
                'HTTP_DATAISDD',
                None
            ) == 'true'
        return False

    @property
    def has_check_perm(self):
        if self.request.META.get('HTTP_DATAHASPERM', False) == 'true':
            return True
        return False

    def _auth_required_failed(self, has_check_perm):
        if self.request.method == 'GET' and self._has_dropdown_list is True:
            return ResponseController.success_200(data=[])
        if has_check_perm is True:
            return ResponseController.forbidden_403()
        return self.return_error_auth_require

    def _get_filter(self) -> Union[False, dict]:
        """
        Get filter_dict from employee_current and plan, app, perm of class
        Returns:

        """
        if self.check_allow['_is_allow_admin']:
            config_data, filter_dict = PermissionChecking(
                user_obj=self.user,
                employee_obj=None,
                plan_code=self.perm_data.get('plan_code', None),
                app_code=self.perm_data.get('app_code', None),
                perm_code=self.perm_data.get('perm_code', None),
            ).get_filter_of_admin()
            if config_data and filter_dict:
                self.set_perm_config_mapped(config_data=config_data)
                return filter_dict
        employee_obj = getattr(self.user, 'employee_current', None)
        if employee_obj:
            config_data, filter_dict = PermissionChecking(
                user_obj=self.user,
                employee_obj=employee_obj,
                plan_code=self.perm_data.get('plan_code', None),
                app_code=self.perm_data.get('app_code', None),
                perm_code=self.perm_data.get('perm_code', None),
            ).check_and_get_filter()
            if config_data and filter_dict:
                self.set_perm_config_mapped(config_data=config_data)
                return filter_dict
        return False

    @property
    def return_error_employee_require(self):
        if hasattr(self.view_this, 'error_login_require'):
            return getattr(self.view_this, 'error_login_require')()
        return ResponseController.forbidden_403()

    @property
    def return_error_login_require(self):
        if hasattr(self.view_this, 'error_login_require'):
            return getattr(self.view_this, 'error_login_require')()
        return ResponseController.unauthorized_401()

    @property
    def return_error_auth_require(self):
        if hasattr(self.view_this, 'error_auth_require'):
            return getattr(self.view_this, 'error_auth_require')()
        return ResponseController.forbidden_403()

    def set_filter_dict(self, result_filter):
        setattr(self.view_this, 'filter_dict', result_filter)
        return result_filter

    def set_perm_config_mapped(self, config_data):
        setattr(self.view_this, 'perm_config_mapped', config_data)
        return config_data

    def __init__(self, view_this, request, **kwargs):
        self.view_this = view_this
        self.request = request
        self.user = request.user
        if not self.user or isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            self.user = None

        allow_admin_tenant = kwargs.get('allow_admin_tenant', False)
        allow_admin_company = kwargs.get('allow_admin_company', False)
        self.check_allow = {
            'allow_admin_tenant': allow_admin_tenant,
            'allow_admin_company': allow_admin_company,
            '_is_allow_admin': allow_admin_tenant or allow_admin_company,
        }

        self.use_custom = {
            'get_filter_auth': kwargs.get('use_custom_get_filter_auth', False),
        }

        plan_code = kwargs.get('plan_code', None)
        app_code = kwargs.get('app_code', None)
        perm_code = kwargs.get('perm_code', None)
        self.perm_data = {
            'plan_code': plan_code.lower() if plan_code else None,
            'app_code': app_code.lower() if app_code else None,
            'perm_code': perm_code.lower() if perm_code else None,
        } if plan_code and app_code and perm_code else {}

    def always_check(
            self,
            self_kwargs,
            login_require,
            employee_require,
            auth_require,
    ) -> Union[True, ResponseController]:
        # check pk in url is UUID
        if 'pk' in self_kwargs and not TypeCheck.check_uuid(self_kwargs['pk']):
            return ResponseController.notfound_404()

        # get require key check
        if auth_require or employee_require:
            login_require = True

        # check login_require | check user in request is exist and not Anonymous
        if login_require and not self.user:
            return self.return_error_login_require

        # check employee object required in request.user
        if employee_require is True and not getattr(self.user, 'employee_current_id', None):
            return self.return_error_employee_require

        return True

    def auth_check(self, auth_require: bool) -> Union[True, ResponseController]:
        has_check_perm = self.has_check_perm
        result_filter = {}
        admin_skip_filter = False
        if self.check_allow['_is_allow_admin']:
            if self.request.user.is_admin_tenant:
                admin_skip_filter = True

        if auth_require and not admin_skip_filter:
            if not self.perm_data:
                return self._auth_required_failed(has_check_perm=has_check_perm)
            result_filter = self._get_filter()
            if not result_filter:
                return self._auth_required_failed(has_check_perm=has_check_perm)

        # fake call API check perm | return status = 200
        if has_check_perm is True:
            return Response({}, status=status.HTTP_200_OK)

        if self.use_custom['get_filter_auth'] and hasattr(self.view_this, 'get_filter_auth'):
            result_filter = self.view_this.get_filter_auth()
        return self.set_filter_dict(result_filter)


def mask_view(**parent_kwargs):
    # login_require: default True
    # auth_require: default False
    # code_perm = default None
    if not isinstance(parent_kwargs, dict):
        parent_kwargs = {}

    def decorated(func_view):
        def wrapper(self, request, *args, **kwargs):  # pylint: disable=R0911,R0912,R0914
            print(request)
            # request.user.employee_current: required
            employee_require: bool = parent_kwargs.get('employee_require', False)

            # request.user: User Object
            login_require: bool = parent_kwargs.get('login_require', True)

            # check Authenticated + Allow Permit
            auth_require: bool = parent_kwargs.get('auth_require', False)

            # Use func custom get filter | override get_filter_dict in class view
            use_custom_get_filter_auth: bool = parent_kwargs.get('use_custom_get_filter_auth', False)

            # skip with user is is_admin_tenant
            allow_admin_tenant: bool = parent_kwargs.get('allow_admin_tenant', False)

            # skip with user is skip_admin
            allow_admin_company: bool = parent_kwargs.get('allow_admin_company', False)

            # plan code for checking
            plan_code: str = parent_kwargs.get('plan_code', None)

            # app code for checking
            app_code: str = parent_kwargs.get('app_code', None)

            # perm code for checking
            perm_code: str = parent_kwargs.get('perm_code', None)

            # class support call check | only class check
            cls_auth_check = AuthPermission(
                view_this=self,
                request=request,
                allow_admin_tenant=allow_admin_tenant, allow_admin_company=allow_admin_company,
                use_custom_get_filter_auth=use_custom_get_filter_auth,
                plan_code=plan_code, app_code=app_code, perm_code=perm_code,
            )

            # always check once call | pk, user, employee,...
            true_or_resp = cls_auth_check.always_check(
                self_kwargs=self.kwargs,
                login_require=login_require,
                employee_require=employee_require,
                auth_require=auth_require,
            )
            if isinstance(true_or_resp, Response):
                return true_or_resp
            if true_or_resp is not True:
                raise ValueError("always_check() don't return type: dict or response: " + str(type(true_or_resp)))

            # check by pass with flag admin
            # check auth permission require | verify from data input
            filter_or_resp = cls_auth_check.auth_check(auth_require=auth_require)
            if isinstance(filter_or_resp, Response):
                return filter_or_resp
            if not isinstance(filter_or_resp, dict):
                raise ValueError("auth_check() don't return type: dict or response: " + str(type(filter_or_resp)))
            self.filter_dict = filter_or_resp

            # call view when access login and auth permission | Data returned is three case:
            #   1. ValidateError from valid --> convert to HTTP 400
            #   2. Exception another: Return 500 with msg is errors
            #   3. Tuple: (data, status)
            try:
                view_return = func_view(self, request, *args, **kwargs)  # --> {'user_list': user_list}
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
            except Exception as err:
                if settings.DEBUG is True:
                    print(f'Error on line {sys.exc_info()[-1].tb_lineno} with {str(err)}')
                return ResponseController.internal_server_error_500(msg=str(err))
            raise ValueError('Return not map happy case.')

        return wraps(func_view)(wrapper)

    return decorated

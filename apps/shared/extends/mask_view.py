from functools import wraps

import rest_framework.exceptions
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse

from rest_framework import status, serializers
from rest_framework.response import Response

from .controllers import ResponseController
from .utils import TypeCheck
from ..translations import ServerMsg

__all__ = ['mask_view']


class AuthPermission:
    def __init__(self, user, code_perm):
        self.user = user
        self.code_perm = code_perm

    def check(self):
        if not self.user or isinstance(self.user, AnonymousUser):
            print(f'[AuthPermission][check] {ServerMsg.VERIFY_AUTH_REQUIRE_USER}')
            return False
        return True

    def check_obj(self, obj, code_perm=None):
        if code_perm is None:
            code_perm = self.code_perm
        if obj and code_perm:
            return True
        return False

    def check_objs(self, objs, code_perm=None):
        if code_perm is None:
            code_perm = self.code_perm
        for obj in objs:
            if not self.check_obj(obj, code_perm):
                return False
        return True


def mask_view(**parent_kwargs):
    # login_require: default True
    # auth_require: default False
    # code_perm = default None
    if not isinstance(parent_kwargs, dict):
        parent_kwargs = {}

    def decorated(func_view):
        def wrapper(self, request, *args, **kwargs):  # pylint: disable=R0911,R0912
            # check pk in url is UUID
            if 'pk' in self.kwargs and not TypeCheck.check_uuid(self.kwargs['pk']):
                return ResponseController.notfound_404()

            # get user in request
            user = request.user
            if not request.user or isinstance(request.user, AnonymousUser):
                user = None

            # get require key check
            login_require = parent_kwargs.get('login_require', True)
            auth_require = parent_kwargs.get('auth_require', False)
            if auth_require:
                login_require = True

            # check login_require | check user in request is exist and not Anonymous
            if login_require and (not user or user.is_authenticated is False or user.is_anonymous is True):
                return ResponseController.unauthorized_401()

            # check auth permission require | verify from data input
            code_perm = parent_kwargs.get('code_perm', None)
            if auth_require and not AuthPermission(user=user, code_perm=code_perm).check():
                return ResponseController.forbidden_403()

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
            except Exception as err:
                if settings.DEBUG is True:
                    print(err)
                return ResponseController.internal_server_error_500(msg=str(err))
            raise ValueError('Return not map happy case.')

        return wraps(func_view)(wrapper)

    return decorated

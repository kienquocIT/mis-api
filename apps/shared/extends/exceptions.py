import sys
import traceback
import json
import logging

from django.conf import settings
from rest_framework import exceptions
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from .response import ConvertErrors
from .push_notify import TeleBotPushNotify

logger = logging.getLogger()


def get_exception_handler_opts(context):
    return {
        'LIST_CONVERT_TO': getattr(context['view'], 'LIST_CONVERT_TO', 'STR'),  # 'FIRST', 'LIST_STR', 'STR'
        'LIST_STR_JOIN_CHAR': getattr(context['view'], 'LIST_STR_JOIN_CHAR', '. '),
        'DATA_ALWAYS_LIST': getattr(context['view'], 'DATA_ALWAYS_LIST', False),  # "a" => ["a"]
    }


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, exceptions.AuthenticationFailed):
        response.data = {
            **response.data,
            'auth_error_code': exc.get_codes()
        }

    if response is not None:
        errors = ConvertErrors(opts=get_exception_handler_opts(context)).convert(response.data, response.status_code)
        if settings.DEBUG_PERMIT:
            print('[custom_exception_handler] errors:', errors)
        response.data = errors
    return response


class Empty200(APIException):
    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail, code=code)


def handle_exception_all_view(_err, self):
    def get_user_id():
        if self.request.user and hasattr(self.request.user, 'id'):
            return self.request.user.id
        return ''

    def get_remote_address():
        ip_address = [self.request.META.get('REMOTE_ADDR')]
        ip_forward = self.request.META.get('HTTP_X_FORWARDED_FOR', self.request.META.get('REMOTE_ADDR'))
        if ip_forward:
            ip_address += ip_forward.split(',')

    def get_headers():
        headers = {**self.request.headers}
        if 'Authorization' in headers:
            headers['Authorization'] = '**hidden**'
        return headers

    data = traceback.format_exception(*sys.exc_info(), limit=None, chain=True)
    err_msg = "".join(json.loads(json.dumps(data).replace("\n", "").replace("^", "")))
    if settings.DEBUG is True:
        print(err_msg)
    else:
        logger.error(
            'URL: %s | USER_ID: %s - %s | METHOD: %s | ERR: %s | ERR_MSG: %s',
            str(self.request.path),
            str(get_user_id()),
            str(self.request.user),
            str(self.request.method),
            str(err_msg),
            str(_err),
        )
    msg = TeleBotPushNotify.generate_msg(
        idx='500',
        status='CRITICAL',
        group_name='SERVER_EXCEPTION',
        **{
            'user': f'{str(get_user_id())} - {str(self.request.user)}',
            'view': str(self.request.resolver_match.view_name),
            'url': f'{str(self.request.method)} : {str(self.request.path)}',
            'query_params': str(self.request.query_params.dict()),
            'headers': str(get_headers()),
            'ip_address': str(get_remote_address()),
            'body': str(self.request.data),
            'err': str(_err),
            'err_msg': str(err_msg),
        }
    )
    TeleBotPushNotify().send_msg(msg=msg)

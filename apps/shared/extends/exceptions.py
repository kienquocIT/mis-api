import sys
import traceback
import json
import logging

from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from .response import convert_errors
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

    if response is not None:
        response.data = convert_errors(response.data, response.status_code, get_exception_handler_opts(context))
    return response


class Empty200(APIException):
    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail, code=code)


def handle_exception_all_view(_err, self):
    def get_user_id():
        if self.request.user and hasattr(self.request.user, 'id'):
            return self.request.user.id
        return ''

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
            'url': str(self.request.path),
            'user_id': str(get_user_id()),
            'user': str(self.request.user),
            'request_method': str(self.request.method),
            'err_msg': str(err_msg),
            'err': str(_err),
        }
    )
    TeleBotPushNotify().send_msg(msg=msg)

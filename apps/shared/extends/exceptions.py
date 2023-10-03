import sys
import traceback
import json
import logging

from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from .response import convert_errors

logger = logging.getLogger()


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = convert_errors(response.data, response.status_code)
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

from rest_framework.views import exception_handler

from .extends import convert_errors


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = convert_errors(response.data, response.status_code)
    return response

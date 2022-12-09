import base64
import json

from django.core.exceptions import PermissionDenied
from django.http import QueryDict
from django.utils.functional import wraps


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def ajax_required(view):
    def wrapper(request, *args, **kwargs):
        if is_ajax(request):
            if request.method in ['POST', 'PUT']:
                body_unicode = request.data['body']
                body_data_base = base64.b64decode(body_unicode).decode('utf-8')
                body_data_loaded = json.loads(body_data_base)
                request.data_parsed = body_data_loaded
            return view(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wraps(view)(wrapper)

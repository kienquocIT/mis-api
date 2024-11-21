from django.utils import translation
from django.http import HttpResponseNotAllowed


class ActiveTranslateAndAllowedMethodMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method not in ['GET', 'POST', 'PUT', 'DELETE']:
            return HttpResponseNotAllowed([])

        if request.user and hasattr(request.user, 'language'):
            translation.activate(request.user.language if request.user.language else 'vi')

        response = self.get_response(request)
        return response

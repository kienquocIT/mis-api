from django.utils import translation


class ActiveTranslateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user and hasattr(request.user, 'language'):
            translation.activate(request.user.language if request.user.language else 'vi')

        response = self.get_response(request)
        return response

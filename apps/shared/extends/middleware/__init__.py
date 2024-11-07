from django.http import HttpResponseNotAllowed


class AllowedMethodMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method not in ['GET', 'POST', 'PUT', 'DELETE']:
            return HttpResponseNotAllowed([])
        response = self.get_response(request)
        return response

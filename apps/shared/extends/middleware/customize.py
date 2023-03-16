from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from jaeger_client import Config


class JaegerTracingMiddleware(MiddlewareMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tracer = None
        if settings.JAEGER_TRACING_ENABLE is True:
            config = Config(
                config={
                    "sampler": {"type": "const", "param": 1},
                    "local_agent": {
                        "reporting_host": settings.JAEGER_TRACING_HOST,
                        "reporting_port": settings.JAEGER_TRACING_PORT,
                    },
                    "logging": True,
                },
                service_name=settings.JAEGER_TRACING_PROJECT_NAME,
            )
            self.tracer = config.initialize_tracer()

    @staticmethod
    def get_view_name(request):
        _name = request.method + ' - '
        if request and hasattr(request, 'resolver_match'):
            resolver_match = request.resolver_match
            if resolver_match and hasattr(resolver_match, 'view_name'):
                return _name + resolver_match.view_name
        return _name + 'GENERAL'

    def __call__(self, request):
        response = self.get_response(request)
        if self.tracer:
            if not request.path.startswith(settings.JAEGER_TRACING_EXCLUDE_LOG_PATH):
                span_ctx = self.tracer.extract(
                    format="http_headers", carrier=request.headers
                )
                view_name = self.get_view_name(request)
                with self.tracer.start_active_span(
                        view_name, child_of=span_ctx
                ) as scope:
                    scope.span.set_tag("http.method", request.method)
                    scope.span.set_tag("http.url", request.build_absolute_uri())
                    scope.span.set_tag("http.status_code", response.status_code)
                    if response.status_code == 500:
                        scope.span.set_tag('error', True)

                        # split Type Error and Message Error
                        err_msg = str(response.content.decode('utf-8'))
                        err_msg = err_msg.split('Request Method:', maxsplit=1)[0].replace("\n", " ")
                        arr_tmp = err_msg.split(" at ")
                        if len(arr_tmp) == 2:
                            scope.span.set_tag('error.kind', arr_tmp[0])
                            scope.span.set_tag('error.object	', arr_tmp[1])
                        else:
                            scope.span.set_tag('message', err_msg)
        return response

# import opentracing
# from jaeger_client import Config
# from opentracing import Tracer
# from opentracing.ext import tags
# from opentracing.propagation import Format
# from django.utils.deprecation import MiddlewareMixin
#
#
# class CustomMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#         self.tracer = self.init_tracer()
#
#     def __call__(self, request):
#         # Tạo một span mới để ghi nhật ký request
#         span_tags = {
#             tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER,
#             tags.HTTP_METHOD: request.method,
#             tags.HTTP_URL: request.build_absolute_uri(),
#         }
#         with self.tracer.start_active_span('django-request', tags=span_tags) as scope:
#             response = self.get_response(request)
#             scope.span.set_tag(tags.HTTP_STATUS_CODE, response.status_code)
#
#         return response
#
#     def init_tracer(self):
#         config = Config(
#             config={
#                 'sampler': {'type': 'const', 'param': 1},
#                 'local_agent': {
#                     'reporting_host': 'localhost',
#                     'reporting_port': 6831,
#                 },
#                 'logging': True,
#             },
#             service_name='PRJ',
#         )
#         return config.initialize_tracer()

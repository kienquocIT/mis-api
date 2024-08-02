import os

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from django.conf import settings


def init():
    if settings.JAEGER_TRACING_ENABLE:
        os.environ['OTEL_PYTHON_DJANGO_EXCLUDED_URLS'] = ",".join(
            [
                'docs/.*', '/docs/.*',
                '__.*',
                'static/.*', '/static/.*',
            ]
        )

        DjangoInstrumentor().instrument()
        LoggingInstrumentor().instrument()

        jaeger_exporter = JaegerExporter(
            agent_host_name=settings.JAEGER_TRACING_HOST,
            agent_port=int(settings.JAEGER_TRACING_PORT),
        )
        trace.set_tracer_provider(
            TracerProvider(
                resource=Resource.create({SERVICE_NAME: settings.JAEGER_TRACING_PROJECT_NAME})
            )
        )
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)

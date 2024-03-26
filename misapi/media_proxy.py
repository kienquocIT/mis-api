import re
from urllib.parse import urlsplit

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.conf import settings
from django.core import exceptions
from django.http import HttpResponseNotFound, HttpResponseForbidden, response
from django.urls import re_path
from django.views.static import serve


def call_serve(request, path, document_root=None, **kwargs):
    try:
        resp = serve(request, path, document_root=document_root, show_indexes=False)
        return resp
    except response.Http404:
        return HttpResponseNotFound()
    except Exception as err:
        print('call_serve:', str(err))
        return HttpResponseForbidden


def proxy_serve_global(request, path, document_root=None, **kwargs):
    return call_serve(request, path, document_root, **kwargs)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def proxy_serve_avatar(request, path, document_root=None, **kwargs):
    if request.user.is_authenticated:
        return call_serve(request, path, document_root, show_indexes=False)
    return HttpResponseForbidden()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def proxy_serve_another(request, path, document_root=None, **kwargs):
    if path.startswith('private/'):
        return HttpResponseNotFound()

    if request.user.is_authenticated:
        return call_serve(request, path, document_root, show_indexes=False)
    return HttpResponseForbidden()


def static(prefix, document_root):
    """
    Return a URL pattern for serving files in debug mode.

    from django.conf import settings
    from django.conf.urls.static import static

    urlpatterns = [
        # ... the rest of your URLconf goes here ...
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    """
    if not prefix:
        raise exceptions.ImproperlyConfigured("Empty static prefix not permitted")
    # if not settings.DEBUG or urlsplit(prefix).netloc:
    #     # No-op if not in debug mode or a non-local prefix.
    #     return []

    prefix_resolver = re.escape(prefix.lstrip("/"))
    return [
        re_path(
            r"^%s(?P<path>public/[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}/global/avatar/.*)$" % prefix_resolver,
            proxy_serve_avatar, kwargs={'document_root': document_root}
        ),
        re_path(
            r"^%s(?P<path>public/[0-9a-f]{12}4[0-9a-f]{3}[89ab][0-9a-f]{15}/global/.*)$" % prefix_resolver,
            proxy_serve_global, kwargs={'document_root': document_root}
        ),
        re_path(
            f"^%s(?P<path>.*)$" % prefix_resolver,
            proxy_serve_another, kwargs={'document_root': document_root}
        ),
    ]

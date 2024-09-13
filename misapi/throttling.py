from django.contrib.auth.models import AnonymousUser
from rest_framework.throttling import SimpleRateThrottle


class AuthThrottle(SimpleRateThrottle):
    scope = 'auth'

    def get_cache_key(self, request, view):
        if request.user and not isinstance(request.user, AnonymousUser):
            ident = str(request.user.pk)
            return self.cache_format % {
                'scope': self.scope,
                'ident': ident
            }
        return None


class AnonThrottle(SimpleRateThrottle):
    scope = 'anon'

    def get_cache_key(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return self.cache_format % {
                'scope': self.scope,
                'ident': request.META['REMOTE_ADDR']
            }
        return None

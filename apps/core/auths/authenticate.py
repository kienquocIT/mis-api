from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.core.cache import cache
from django.utils import translation


class MyCustomJWTAuthenticate(JWTAuthentication):
    def authenticate(self, request):
        # data = super().authenticate(request)
        # if data and isinstance(data, tuple) and isinstance(data[0], self.user_model):
        #     translation.activate(data[0].language if data[0].language else 'vi')
        # return data

        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        user = None
        token = self.get_validated_token(raw_token)
        key_cache = f"{settings.CACHE_KEY_PREFIX}_{token['jti']}"
        if token is not None:
            user = cache.get(key_cache)

        if user is None:
            user = self.get_user(token)
            if user is not None and user.is_active:
                cache.set(key_cache, user, timeout=600)  # cache user for 10 minutes

        if user and token and isinstance(user, self.user_model):
            translation.activate(user.language if user.language else 'vi')
        return user, token


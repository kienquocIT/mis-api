from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from rest_framework_simplejwt.settings import api_settings

from django.utils import translation


class MyCustomJWTAuthenticate(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken("Token contained no recognizable user identification")

        try:
            user = self.user_model.objects.get(
                **{api_settings.USER_ID_FIELD: user_id}, force_cache=True, cache_timeout=60 * 60  # 1 hours
            )
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed("User not found", code="user_not_found")

        if not user.is_active:
            raise AuthenticationFailed("User is inactive", code="user_inactive")

        return user

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        token = self.get_validated_token(raw_token)
        user = self.get_user(token)

        if user and token and isinstance(user, self.user_model):
            translation.activate(user.language if user.language else 'vi')
        return user, token

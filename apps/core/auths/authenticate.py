from django.conf import settings
from django.utils import translation
from rest_framework.exceptions import AuthenticationFailed

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings


class MyCustomJWTAuthenticate(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise AuthenticationFailed("Token contained no recognizable user identification", code="token_no_user_id")

        try:
            user = self.user_model.objects.select_related('employee_current').get(
                **{api_settings.USER_ID_FIELD: user_id},
                force_cache=True, cache_timeout=60 * 60  # 1 hours
            )
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(code="user_not_found")

        if not user.is_active:
            raise AuthenticationFailed(code="user_inactive")

        return user

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            token = self.get_validated_token(raw_token)
        except InvalidToken:
            raise AuthenticationFailed(code="token_failure")

        user = self.get_user(token)

        # from rest_framework_simplejwt.tokens import UntypedToken
        # xsource = request.headers.get('X-Source', '')
        # device_id = request.headers.get('Device-ID', '')
        # print('Device-ID:', device_id)

        url_excludes = [
            '/api/auth/2fa',
        ]

        if user and token and isinstance(user, self.user_model):
            is_2fa_verified = token.payload.get(settings.JWT_KEY_2FA_VERIFIED, None)
            if user.auth_locked_out is True:
                # deny when locked out
                is_2fa_state = False
            else:
                if settings.SYNC_2FA_ENABLED is False:
                    # skip 2FA checking
                    is_2fa_state = True
                elif user.auth_2fa is True:
                    # state by token key
                    is_2fa_state = is_2fa_verified is True
                else:
                    # not lock, not auth -> auto True
                    is_2fa_state = True
            request.is_2fa_verified = is_2fa_verified
            request.is_2fa_enable = user.auth_2fa
            request.is_2fa_state = is_2fa_state

            if is_2fa_state is True or (is_2fa_state is False and request.path in url_excludes):
                if settings.DEBUG_PERMIT:
                    print('active language [authenticate]:', user.language if user.language else 'vi', user, user.id)
                translation.activate(user.language if user.language else 'vi')
            else:
                if settings.DEBUG_PERMIT:
                    print('auth 2fa failed:', request.path, token.payload)
                raise AuthenticationFailed(code='authentication_2fa_failed')
        return user, token

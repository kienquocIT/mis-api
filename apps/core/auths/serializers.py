from django.conf import settings
from django.contrib.auth.models import update_last_login
from slugify import slugify
from rest_framework import serializers
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.core.tenant.models import Tenant
from apps.shared import translations as trans, ServerMsg
from apps.core.account.models import User
from apps.shared.translations import AuthMsg


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        # ...

        return token

    @classmethod
    def get_full_token(cls, user):
        data = {}

        refresh = super().get_token(user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if getattr(settings, 'UPDATE_LAST_LOGIN', True):
            update_last_login(None, user)

        return data


class AuthLoginSerializer(Serializer):  # noqa
    tenant_code = serializers.CharField(max_length=15)
    username = serializers.SlugField(max_length=100)
    password = serializers.CharField(max_length=None)

    @classmethod
    def validate_tenant_code(cls, attrs):
        tenant = Tenant.objects.filter(code=attrs)
        match tenant.count():
            case 0:
                err_msg = AuthMsg.TENANT_NOT_FOUND.format(attrs)
            case 1:
                return tenant.first()
            case _:
                err_msg = AuthMsg.TENANT_RETURN_MULTIPLE.format(attrs)
        raise serializers.ValidationError({'tenant_code': err_msg})

    @classmethod
    def validate_username(cls, attrs):
        username_slugify = slugify(attrs)
        if username_slugify == attrs:
            return username_slugify
        raise serializers.ValidationError(AuthMsg.USERNAME_OR_PASSWORD_INCORRECT)

    @classmethod
    def validate_password(cls, attrs):
        return attrs

    def validate(self, attrs):
        try:
            username_value = User.convert_username_field_data(attrs['username'], attrs['tenant_code'])
            user_obj = User.objects.get(**{User.USERNAME_FIELD: username_value})
            if user_obj:
                if user_obj.check_password(attrs['password']):
                    return user_obj
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': AuthMsg.USERNAME_OR_PASSWORD_INCORRECT})
        except Exception:
            raise serializers.ValidationError({'detail': ServerMsg.UNDEFINED_ERR})

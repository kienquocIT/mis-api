import re

from django.conf import settings
from django.contrib.auth.models import update_last_login
from slugify import slugify
from rest_framework import serializers
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.core.tenant.models import Tenant
from apps.core.company.models import Company, CompanyUserEmployee
from apps.shared import ServerMsg, AccountMsg
from apps.core.account.models import User
from apps.shared.translations import AuthMsg


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):  # pylint: disable=W0223  # noqa
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


class AuthLoginSerializer(Serializer):  # pylint: disable=W0223 # noqa
    tenant_code = serializers.CharField(max_length=15)
    username = serializers.SlugField(max_length=100)
    password = serializers.CharField(max_length=None)

    @classmethod
    def validate_tenant_code(cls, attrs):
        code = attrs.lower()
        tenant = Tenant.objects.filter(code=code)
        match tenant.count():
            case 0:
                err_msg = AuthMsg.TENANT_NOT_FOUND.format(code)
            case 1:
                return tenant.first()
            case _:
                err_msg = AuthMsg.TENANT_RETURN_MULTIPLE.format(code)
        raise serializers.ValidationError({'tenant_code': err_msg})

    @classmethod
    def validate_username(cls, attrs):
        username = attrs.lower()
        username_slugify = slugify(username)
        if username_slugify == username:
            return username_slugify
        raise serializers.ValidationError({"username": AuthMsg.USERNAME_OR_PASSWORD_INCORRECT})

    @classmethod
    def validate_password(cls, attrs):
        return attrs

    def validate(self, attrs):
        try:
            username_value = User.convert_username_field_data(attrs['username'], attrs['tenant_code'])
            user_obj = User.objects.select_related(
                'tenant_current', 'company_current', 'employee_current', 'space_current',
            ).get(**{User.USERNAME_FIELD: username_value})
            if user_obj:
                if user_obj.check_password(attrs['password']):
                    return user_obj
                raise User.DoesNotExist()
            raise serializers.ValidationError({'detail': AuthMsg.USERNAME_OR_PASSWORD_INCORRECT})
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': AuthMsg.USERNAME_OR_PASSWORD_INCORRECT})
        except Exception as err:
            print(err)
            raise serializers.ValidationError({'detail': ServerMsg.UNDEFINED_ERR})


class SwitchCompanySerializer(Serializer):  # pylint: disable=W0223 # noqa
    company = serializers.UUIDField()

    @classmethod
    def validate_company(cls, attrs):
        if attrs:
            try:
                company_obj = Company.objects.get(pk=attrs)
                return company_obj
            except Company.DoesNotExist:
                pass
        raise serializers.ValidationError({"company": AccountMsg.COMPANY_NOT_EXIST})

    def validate(self, attrs):
        # user_obj = get_current_user()
        user_obj = self.context.get('user_obj', None)
        if user_obj:
            company_obj = attrs['company']
            if user_obj and company_obj:
                try:
                    obj = CompanyUserEmployee.objects.get(company=company_obj, user=user_obj)
                    attrs['user'] = user_obj
                    attrs['company_user_employee'] = obj
                    return attrs
                except CompanyUserEmployee.DoesNotExist:
                    pass
            raise serializers.ValidationError({"detail": AccountMsg.COMPANY_NOT_EXIST})
        raise serializers.ValidationError({"detail": AccountMsg.USER_NOT_EXIST})


class AuthValidAccessCodeSerializer(serializers.Serializer):  # noqa
    company_id = serializers.UUIDField()
    access_id = serializers.UUIDField()
    user_agent = serializers.CharField()
    public_ip = serializers.CharField()


class MyLanguageUpdateSerializer(serializers.ModelSerializer):
    @classmethod
    def validate_language(cls, attrs):
        if attrs and attrs in dict(settings.LANGUAGE_CHOICE):
            return attrs
        raise serializers.ValidationError(
            {
                'language': AuthMsg.LANGUAGE_NOT_SUPPORT,
            }
        )

    def update(self, instance, validated_data):
        language = validated_data['language']
        instance.language = language
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('language',)


class ChangePasswordSerializer(serializers.Serializer):  # noqa
    current_password = serializers.CharField(min_length=6)
    new_password = serializers.CharField(min_length=6)
    new_password_again = serializers.CharField(min_length=6)

    def validate_current_password(self, attrs):
        if self.instance and hasattr(self.instance, 'check_password'):
            if self.instance.check_password(attrs):
                return attrs
        raise serializers.ValidationError(
            {
                'current_password': AuthMsg.PASSWORD_IS_INCORRECT
            }
        )

    @staticmethod
    def check_new_password(data) -> bool:
        if data:
            if len(data) >= 6:
                has_digit = re.search(r"\d", data)
                has_uppercase = re.search(r"[A-Z]", data)
                has_special_char = re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?~]', data)

                true_counter = 0
                for item in [has_digit, has_uppercase, has_special_char]:
                    if item:
                        true_counter += 1

                if true_counter >= 2:
                    return True
        return False

    @classmethod
    def validate_new_password(cls, attrs):
        if cls.check_new_password(attrs):
            return attrs
        raise serializers.ValidationError(
            {
                'new_password': AuthMsg.PASSWORD_REQUIRED_CHARACTERS
            }
        )

    @classmethod
    def validate_new_password_again(cls, attrs):
        if cls.check_new_password(attrs):
            return attrs
        raise serializers.ValidationError(
            {
                'new_password_again': AuthMsg.PASSWORD_REQUIRED_CHARACTERS
            }
        )

    def validate(self, attrs):
        old_pass = attrs['current_password']
        new_pass = attrs['new_password']
        new_pass_again = attrs['new_password_again']
        if new_pass == new_pass_again:
            if old_pass != new_pass:
                return attrs
            raise serializers.ValidationError(
                {
                    'new_password': AuthMsg.PASSWORD_NEW_NOT_SAME_CURRENT_PASSWORD,
                }
            )
        raise serializers.ValidationError(
            {
                'new_password_again': AuthMsg.PASSWORD_NOT_SAME_PASSWORD_AGAIN
            }
        )

    def update(self, instance, validated_data):
        new_password = validated_data['new_password']
        instance.set_password(new_password)
        instance.save()
        return instance

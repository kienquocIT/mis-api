import re
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import update_last_login
from django.utils import timezone
from slugify import slugify
from rest_framework import serializers
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.core.tenant.models import Tenant
from apps.core.company.models import Company, CompanyUserEmployee
from apps.shared import ServerMsg, AccountMsg
from apps.core.account.models import User, ValidateUser
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


class ValidateUserDetailSerializer(serializers.ModelSerializer):
    push_notify_data = serializers.SerializerMethodField()

    @classmethod
    def get_push_notify_data(cls, obj):
        state, name_service, destination_data = obj.push_notify_data()

        def mask_destination():
            def mask_name(_name):
                if len(_name) > 5:
                    return _name[:3] + "*" * (len(_name) - 4) + _name[-1]
                if len(_name) > 3:
                    return _name[:3] + "*" * (len(_name) - 3)
                if len(_name) > 0:
                    return _name[:1] + "*" * (len(_name) - 3)
                return ''

            if name_service == 'E-Mail':
                name_email, *remainder = destination_data.split("@")

                def mask_mail_host(_host_name):
                    return "@".join([mask_name(item) for item in _host_name])
                return f'{mask_name(name_email)}@{mask_mail_host(remainder)}'

            if name_service == 'SMS':
                return mask_name(destination_data)

            return ''

        if state:
            return {
                'name_service': name_service if name_service else '',
                'destination': mask_destination(),
            }
        return {}

    user_data = serializers.SerializerMethodField()

    @classmethod
    def get_user_data(cls, obj):
        def get_avatar():
            if obj.user.employee_current:
                emp_obj = obj.user.employee_current
                if hasattr(emp_obj, 'avatar_img') and emp_obj.avatar_img:
                    return emp_obj.avatar_img.url if emp_obj.avatar_img else None
            return None

        if obj.user:
            return {
                'full_name': obj.user.get_full_name(),
                'avatar': get_avatar(),
            }
        return {}

    class Meta:
        model = ValidateUser
        fields = ('id', 'date_expires', 'user_data', 'push_notify_data')


class ForgotPasswordGetOTPSerializer(serializers.ModelSerializer):
    tenant_code = serializers.CharField()
    username = serializers.CharField()

    @classmethod
    def validate_tenant_code(cls, attrs):
        try:
            return Tenant.objects.get(code=attrs)
        except Tenant.DoesNotExist:
            pass
        raise serializers.ValidationError(
            {
                'tenant_code': AuthMsg.TENANT_NOT_FOUND.format(str(attrs))
            }
        )

    def validate(self, attrs):
        username = attrs['username']
        tenant_obj = attrs['tenant_code']
        if username and tenant_obj:
            try:
                user_obj = User.objects.get(tenant_current=tenant_obj, username=username)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        'username': AuthMsg.USER_DOES_NOT_EXIST
                    }
                )
            last_call = ValidateUser.objects.filter(
                user=user_obj, date_created__gte=timezone.now() - timedelta(hours=1)
            ).count()
            if last_call > 5:
                raise serializers.ValidationError(
                    {
                        'detail': AuthMsg.MAX_REQUEST_FORGOT.format('5', '1')
                    }
                )
            return {
                **attrs,
                'user_obj': user_obj
            }
        raise serializers.ValidationError(
            {
                'username': AuthMsg.USERNAME_REQUIRE
            }
        )

    class Meta:
        model = ValidateUser
        fields = ('tenant_code', 'username')

    def create(self, validated_data):
        user_obj = validated_data['user_obj']
        otp = ValidateUser.generate_otp()

        return ValidateUser.objects.create(
            user=user_obj,
            otp=otp,
            date_expires=ValidateUser.generate_expire(minutes=2)
        )


class SubmitOTPSerializer(serializers.ModelSerializer):
    otp = serializers.CharField()

    def validate_otp(self, attrs):
        if self.instance.otp == attrs:
            return attrs
        raise serializers.ValidationError({'otp': AuthMsg.OTP_NOT_MATCH})

    def update(self, instance, validated_data):
        instance.is_valid = True
        instance.save(update_fields=['is_valid'])
        return instance

    class Meta:
        model = ValidateUser
        fields = ('otp',)

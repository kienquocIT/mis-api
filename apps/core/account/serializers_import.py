import re

from django.utils.text import slugify
from rest_framework import serializers

from apps.core.account.models import User
from apps.core.company.models import CompanyUserEmployee, Company
from apps.shared import AccountMsg


class UserImportReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name')


class UserImportSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)

    @classmethod
    def validate_username(cls, attrs):
        attrs = attrs.lower()
        username_slugify = slugify(attrs)
        if username_slugify != attrs:
            raise serializers.ValidationError({'username': AccountMsg.USERNAME_MUST_BE_SLUGIFY_STRING})

        if User.objects.filter_current(
                username=username_slugify,
                fill__tenant=True, fill__map_key={'fill__tenant': 'tenant_current_id'}
        ).exists():
            raise serializers.ValidationError({'username': AccountMsg.USERNAME_EXISTS})
        return username_slugify

    password = serializers.CharField(max_length=128, allow_blank=True)

    @classmethod
    def validate_password(cls, attrs):
        num_count = sum(1 for char in attrs if char.isnumeric())
        alpha_count = sum(1 for char in attrs if char.isalpha())
        if num_count == 0 or alpha_count == 0:
            raise serializers.ValidationError({"password": AccountMsg.VALID_PASSWORD})
        return attrs

    email = serializers.EmailField(max_length=150, allow_blank=True, allow_null=True)
    phone = serializers.CharField(max_length=25, allow_blank=True, allow_null=True)

    @classmethod
    def validate_phone(cls, attrs):
        if attrs:
            regex = r"""^((\+84)|0)([35789]|1[2389])([0-9]{8})$"""
            pattern = re.compile(regex)
            if pattern.match(attrs):
                return attrs
            raise serializers.ValidationError({"phone": AccountMsg.PHONE_FORMAT_VN_INCORRECT})
        return None

    def create(self, validated_data):
        tenant = self.context.get('tenant_current', None)
        company = self.context.get('company_current', None)
        user_obj = self.context.get('user_obj', None)
        if (
                company and hasattr(company, 'id')  # pylint: disable=R0916
                and user_obj and hasattr(user_obj, 'id') and hasattr(user_obj, 'tenant_current_id')
                and tenant and hasattr(tenant, 'id')
        ):
            tenant_current_id = getattr(tenant, 'id', None)
            company_current_id = getattr(company, 'id', None)
            if tenant_current_id and company_current_id:
                password = validated_data.pop("password")

                # create user
                validated_data['tenant_current_id'] = tenant_current_id
                validated_data['company_current_id'] = company_current_id
                obj = User.objects.create(**validated_data)

                # create linked between user and employee
                CompanyUserEmployee.create_new(company_id=company.id, user_id=obj.id)

                # refresh total user of company
                company.total_user = Company.refresh_total_user(ids=[company.id])

                # update password and re-save
                obj.set_password(password)
                obj.save()
                return obj
        raise serializers.ValidationError(
            {
                'detail': AccountMsg.COMPANY_NOT_EXIST
            }
        )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'password',
            'phone',
            'email',
        )

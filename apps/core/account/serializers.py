from rest_framework import serializers

from apps.core.account.models import User
from apps.core.company.models import Company


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    # tenant_current = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
            'username',
            'email',
            'phone',
            # 'tenant_current'
        )

    @classmethod
    def get_full_name(cls, obj):
        return User.get_full_name(obj, 2)

    # def get_tenant_current(self, obj):
    #     if obj.tenant_current:
    #         return {
    #             'id': obj.tenant_current_id,
    #             'title': obj.tenant_current.title,
    #             'code': obj.tenant_current.code
    #         }
    #     return {}


class UserUpdateSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=50, allow_null=True, allow_blank=True)
    email = serializers.EmailField(max_length=150, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone',
            'company_current'
        )

    @classmethod
    def validate_phone(cls, attrs):
        if not attrs.isnumeric():
            raise serializers.ValidationError("phone number does not contain characters")
        return attrs


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, allow_blank=True)
    email = serializers.EmailField(max_length=150, allow_blank=True, allow_null=True)
    username = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'password',
            'phone',
            'company_current',
            'email',
        )

    @classmethod
    def validate_password(cls, attrs):
        # uppercase_count = sum(1 for char in attrs if char.isupper())
        # lower_count = sum(1 for char in attrs if char.isupper())
        num_count = sum(1 for char in attrs if char.isnumeric())
        # if uppercase_count == 0:
        #     raise serializers.ValidationError("Password must contain upper letters")
        # if lower_count == 0:
        #     raise serializers.ValidationError("Password must contain character")
        if num_count == 0:
            raise serializers.ValidationError("Password must contain number")
        return attrs

    @classmethod
    def validate_phone(cls, attrs):
        if not attrs.isnumeric():
            raise serializers.ValidationError("phone number does not contain characters")
        return attrs

    def create(self, validated_data):
        obj = User.objects.create(**validated_data)
        password = validated_data.pop("password")
        obj.set_password(password)
        obj.save()
        return obj


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
            'company',
            'email',
            'username',
            'company_current_id',
            'phone',
            'tenant_current',
        )

    @classmethod
    def get_full_name(cls, obj):
        return User.get_full_name(obj, 2)

    @classmethod
    def get_company(cls, obj):
        companies = []
        company = Company.object_normal.filter(pk=obj.company_current_id)
        for item in company:
            companies.append({
                'code': item.code,
                'title': item.title,
                'representative': item.representative_fullname,
                'license': ['Sale', 'Hr'],
            })
        return companies

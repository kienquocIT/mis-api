from rest_framework import serializers

from apps.core.account.models import User
from apps.core.company.models import Company, CompanyUserEmployee
from apps.core.hr.models import Employee
from apps.shared.decorators import query_debugger


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
        company = CompanyUserEmployee.object_normal.filter(user_id=obj.id)
        for item in company:
            try:
                co = Company.object_normal.get(pk=item.company_id)
                companies.append({
                'code': co.code,
                'title': co.title,
                'representative': co.representative_fullname,
                })
            except Exception as err:
                pass
        return companies


class CompanyUserDetailSerializer(serializers.ModelSerializer):
    companies = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'company_current',
            'companies',
        )

    @classmethod
    def get_companies(cls, obj):
        company_user = CompanyUserEmployee.object_normal.filter(user_id=obj.id)
        companies = []
        for item in company_user:
            try:
                company = Company.object_normal.get(id=item.company_id)
                companies.append({
                    'id': company.id,
                    'name': company.title,
                })
            except Exception as err:
                raise serializers.ValidationError("Company does not exist.")
        return companies


class CompanyUserUpdateSerializer(serializers.ModelSerializer):
    companies = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False,
    )

    class Meta:
        model = User
        fields = (
            'companies',
        )

    @query_debugger
    def update(self, instance, validated_data):
        if 'companies' in validated_data:
            user_companies = CompanyUserEmployee.object_normal.filter(user_id=instance)
            user_companies = [i.company_id for i in user_companies]
            user_companies.remove(instance.company_current_id)

            data_bulk = validated_data.pop('companies')
            data_bulk.remove(instance.company_current_id)

            list_add_company = data_bulk.copy()
            list_update_company = list(set(user_companies.copy()))

            bulk_info = []
            for company in data_bulk:
                if company in user_companies:
                    list_update_company.remove(company)
                    list_add_company.remove(company)

            for co in list_update_company:
                co_old = CompanyUserEmployee.object_normal.filter(user=instance, company_id=co).first()
                if co_old:
                    try:
                        emp = Employee.object_normal.get(pk=co_old.employee_id)
                        emp.user_id = None
                        emp.save()
                    except Exception as err:
                        pass
                    co_old.delete()
                try:
                    co_obj = Company.object_normal.get(id=co)
                    co_obj.total_user = co_obj.total_user - 1
                    co_obj.save()
                except Exception as err:
                    raise AttributeError("Company not exists")

            for company in list_add_company:
                try:
                    co_obj = Company.object_normal.get(id=company)
                    co_obj.total_user = co_obj.total_user + 1
                    co_obj.save()
                except Exception as err:
                    raise AttributeError("Company not exists")
                bulk_info.append(CompanyUserEmployee(company_id=company, user_id=instance.id))

            if bulk_info:
                CompanyUserEmployee.object_normal.bulk_create(bulk_info)

            if CompanyUserEmployee.object_normal.filter(user_id=instance.id).count() > 1:
                instance.save(is_superuser=True)
            else:
                instance.save()
            return instance

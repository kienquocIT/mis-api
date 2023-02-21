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

    @query_debugger
    def update(self, instance, validated_data):
        if 'company_current' in validated_data:
            data_bulk = validated_data['company_current']
            if data_bulk != instance.company_current:
                co_user_emp = list(CompanyUserEmployee.object_normal.filter(user=instance))
                if len(co_user_emp) == 1:
                    if co_user_emp[0].employee:
                        co_user_emp[0].employee.company = data_bulk
                        co_user_emp[0].employee.save()

                    co_user_emp[0].company = data_bulk
                    co_user_emp[0].save()

                    instance.company_current.total_user -= 1
                    instance.company_current.save()

                    data_bulk.total_user += 1
                    data_bulk.save()
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()
        return instance


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
            bulk_info_add = []
            remove_list = []
            company_id_list = validated_data['companies']
            company_old_id_list = CompanyUserEmployee.object_normal.filter(
                user=instance
            ).exclude(
                company_id=instance.company_current_id
            ).values_list(
                'company_id',
                flat=True
            )
            # check add
            for company_id in company_id_list:
                if company_id != instance.company_current_id:
                    if company_id not in company_old_id_list:
                        bulk_info_add.append(CompanyUserEmployee(
                            company_id=company_id,
                            user_id=instance.id)
                        )
            # check remove
            for company_old_id in company_old_id_list:
                if company_old_id not in company_id_list:
                    remove_list.append(company_old_id)
            if bulk_info_add:
                company_user_add = CompanyUserEmployee.object_normal.bulk_create(bulk_info_add)
                if company_user_add:
                    for company_add in company_user_add:
                        company_add.company.total_user += 1
                        company_add.company.save()
            if remove_list:
                company_user_remove = CompanyUserEmployee.object_normal.filter(
                    company_id__in=remove_list,
                    user=instance
                ).select_related(
                    'employee',
                    'company'
                )
                if company_user_remove:
                    for data_remove in company_user_remove:
                        if data_remove.employee:
                            data_remove.employee.user = None
                            data_remove.employee.save()
                            data_remove.delete()

                            if data_remove.company.total_user > 0:
                                data_remove.company.total_user -= 1
                                data_remove.company.save()
                        else:
                            if data_remove.company.total_user > 0:
                                data_remove.company.total_user -= 1
                                data_remove.company.save()
                            data_remove.delete()

            if len(company_old_id_list) != 0:
                if len(company_old_id_list) == len(remove_list):
                    instance.save()
            else:
                if len(bulk_info_add) > 0:
                    instance.save(is_superuser=True)
        return instance

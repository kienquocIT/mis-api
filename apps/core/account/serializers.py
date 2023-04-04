from crum import get_current_user
from rest_framework import serializers

from apps.core.account.models import User
from apps.core.company.models import Company, CompanyUserEmployee
from apps.shared import AccountMsg


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

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
        )

    @classmethod
    def get_full_name(cls, obj):
        return User.get_full_name(obj, 2)


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
            raise serializers.ValidationError(AccountMsg.PHONE_CONTAIN_CHARACTER)
        return attrs

    def update(self, instance, validated_data):
        """
            if user is employee and only in 1 company (line 57)
            -> move employee + user in new company
        """

        if 'company_current' in validated_data:
            data_bulk = validated_data['company_current']
            if data_bulk != instance.company_current:
                co_user_emp = CompanyUserEmployee.objects.select_related(
                    'employee'
                ).filter(
                    user=instance
                )
                if co_user_emp.exclude(
                    employee=None
                ) == 1:
                    if co_user_emp[0].employee:
                        co_user_emp[0].employee.company = data_bulk
                        co_user_emp[0].employee.save()

                    co_user_emp[0].company = data_bulk
                    co_user_emp[0].save()

                if len(co_user_emp) == 1:
                    instance.company_current.total_user -= 1
                    instance.company_current.save()

                    data_bulk.total_user += 1
                    data_bulk.save()
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()
            return instance

        raise serializers.ValidationError(AccountMsg.USER_DATA_VALID)


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
        num_count = sum(1 for char in attrs if char.isnumeric())
        alpha_count = sum(1 for char in attrs if char.isalpha())
        if num_count == 0 or alpha_count == 0:
            raise serializers.ValidationError(AccountMsg.VALID_PASSWORD)
        return attrs

    @classmethod
    def validate_phone(cls, attrs):
        if not attrs.isnumeric():
            raise serializers.ValidationError(AccountMsg.PHONE_CONTAIN_CHARACTER)
        return attrs

    def create(self, validated_data):
        user_obj = get_current_user()
        if user_obj and getattr(user_obj, 'tenant_current_id', None):
            validated_data['tenant_current_id'] = user_obj.tenant_current_id
        obj = User.objects.create(**validated_data)
        company = validated_data['company_current']
        company.total_user = CompanyUserEmployee.objects.filter(
            company_id=validated_data['company_current']
        ).count() + 1
        company.save()
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
        # Reminds: Adding clean ref to TABLE_REF (apps.shared.Caching)
        # When using prefetch_related in MAIN QUERY + CACHED IT
        #   - Remarks: When on change CompanyUserEmployee then system clean cache of CompanyUserEmployee, auto clean
        #   cache of ref table
        # if we don't use prefetch_relate, we use query ModelM2M.objects.filter(...).cache()
        #   --> This way is slow first time but so fast next time.
        return [{
            "id": x.id,
            "title": x.title,
            "code": x.code,
            "representative": x.representative_fullname,
        } for x in obj.companies.all()]


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
        company_user = CompanyUserEmployee.objects.filter(user_id=obj.id)
        companies = []
        for item in company_user:
            try:
                company = Company.objects.get(id=item.company_id)
                companies.append(
                    {
                        'id': company.id,
                        'name': company.title,
                    }
                )
            except Company.DoesNotExist as exc:
                raise serializers.ValidationError(AccountMsg.COMPANY_NOT_EXIST) from exc
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

    @classmethod
    def get_company_list_added(cls, instance, company_id_list, company_old_id_list):
        bulk_info_add = []
        for company_id in company_id_list:
            if company_id != instance.company_current_id:
                if company_id not in company_old_id_list:
                    bulk_info_add.append(
                        CompanyUserEmployee(
                            company_id=company_id,
                            user_id=instance.id
                        )
                    )
        return bulk_info_add

    @classmethod
    def add_company(cls, bulk_info_add):
        if bulk_info_add:
            company_user_add = CompanyUserEmployee.objects.bulk_create(bulk_info_add)
            if company_user_add:
                for company_add in company_user_add:
                    company_add.company.total_user += 1
                    company_add.company.save()

    @classmethod
    def get_company_list_delete(cls, company_id_list, company_old_id_list):
        remove_list = []
        for company_old_id in company_old_id_list:
            if company_old_id not in company_id_list:
                remove_list.append(company_old_id)
        return remove_list

    @classmethod
    def delete_user(cls, instance, remove_list):
        if remove_list:
            company_user_remove = CompanyUserEmployee.objects.filter(
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

    def update(self, instance, validated_data):
        if 'companies' in validated_data:
            company_id_list = validated_data['companies']
            company_old_id_list = CompanyUserEmployee.objects.filter(
                user=instance
            ).exclude(
                company_id=instance.company_current_id
            ).values_list(
                'company_id',
                flat=True
            )
            # add company for user
            bulk_info_add = self.get_company_list_added(instance, company_id_list, company_old_id_list)
            self.add_company(bulk_info_add)
            # remove user
            remove_list = self.get_company_list_delete(company_id_list, company_old_id_list)
            self.delete_user(instance, remove_list)

            num_company = CompanyUserEmployee.objects.filter(user=instance).count()

            if num_company > 1:
                instance.save(is_superuser=True)
            else:
                instance.save()

            return instance
        raise serializers.ValidationError(AccountMsg.USER_DATA_VALID)

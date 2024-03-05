from crum import get_current_user
from rest_framework import serializers

from apps.core.account.models import User
from apps.core.company.models import Company, CompanyUserEmployee
from apps.shared import AccountMsg


class UserListTenantOverviewSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    company_list = serializers.SerializerMethodField()
    employee_mapped = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'full_name',
            'company_list',
            'employee_mapped',
        )

    @classmethod
    def get_full_name(cls, obj):
        return User.get_full_name(obj, 2)

    @classmethod
    def get_company_list(cls, obj):
        return [
            str(x.company_id) for x in obj.company_user_employee_set_user.all()
        ]

    @classmethod
    def get_employee_mapped(cls, obj):
        return {
            str(x.company_id): (str(x.employee_id) if x.employee_id else None)
            for x in obj.company_user_employee_set_user.all()
        }


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
            'is_admin_tenant',
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
            'company_current',
            'is_admin_tenant',
        )

    @classmethod
    def validate_phone(cls, attrs):
        if not attrs.isnumeric():
            raise serializers.ValidationError({"phone": AccountMsg.PHONE_CONTAIN_CHARACTER})
        return attrs

    def update(self, instance, validated_data):
        if 'company_current' in validated_data:
            data_bulk = validated_data['company_current']
            if data_bulk != instance.company_current:
                list_company_user_emp = CompanyUserEmployee.objects.select_related(
                    'employee', 'company'
                ).filter(
                    user=instance
                )
                company_user_bulk = list_company_user_emp.filter(company=data_bulk).first()
                company_user_instance = list_company_user_emp.filter(company=instance.company_current).first()

                if company_user_bulk:
                    if company_user_bulk.employee is None:
                        if company_user_instance.employee is not None:
                            company_user_instance.employee.company = data_bulk
                            company_user_instance.employee.save()

                            company_user_bulk.employee = company_user_instance.employee
                            company_user_instance.employee = None

                    company_user_bulk.is_created_company = True
                    company_user_bulk.save()

                    company_user_instance.is_created_company = False
                    company_user_instance.save()
                else:
                    if company_user_instance.employee:
                        company_user_instance.employee.company = data_bulk
                        company_user_instance.employee.save()

                    company_user_instance.company = data_bulk
                    company_user_instance.save()

                    instance.company_current.total_user -= 1
                    instance.company_current.save()

                    data_bulk.total_user += 1
                    data_bulk.save()

            for key, value in validated_data.items():
                setattr(instance, key, value)
            if instance.is_superuser:
                instance.save(is_superuser=True)
            else:
                instance.save()
            return instance
        raise serializers.ValidationError({"detail": AccountMsg.USER_DATA_VALID})


class UserResetPasswordSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField()

    def validate(self, attrs):
        if attrs['password'] == attrs['re_password']:
            return attrs
        raise serializers.ValidationError({
            'detail': AccountMsg.VALID_PASSWORD
        })

    def update(self, instance, validated_data):
        password = validated_data['password']
        instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = (
            'password',
            're_password',
        )


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
    def validate_username(cls, attrs):
        if User.objects.filter_current(
                username=attrs,
                fill__tenant=True, fill__map_key={'fill__tenant': 'tenant_current_id'}
        ).exists():
            raise serializers.ValidationError({'username': AccountMsg.USERNAME_EXISTS})
        return attrs

    @classmethod
    def validate_password(cls, attrs):
        num_count = sum(1 for char in attrs if char.isnumeric())
        alpha_count = sum(1 for char in attrs if char.isalpha())
        if num_count == 0 or alpha_count == 0:
            raise serializers.ValidationError({"password": AccountMsg.VALID_PASSWORD})
        return attrs

    @classmethod
    def validate_phone(cls, attrs):
        if not attrs.isnumeric():
            raise serializers.ValidationError({"phone": AccountMsg.PHONE_CONTAIN_CHARACTER})
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
            'is_active',
            'is_admin_tenant',
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
            except Company.DoesNotExist:
                raise serializers.ValidationError({'companies': AccountMsg.COMPANY_NOT_EXIST})
        return companies


class CompanyUserEmployeeUpdateSerializer(serializers.ModelSerializer):
    companies = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False,
    )

    def validate_companies(self, attrs):
        if self.instance and isinstance(attrs, list):
            objs = Company.objects.filter(id__in=attrs)
            if len(objs) == len(attrs):
                return objs
            raise serializers.ValidationError({'companies': AccountMsg.COMPANY_NOT_EXIST})
        raise serializers.ValidationError({'companies': AccountMsg.USER_DATA_VALID})

    class Meta:
        model = User
        fields = (
            'companies',
        )

    @classmethod
    def get_change_companies(cls, objs_old, objs_new):
        ids_old = {str(x) for x in objs_old.values_list('id', flat=True)}
        ids_new = {str(x) for x in objs_new.values_list('id', flat=True)}
        # return (remove, add)
        return list(ids_old - ids_new), list(ids_new - ids_old), list(ids_old & ids_new)

    @classmethod
    def get_objs(cls, ids, objs):
        result = []
        for obj in objs:
            if str(obj.id) in ids:
                result.append(obj)
        return result

    def update(self, instance, validated_data):
        # update CompanyUserEmployee
        companies_old = self.instance.companies.all()
        companies_new = validated_data['companies']
        ids_remove, ids_add, ids_same = self.get_change_companies(companies_old, companies_new)

        CompanyUserEmployee.remove_company_from_user(instance.id, company_ids=ids_remove)
        CompanyUserEmployee.add_company_to_user(instance.id, company_ids=ids_add)

        # update total user of company
        Company.refresh_total_user(ids_remove + ids_add)

        # update company_current of user if process need
        if instance.company_current_id in ids_remove:
            if ids_same:
                instance.company_current_id = ids_same[0]
                instance.save(update_fields=['company_current_id'])

        # return user obj
        return instance

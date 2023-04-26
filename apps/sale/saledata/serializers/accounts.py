from rest_framework import serializers
from apps.core.hr.models import Employee
from apps.sale.saledata.models.accounts import (
    Salutation, Interest, AccountType, Industry, Contact, Account, AccountEmployee
)
from apps.shared import HRMsg, AccountsMsg


# Salutation
class SalutationListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Salutation
        fields = ('id', 'title', 'code', 'description')


class SalutationCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Salutation
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_code(cls, value):
        if Salutation.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
        return value

    @classmethod
    def validate_title(cls, value):
        if Salutation.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


class SalutationDetailSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Salutation
        fields = ('id', 'title', 'code', 'description')


class SalutationUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Salutation
        fields = ('title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and Salutation.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


# Interest
class InterestsListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Interest
        fields = ('id', 'title', 'code', 'description')


class InterestsCreateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Interest
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_code(cls, value):
        if Interest.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
        return value

    @classmethod
    def validate_title(cls, value):
        if Interest.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


class InterestsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ('id', 'title', 'code', 'description')


class InterestsUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Interest
        fields = ('title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and Interest.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


# Account Type
class AccountTypeListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = AccountType
        fields = ('id', 'title', 'code', 'description')


class AccountTypeCreateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = AccountType
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_code(cls, value):
        if AccountType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
        return value

    @classmethod
    def validate_title(cls, value):
        if AccountType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


class AccountTypeDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountType
        fields = ('id', 'title', 'code', 'description')


class AccountTypeUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = AccountType
        fields = ('title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and AccountType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


# Industry
class IndustryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ('id', 'title', 'code', 'description')


class IndustryCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Industry
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_code(cls, value):
        if Industry.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
        return value

    @classmethod
    def validate_title(cls, value):
        if Industry.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


class IndustryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ('id', 'title', 'code', 'description')


class IndustryUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Industry
        fields = ('title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and Industry.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


# Contact
class ContactListSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    account_name = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            'id',
            'fullname',
            'job_title',
            'owner',
            'account_name',
            'mobile',
            'email'
        )

    @classmethod
    def get_owner(cls, obj):
        if obj.owner:
            owner = Employee.objects.filter(
                id=obj.owner
            ).first()
            if owner:
                return {
                    'id': obj.owner,
                    'fullname': owner.get_full_name(2)
                }
        raise serializers.ValidationError({"owner": HRMsg.EMPLOYEES_NOT_EXIST})

    @classmethod
    def get_account_name(cls, obj):
        if obj.account_name:
            return {
                'id': obj.account_name_id,
                'name': obj.account_name.name
            }
        return {}


class ContactCreateSerializer(serializers.ModelSerializer):
    account_name = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Contact
        fields = (
            "owner",
            "job_title",
            "biography",
            "avatar",
            "fullname",
            "salutation",
            "phone",
            "mobile",
            "email",
            "report_to",
            "address_information",
            "additional_information",
            'account_name'
        )

    @classmethod
    def validate_account_name(cls, attrs):
        if attrs is not None:
            account = Account.objects.filter(
                id=attrs
            ).first()
            if account:
                return account
        raise serializers.ValidationError({"account_name": AccountsMsg.ACCOUNT_NOT_EXIST})

    @classmethod
    def validate_email(cls, attrs):
        if attrs is not None:
            if Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    email=attrs,
            ).exists():
                raise serializers.ValidationError({"email": AccountsMsg.EMAIL_EXIST})
            return attrs
        return None

    @classmethod
    def validate_mobile(cls, attrs):
        if attrs is not None:
            if Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    mobile=attrs,
            ).exists():
                raise serializers.ValidationError({"mobile": AccountsMsg.MOBILE_EXIST})
            return attrs
        return None


class ContactDetailSerializer(serializers.ModelSerializer):
    salutation = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    report_to = serializers.SerializerMethodField()
    additional_information = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    account_name = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            "id",
            "owner",
            "job_title",
            "biography",
            "avatar",
            "fullname",
            "salutation",
            "phone",
            "mobile",
            "email",
            "report_to",
            "address_information",
            "additional_information",
            "account_name"
        )

    @classmethod
    def get_salutation(cls, obj):
        if obj.salutation:
            return {
                'id': obj.salutation_id,
                'title': obj.salutation.title
            }
        return {}

    @classmethod
    def get_owner(cls, obj):
        if obj.owner:
            owner = Employee.objects.filter(
                id=obj.owner
            ).first()
            if owner:
                return {
                    'id': obj.owner,
                    'fullname': owner.get_full_name(2)
                }
        raise serializers.ValidationError({"owner": HRMsg.EMPLOYEES_NOT_EXIST})

    @classmethod
    def get_report_to(cls, obj):
        if obj.report_to:
            owner = Contact.objects.filter(
                id=obj.report_to
            ).first()
            if owner:
                return {
                    'id': obj.report_to,
                    'fullname': owner.fullname
                }
        return {}

    @classmethod
    def get_additional_information(cls, obj):
        if obj.additional_information:
            interest_list = []
            interest_id_list = list(obj.additional_information.get('interests', None))
            interest = Interest.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id__in=interest_id_list
            )
            if interest:
                for item in interest:
                    interest_list.append(
                        {
                            'id': item.id,
                            'title': item.title
                        }
                    )
            obj.additional_information['interests'] = interest_list
            return obj.additional_information
        return {}

    @classmethod
    def get_fullname(cls, obj):
        if obj.fullname:
            return {
                'fullname': obj.fullname,
                'last_name': obj.fullname.split(' ')[-1],
                'first_name': ' '.join(obj.fullname.split(' ')[:-1])
            }
        return {}

    @classmethod
    def get_account_name(cls, obj):
        if obj.account_name:
            return {
                "id": obj.account_name_id,
                "name": obj.account_name.name
            }
        return {}


class ContactUpdateSerializer(serializers.ModelSerializer):
    account_name = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Contact
        fields = (
            "owner",
            "job_title",
            "biography",
            "avatar",
            "fullname",
            "salutation",
            "phone",
            "mobile",
            "email",
            "report_to",
            "address_information",
            "additional_information",
            'account_name'
        )

    @classmethod
    def validate_account_name(cls, value):
        if value is not None:
            account = Account.objects.filter(
                id=value
            ).first()
            if account:
                return account
        raise serializers.ValidationError({"account_name": AccountsMsg.ACCOUNT_NOT_EXIST})

    def validate_email(self, attrs):
        if attrs is not None:
            if attrs != self.instance.email and Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    email=attrs,
            ).exists():
                raise serializers.ValidationError({"email": AccountsMsg.EMAIL_EXIST})
            return attrs
        return None

    def validate_mobile(self, attrs):
        if attrs is not None:
            if attrs != self.instance.mobile and Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    mobile=attrs,
            ).exists():
                raise serializers.ValidationError({"mobile": AccountsMsg.MOBILE_EXIST})
            return attrs
        return None

    def update(self, instance, validated_data):
        if 'account_name' not in validated_data.keys():
            validated_data.update({'account_name': None})

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance


class ContactListNotMapAccountSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            'id',
            'fullname',
            'job_title',
            'owner',
            'mobile',
            'phone',
            'email'
        )

    @classmethod
    def get_owner(cls, obj):
        if obj.owner:
            owner = Employee.objects.filter(
                id=obj.owner
            ).first()
            if owner:
                return {
                    'id': obj.owner,
                    'fullname': owner.get_full_name(2)
                }
        raise serializers.ValidationError({"owner": HRMsg.EMPLOYEES_NOT_EXIST})


# Account
class AccountListSerializer(serializers.ModelSerializer):
    account_type = serializers.SerializerMethodField()
    manager = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            "id",
            "name",
            "website",
            "account_type",
            "manager",
            "owner",
            "phone",
        )

    @classmethod
    def get_account_type(cls, obj):
        if obj.account_type:
            all_account_types = [account_type.get('title', None) for account_type in obj.account_type]
            return all_account_types
        return []

    @classmethod
    def get_manager(cls, obj):
        if obj.manager:
            return obj.manager
        return []

    @classmethod
    def get_owner(cls, obj):
        owner = Contact.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            account_name=obj,
            is_primary=True
        ).first()
        if owner:
            return {
                'id': owner.id,
                'fullname': owner.fullname
            }
        return {}


class AccountCreateSerializer(serializers.ModelSerializer):
    contact_select_list = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False
    )
    contact_primary = serializers.UUIDField(required=False)
    parent_account = serializers.UUIDField(required=False, allow_null=True)
    name = serializers.CharField(max_length=150)
    code = serializers.CharField(max_length=150)
    account_type = serializers.JSONField()

    class Meta:
        model = Account
        fields = (
            'name',
            'code',
            'website',
            'account_type',
            'manager',
            'parent_account',
            'tax_code',
            'industry',
            'annual_revenue',
            'total_employees',
            'phone',
            'email',
            'shipping_address',
            'billing_address',
            'contact_select_list',
            'contact_primary'
        )

    @classmethod
    def validate_code(cls, value):
        if Account.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
        return value

    def validate(self, validate_data):
        account_types = []
        for item in validate_data.get('account_type', None):
            account_type = AccountType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id=item
            ).first()
            if account_type:
                title = account_type.title
                code = account_type.code
                detail = ''
                tax_code = validate_data.get('tax_code', None)
                if title.lower() == 'customer':
                    detail = self.initial_data.get('customer_type', None)
                    if detail == 'organization':
                        if tax_code is None:
                            raise serializers.ValidationError(AccountsMsg.TAX_CODE_NOT_NONE)
                if tax_code is not None:
                    account_map_tax_code = Account.objects.filter_current(
                        fill__tenant=True,
                        fill__company=True,
                        tax_code=tax_code,
                    ).first()
                    if account_map_tax_code:
                        raise serializers.ValidationError(AccountsMsg.TAX_CODE_IS_EXIST)
                account_types.append({'id': str(item), 'code': code, 'title': title, 'detail': detail})
            else:
                raise serializers.ValidationError(AccountsMsg.ACCOUNTTYPE_NOT_EXIST)
        validate_data['account_type'] = account_types
        return validate_data

    def create(self, validated_data):
        """
        step 1: contact_select_list: get list contact selected
        step 2: get primary contact
        step 3: contact_select_list = contact_select_list append primary contact
        step 4: update is_primary in which id == primary
        """
        contact_select_list = None
        contact_primary = None
        if 'contact_select_list' in validated_data:
            contact_select_list = validated_data.get('contact_select_list', None)
            del validated_data['contact_select_list']
        if 'contact_primary' in validated_data:
            contact_primary = validated_data.get('contact_primary', None)
            del validated_data['contact_primary']

        # create account
        account = Account.objects.create(**validated_data)

        # create in AccountEmployee
        bulk_info = []
        manager_field = []
        get_employees = Employee.objects.filter_current(fill__tenant=True, fill__company=True, id__in=account.manager)
        for employee in get_employees:
            bulk_info.append(AccountEmployee(**{'account': account, 'employee': employee}))
            manager_field.append(
                {'id': str(employee.id), 'code': employee.code, 'fullname': employee.get_full_name(2)}
            )
        account.manager = manager_field
        account.save()

        AccountEmployee.objects.bulk_create(bulk_info)

        # update contact select
        if contact_primary:
            contact_select_list.append(contact_primary)
        if contact_select_list:
            contact_list = Contact.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id__in=contact_select_list
            )
            if contact_list:
                for contact in contact_list:
                    if contact.id == contact_primary:
                        contact.is_primary = True
                    contact.account_name = account
                    contact.save()
        return account


class AccountDetailSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    contact_mapped = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
            'name',
            'code',
            'website',
            'account_type',
            'manager',
            'parent_account',
            'tax_code',
            'industry',
            'annual_revenue',
            'total_employees',
            'phone',
            'email',
            'shipping_address',
            'billing_address',
            'owner',
            'contact_mapped'
        )

    @classmethod
    def get_owner(cls, obj):
        account_owner = Contact.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            account_name=obj,
            is_primary=True
        ).first()
        if account_owner:
            contact_owner = Employee.objects.filter(
                id=account_owner.owner
            ).first()

            if contact_owner:
                contact_owner_information = {'id': str(account_owner.owner), 'fullname': contact_owner.get_full_name(2)}
                return {
                    'id': account_owner.id,
                    'fullname': account_owner.fullname,
                    'job_title': account_owner.job_title,
                    'email': account_owner.email,
                    'mobile': account_owner.mobile,
                    'owner': contact_owner_information
                }
            else:
                raise serializers.ValidationError({"owner": HRMsg.EMPLOYEES_NOT_EXIST})
        return {}

    @classmethod
    def get_contact_mapped(cls, obj):
        contact_mapped = Contact.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            account_name=obj
        )
        if len(contact_mapped) > 0:
            list_contact_mapped = []
            for i in contact_mapped:
                list_contact_mapped.append(
                    {
                        'id': i.id,
                        'fullname': i.fullname,
                        'job_title': i.job_title,
                        'email': i.email,
                        'mobile': i.mobile
                    }
                )
            return list_contact_mapped
        return []


def recreate_employee_map_account(instance):
    bulk_info = []
    instance_manager_field = []
    get_employees = Employee.objects.filter_current(fill__tenant=True, fill__company=True, id__in=instance.manager)
    for employee in get_employees:
        bulk_info.append(AccountEmployee(**{'account': instance, 'employee': employee}))
        instance_manager_field.append(
            {'id': str(employee.id), 'code': employee.code, 'fullname': employee.get_full_name(2)}
        )
    instance.manager = instance_manager_field
    instance.save()
    AccountEmployee.objects.filter(account=instance).delete()
    AccountEmployee.objects.bulk_create(bulk_info)
    return True


def update_account_owner(instance, account_owner):
    if account_owner:
        Contact.objects.filter_current(fill__tenant=True, fill__company=True, id=account_owner).update(
            account_name=instance,
            is_primary=True
        )
    Contact.objects.filter_current(fill__tenant=True, fill__company=True, account_name=instance).update(
        account_name=None,
        is_primary=False
    )
    return True


class AccountUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=150)
    account_type = serializers.JSONField()
    parent_account = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Account
        fields = (
            'name',
            'website',
            'account_type',
            'manager',
            'parent_account',
            'tax_code',
            'industry',
            'annual_revenue',
            'total_employees',
            'phone',
            'email',
            'shipping_address',
            'billing_address',
        )

    def validate(self, validate_data):
        account_types = []
        for item in validate_data.get('account_type', None):
            account_type = AccountType.objects.filter_current(fill__tenant=True, fill__company=True, id=item).first()
            if account_type:
                detail = self.initial_data.get('customer_detail_type', '')
                account_types.append(
                    {'id': str(item), 'code': account_type.code, 'title': account_type.title, 'detail': detail}
                )
                if detail == 'organization':  # tax_code is required
                    tax_code = validate_data.get('tax_code', None)
                    if tax_code:
                        account_mapped_tax_code = Account.objects.filter_current(
                            fill__tenant=True,
                            fill__company=True,
                            tax_code=tax_code
                        ).first()
                        if account_mapped_tax_code and account_mapped_tax_code != self.instance:
                            raise serializers.ValidationError(AccountsMsg.TAX_CODE_IS_EXIST)
                    else:
                        raise serializers.ValidationError(AccountsMsg.TAX_CODE_NOT_NONE)
                elif detail == 'individual':
                    validate_data.update({'parent_account': None})
            else:
                raise serializers.ValidationError(AccountsMsg.ACCOUNTTYPE_NOT_EXIST)
        validate_data['account_type'] = account_types
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        update_account_owner(instance, self.initial_data.get('account-owner', None))  # update account owner
        recreate_employee_map_account(instance)  # recreate in AccountEmployee (Account Manager)
        return instance


class AccountsMapEmployeesListSerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField()

    class Meta:
        model = AccountEmployee
        fields = (
            'id',
            'employee',
            'account',
        )

    @classmethod
    def get_account(cls, obj):
        return {
            'id': obj.account_id,
            'name': obj.account.name
        }

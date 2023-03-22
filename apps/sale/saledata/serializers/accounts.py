import string
from rest_framework import serializers
from apps.core.hr.models import Employee
from apps.sale.saledata.models.accounts import (
    Salutation, Interest, AccountType, Industry, Contact, Account, AccountEmployee
)
from apps.shared import HRMsg
from apps.shared.translations.accounts import AccountsMsg


# Salutation
class SalutationListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Salutation
        fields = ('id', 'title', 'code', 'description')


class SalutationCreateSerializer(serializers.ModelSerializer):

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
            raise serializers.ValidationError(AccountsMsg.CODE_EXIST)
        return value

    @classmethod
    def validate_title(cls, value):
        if Salutation.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError(AccountsMsg.NAME_EXIST)
        return value


class SalutationDetailSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Salutation
        fields = ('id', 'title', 'code', 'description')


class SalutationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salutation
        fields = ('title', 'code', 'description')

    def validate_code(self, value):
        if value != self.instance.code and Salutation.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError(AccountsMsg.CODE_EXIST)
        return value

    def validate_title(self, value):
        if value != self.instance.title and Salutation.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError(AccountsMsg.NAME_EXIST)
        return value


# Interest
class InterestsListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Interest
        fields = ('id', 'title', 'code', 'description')


class InterestsCreateSerializer(serializers.ModelSerializer):  # noqa
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
            raise serializers.ValidationError(AccountsMsg.CODE_EXIST)
        return value

    @classmethod
    def validate_title(cls, value):
        if Interest.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError(AccountsMsg.NAME_EXIST)
        return value


class InterestsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ('id', 'title', 'code', 'description')


class InterestsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ('title', 'code', 'description')

    def validate_code(self, value):
        if value != self.instance.code and Interest.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError(AccountsMsg.CODE_EXIST)
        return value

    def validate_title(self, value):
        if value != self.instance.title and Interest.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError(AccountsMsg.NAME_EXIST)
        return value


# Account Type
class AccountTypeListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = AccountType
        fields = ('id', 'title', 'code', 'description')


class AccountTypeCreateSerializer(serializers.ModelSerializer):  # noqa
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
            raise serializers.ValidationError(AccountsMsg.CODE_EXIST)
        return value

    @classmethod
    def validate_title(cls, value):
        if AccountType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError(AccountsMsg.NAME_EXIST)
        return value


class AccountTypeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ('id', 'title', 'code', 'description')


class AccountTypeUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountType
        fields = ('title', 'code', 'description')

    def validate_code(self, value):
        if value != self.instance.code and AccountType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError(AccountsMsg.CODE_EXIST)
        return value

    def validate_title(self, value):
        if value != self.instance.title and AccountType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError(AccountsMsg.NAME_EXIST)
        return value


# Industry
class IndustryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ('id', 'title', 'code', 'description')


class IndustryCreateSerializer(serializers.ModelSerializer):
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
            raise serializers.ValidationError(AccountsMsg.CODE_EXIST)
        return value

    @classmethod
    def validate_title(cls, value):
        if Industry.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError(AccountsMsg.NAME_EXIST)
        return value


class IndustryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ('id', 'title', 'code', 'description')


class IndustryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ('title', 'code', 'description')

    def validate_code(self, value):
        if value != self.instance.code and Industry.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError(AccountsMsg.CODE_EXIST)
        return value

    def validate_title(self, value):
        if value != self.instance.title and Industry.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError(AccountsMsg.NAME_EXIST)
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
        try:
            if obj.owner:
                owner = Employee.objects.get(id=obj.owner)
                return {
                    'id': obj.owner,
                    'fullname': owner.get_full_name(2)
                }
        except Employee.DoesNotExist as exc:
            raise serializers.ValidationError(HRMsg.EMPLOYEES_NOT_EXIST) from exc
        return {}

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
            'account_name',
        )

    @classmethod
    def validate_account_name(cls, attrs):
        try:
            if attrs is not None:
                return Account.objects.get(id=attrs)
        except Account.DoesNotExist as exc:
            raise serializers.ValidationError(AccountsMsg.ACCOUNT_NOT_EXIST) from exc
        return None

    @classmethod
    def validate_email(cls, attrs):
        if attrs is not None:
            if Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    email=attrs,
            ).exists():
                raise serializers.ValidationError(AccountsMsg.EMAIL_EXIST)
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
                raise serializers.ValidationError(AccountsMsg.MOBILE_EXIST)
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
        try:
            if obj.owner:
                owner = Employee.objects.get(id=obj.owner)
                return {
                    'id': obj.owner,
                    'fullname': owner.get_full_name(2)
                }
        except Employee.DoesNotExist as exc:
            raise serializers.ValidationError(HRMsg.EMPLOYEES_NOT_EXIST) from exc
        return {}

    @classmethod
    def get_report_to(cls, obj):
        try:
            if obj.report_to:
                owner = Contact.objects.get(id=obj.report_to)
                return {
                    'id': obj.report_to,
                    'fullname': owner.fullname
                }
        except Contact.DoesNotExist as exc:
            raise serializers.ValidationError(AccountsMsg.CONTACT_NOT_EXIST) from exc
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
        try:
            if value is not None:
                return Account.objects.get(id=value)
        except Account.DoesNotExist as exc:
            raise serializers.ValidationError(AccountsMsg.ACCOUNT_NOT_EXIST) from exc
        return None

    def validate_email(self, attrs):
        if attrs is not None:
            if attrs != self.instance.email and Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    email=attrs,
            ).exists():
                raise serializers.ValidationError(AccountsMsg.EMAIL_EXIST)
            return attrs
        return None

    def validate_mobile(self, attrs):
        if attrs is not None:
            if attrs != self.instance.mobile and Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    mobile=attrs,
            ).exists():
                raise serializers.ValidationError(AccountsMsg.MOBILE_EXIST)
            return attrs
        return None


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
        try:
            if obj.owner:
                owner = Employee.objects.get(id=obj.owner)
                return {
                    'id': obj.owner,
                    'fullname': owner.get_full_name(2)
                }
        except Employee.DoesNotExist as exc:
            raise serializers.ValidationError(HRMsg.EMPLOYEES_NOT_EXIST) from exc
        return {}


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
            employees = Employee.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id__in=obj.manager,
            )
            all_managers = []
            for employee in employees:
                all_managers.append(employee.get_full_name(2))
            return all_managers
        return []

    @classmethod
    def get_owner(cls, obj):
        owner = Contact.objects.filter(
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
            raise serializers.ValidationError(AccountsMsg.CODE_EXIST)
        return value

    def validate(self, validate_data):
        account_type = []
        for item in validate_data.get('account_type', None):
            title = AccountType.objects.get(id=item).title
            detail = ''
            if title.lower() == 'customer':
                detail = self.initial_data.get('customer_type', None)
            account_type.append({'title': title, 'detail': detail})
        validate_data['account_type'] = account_type
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
        get_employees = Employee.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            id__in=account.manager,
        )
        for employee in get_employees:
            bulk_info.append(
                AccountEmployee(
                    **{
                        'account': account,
                        'employee': employee,
                    }
                )
            )

        AccountEmployee.objects.bulk_create(bulk_info)

        # update contact select
        if contact_primary:
            contact_select_list.append(contact_primary)

        if contact_select_list:
            contact_list = Contact.objects.filter(id__in=contact_select_list)
            if contact_list:
                for contact in contact_list:
                    if contact.id == contact_primary:
                        contact.is_primary = True
                    contact.account_name = account
                    contact.save()
        return account


class AccountDetailSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

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
            'owner'
        )

    @classmethod
    def get_owner(cls, obj):
        try:
            list_owner = []
            resp = Contact.objects.filter(account_name=obj)
            for item in resp:
                list_owner.append(
                    {
                        'id': item.id,
                        'fullname': item.fullname,
                    }
                )
            return list_owner
        except Contact.DoesNotExist as exc:
            raise serializers.ValidationError(AccountsMsg.CONTACT_NOT_EXIST) from exc


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

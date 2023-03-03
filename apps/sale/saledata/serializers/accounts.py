from rest_framework import serializers
from apps.core.hr.models import Employee
from apps.sale.saledata.models.accounts import (Salutation, Interest, AccountType, Industry, Contact, Account)
from django.db.models import Q


# Salutation
class SalutationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salutation
        fields = ('id', 'title', 'code', 'description')


class SalutationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salutation
        fields = ('code', 'title', 'description')


class SalutationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salutation
        fields = ('id', 'title', 'code', 'description')


# Interest
class InterestsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ('id', 'title', 'code', 'description')


class InterestsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ('code', 'title', 'description')


class InterestsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ('id', 'title', 'code', 'description')


# Account Type
class AccountTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ('id', 'title', 'code', 'description')


class AccountTypeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ('code', 'title', 'description')


class AccountTypeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ('id', 'title', 'code', 'description')


# Industry
class IndustryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ('id', 'title', 'code', 'description')


class IndustryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ('code', 'title', 'description')


class IndustryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ('id', 'title', 'code', 'description')


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
                owner = Employee.object_global.get(id=obj.owner)
                return {
                    'id': owner.id,
                    'fullname': Employee.get_full_name(owner, 2)
                }
        except Exception as e:
            print(e)
        return {}

    @classmethod
    def get_account_name(cls, obj):
        if obj.account_name:
            return {'id': obj.account_name.id, 'name': obj.account_name.name}
        return {}


class ContactCreateSerializer(serializers.ModelSerializer):
    account_name = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Contact
        fields = (
            "owner",
            "job_title",
            "bio",
            "avatar",
            "fullname",
            "salutation",
            "phone",
            "mobile",
            "email",
            "report_to",
            "address_infor",
            "additional_infor",
            'account_name'
        )

    def validate_account_name(self, attrs):
        try:
            if attrs is not None:
                return Account.object_normal.get(id=attrs)
            return None
        except Exception as e:
            raise serializers.ValidationError('Account does not exist.')


class ContactDetailSerializer(serializers.ModelSerializer):
    salutation = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    report_to = serializers.SerializerMethodField()
    additional_infor = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    account_name = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            "id",
            "owner",
            "job_title",
            "bio",
            "avatar",
            "fullname",
            "salutation",
            "phone",
            "mobile",
            "email",
            "report_to",
            "address_infor",
            "additional_infor",
            'account_name'
        )

    @classmethod
    def get_salutation(cls, obj):
        if obj.salutation:
            return {'id': obj.salutation_id, 'title': obj.salutation.title}
        return {}

    @classmethod
    def get_owner(cls, obj):
        try:
            if obj.owner:
                owner = Employee.object_global.get(id=obj.owner)
                return {
                    'id': owner.id,
                    'fullname': Employee.get_full_name(owner, 2)
                }
        except Exception as e:
            print(e)
        return {}

    @classmethod
    def get_report_to(cls, obj):
        print(obj.report_to)
        try:
            if obj.report_to:
                owner = Contact.object_normal.get(id=obj.report_to)
                return {
                    'id': owner.id,
                    'fullname': owner.fullname
                }
        except Exception as e:
            print(e)
        return {}

    @classmethod
    def get_additional_infor(cls, obj):
        if obj.additional_infor:
            interest_list = []
            for i in obj.additional_infor.get('interests', None):
                interest_list.append(
                    {
                        'id': Interest.object_normal.get(id=i).id,
                        'title': Interest.object_normal.get(id=i).title
                    }
                )
            obj.additional_infor['interests'] = interest_list
            return obj.additional_infor
        return []

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
            return {"id": obj.account_name_id, 'name': obj.account_name.name}
        return {}


class ContactUpdateSerializer(serializers.ModelSerializer):
    account_name = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Contact
        fields = (
            "owner",
            "job_title",
            "bio",
            "avatar",
            "fullname",
            "salutation",
            "phone",
            "mobile",
            "email",
            "report_to",
            "address_infor",
            "additional_infor",
            'account_name'
        )

    def validate_account_name(self, value):
        try:
            if value is not None:
                return Account.object_normal.get(id=value)
            return None
        except Exception as e:
            raise serializers.ValidationError('Account does not exist.')


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
                owner = Employee.object_global.get(id=obj.owner)
                return {
                    'id': owner.id,
                    'fullname': Employee.get_full_name(owner, 2)
                }
        except Exception as e:
            print(e)
        return {}


# Account
class AccountListSerializer(serializers.ModelSerializer):
    account_type = serializers.SerializerMethodField()
    industry = serializers.SerializerMethodField()
    manager = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            "id",
            "name",
            "website",
            "account_type",
            "manager",
            "industry",
            "phone",
        )

    @classmethod
    def get_account_type(cls, obj):
        if obj.account_type:
            all_account_types = [account_type.get('title', None) for account_type in obj.account_type]
            return all_account_types
        return []

    @classmethod
    def get_industry(cls, obj):
        if obj.industry:
            return obj.industry.title
        return []

    @classmethod
    def get_manager(cls, obj):
        if obj.manager:
            all_managers = [Employee.object_normal.get(id=employees_id).get_full_name() for employees_id in obj.manager]
            return all_managers
        return []


class ContactSubCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = (
            'owner',
            'fullname'
        )


class AccountCreateSerializer(serializers.ModelSerializer):
    contact_select_list = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False
    )
    contact_create_list = ContactSubCreateSerializer(
        many=True,
        required=False
    )
    contact_primary = serializers.UUIDField(required=False)

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
            'contact_create_list',
            'contact_primary'
        )

    def validate(self, validate_data):
        account_type = []
        for item in validate_data.get('account_type', None):
            title = AccountType.object_normal.get(id=item).title
            detail = ''
            if title.lower() == 'customer':
                detail = self.initial_data.get('customer_type', None)
            account_type.append({'title': title, 'detail': detail})
        validate_data['account_type'] = account_type
        return validate_data

    def create(self, validated_data):
        contact_select_list = None # [..............]
        contact_primary = None
        if 'contact_select_list' in validated_data:
            contact_select_list = validated_data.get('contact_select_list', None)
            del validated_data['contact_select_list']
        if 'contact_primary' in validated_data:
            contact_primary = validated_data.get('contact_primary', None)
            del validated_data['contact_primary']

        # create account
        account = Account.object_normal.create(**validated_data)

        # update contact select
        if contact_select_list:
            if contact_primary:
                contact_select_list.append(contact_primary)
            contact_list = Contact.object_normal.filter(id__in=contact_select_list)
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
        fields = "__all__"

    @classmethod
    def get_owner(cls, obj):
        list_owner = []
        resp = Contact.object_normal.filter(account_name=obj)
        for item in resp:
            list_owner.append({
                'id': item.id,
                'fullname': item.fullname,
            })
        return list_owner


class AccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class EmployeeMapAccountListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    account = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = (
            'id',
            'full_name',
            'account',
        )

    @classmethod
    def get_full_name(cls, obj):
        return Employee.get_full_name(obj, 2)

    def get_account(self, obj):
        account_list = Account.object_normal.filter(Q(manager__contains=[str(obj.id)]))
        id_list = []
        name_list = []
        for account in account_list:
            id_list.append(account.id)
            name_list.append(account.name)
        return {'name': name_list, 'id': id_list}

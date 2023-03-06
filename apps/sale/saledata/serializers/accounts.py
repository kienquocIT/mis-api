from django.db.models import Q
from rest_framework import serializers
from apps.core.hr.models import Employee
from apps.sale.saledata.models.accounts import (
    Salutation, Interest, AccountType, Industry, Contact, Account
)


# Salutation
class SalutationListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Salutation
        fields = ('id', 'title', 'code', 'description')


class SalutationCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Salutation
        fields = ('code', 'title', 'description')

    def validate_code(self, value):
        if Salutation.object_normal.filter(code=value).exists():
            raise serializers.ValidationError("Code is already exist.")
        return value

    def validate_title(self, value):
        if Salutation.object_normal.filter(title=value).exists():
            raise serializers.ValidationError("Name is already exist.")
        return value


class SalutationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salutation
        fields = ('id', 'title', 'code', 'description')


class SalutationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salutation
        fields = ('title', 'code', 'description')

    def validate_code(self, value):
        if value != self.instance.code and Salutation.object_normal.filter(code=value).exists():
            raise serializers.ValidationError("Code is already exist.")
        return value

    def validate_title(self, value):
        if value != self.instance.title and Salutation.object_normal.filter(title=value).exists():
            raise serializers.ValidationError("Name is already exist.")
        return value


# Interest
class InterestsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ('id', 'title', 'code', 'description')


class InterestsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ('code', 'title', 'description')

    def validate_code(self, value):
        if Interest.object_normal.filter(code=value).exists():
            raise serializers.ValidationError("Code is already exist.")
        return value

    def validate_title(self, value):
        if Interest.object_normal.filter(title=value).exists():
            raise serializers.ValidationError("Name is already exist.")
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
        if value != self.instance.code and Interest.object_normal.filter(code=value).exists():
            raise serializers.ValidationError("Code is already exist.")
        return value

    def validate_title(self, value):
        if value != self.instance.title and Interest.object_normal.filter(title=value).exists():
            raise serializers.ValidationError("Name is already exist.")
        return value


# Account Type
class AccountTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ('id', 'title', 'code', 'description')


class AccountTypeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ('code', 'title', 'description')

    def validate_code(self, value):
        if AccountType.object_normal.filter(code=value).exists():
            raise serializers.ValidationError("Code is already exist.")
        return value

    def validate_title(self, value):
        if value != self.instance.title and AccountType.object_normal.filter(title=value).exists():
            raise serializers.ValidationError("Name is already exist.")
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
        if value != self.instance.code and AccountType.object_normal.filter(code=value).exists():
            raise serializers.ValidationError("Code is already exist.")
        return value

    def validate_title(self, value):
        if value != self.instance.title and AccountType.object_normal.filter(title=value).exists():
            raise serializers.ValidationError("Name is already exist.")
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

    def validate_code(self, value):
        if Industry.object_normal.filter(code=value).exists():
            raise serializers.ValidationError("Code is already exist.")
        return value

    def validate_title(self, value):
        if Industry.object_normal.filter(title=value).exists():
            raise serializers.ValidationError("Name is already exist.")
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
        if value != self.instance.code and Industry.object_normal.filter(code=value).exists():
            raise serializers.ValidationError("Code is already exist.")
        return value

    def validate_title(self, value):
        if value != self.instance.title and Industry.object_normal.filter(title=value).exists():
            raise serializers.ValidationError("Name is already exist.")
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
                owner = Employee.object_global.get(id=obj.owner)
                return {
                    'id': owner.id,
                    'fullname': Employee.get_full_name(owner, 2)
                }
        except Employee.DoesNotExist:
            pass
        return {}

    @classmethod
    def get_account_name(cls, obj):
        try:
            if obj.account_name:
                return {
                    'id': obj.account_name.id,
                    'name': obj.account_name.name
                }
        except Account.DoesNotExist:
            pass
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
        except Account.DoesNotExist:
            pass
        return None

    def validate_email(self, attrs):
        if attrs is not None:
            if Contact.object_normal.filter(email=attrs).exists():
                raise serializers.ValidationError("Email is already exist.")
            return attrs
        return ''

    def validate_phone(self, attrs):
        if attrs is not None:
            if Contact.object_normal.filter(phone=attrs).exists():
                raise serializers.ValidationError("Phone is already exist.")
            return attrs
        return ''

    def validate_mobile(self, attrs):
        if attrs is not None:
            if Contact.object_normal.filter(mobile=attrs).exists():
                raise serializers.ValidationError("Mobile is already exist.")
            return attrs
        return ''


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
        try:
            if obj.salutation:
                return {
                    'id': obj.salutation_id,
                    'title': obj.salutation.title
                }
        except Salutation.DoesNotExist:
            pass
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
        except Employee.DoesNotExist:
            pass
        return {}

    @classmethod
    def get_report_to(cls, obj):
        try:
            if obj.report_to:
                owner = Contact.object_normal.get(id=obj.report_to)
                return {
                    'id': owner.id,
                    'fullname': owner.fullname
                }
        except Contact.DoesNotExist:
            pass
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
        try:
            if obj.account_name:
                return {
                    "id": obj.account_name_id,
                    'name': obj.account_name.name
                }
        except Account.DoesNotExist:
            pass
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
        except Account.DoesNotExist:
            pass
        return None

    def validate_email(self, attrs):
        if attrs is not None:
            if attrs != self.instance.email and Contact.object_normal.filter(email=attrs).exists():
                raise serializers.ValidationError("Email is already exist.")
            return attrs
        return ''

    def validate_phone(self, attrs):
        if attrs is not None:
            if attrs != self.instance.phone and Contact.object_normal.filter(phone=attrs).exists():
                raise serializers.ValidationError("Phone is already exist.")
            return attrs
        return ''

    def validate_mobile(self, attrs):
        if attrs is not None:
            if attrs != self.instance.mobile and Contact.object_normal.filter(mobile=attrs).exists():
                raise serializers.ValidationError("Mobile is already exist.")
            return attrs
        return ''


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
        except Employee.DoesNotExist:
            pass
        return {}


# Account
class AccountListSerializer(serializers.ModelSerializer):
    account_type = serializers.SerializerMethodField()
    industry = serializers.SerializerMethodField()
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
            "industry",
            "phone",
        )

    @classmethod
    def get_account_type(cls, obj):
        try:
            if obj.account_type:
                all_account_types = [account_type.get('title', None) for account_type in obj.account_type]
                return all_account_types
        except AccountType.DoesNotExist:
            pass
        return []

    @classmethod
    def get_industry(cls, obj):
        try:
            if obj.industry:
                return obj.industry.title
        except Industry.DoesNotExist:
            pass
        return []

    @classmethod
    def get_manager(cls, obj):
        try:
            if obj.manager:
                all_managers = [Employee.object_normal.get(id=employees_id).get_full_name() for employees_id in
                                obj.manager]
                return all_managers
        except Employee.DoesNotExist:
            pass
        return []

    @classmethod
    def get_owner(cls, obj):
        try:
            if obj.id:
                owner = Contact.object_normal.get(account_name=obj.id, is_primary=True)
                return {
                    'id': owner.id,
                    'fullname': owner.fullname
                }
        except Contact.DoesNotExist:
            pass
        return {}


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

    def validate_code(self, value):
        try:
            if Account.object_normal.filter(code=value).exists():
                raise serializers.ValidationError("Code is already exist.")
        except Account.DoesNotExist:
            pass
        return value

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
        contact_select_list = None
        contact_primary = None
        if 'contact_select_list' in validated_data:
            contact_select_list = validated_data.get('contact_select_list', None)
            del validated_data['contact_select_list']
        if 'contact_primary' in validated_data:
            contact_primary = validated_data.get('contact_primary', None)
            del validated_data['contact_primary']

        # create account
        account = Account.object_normal.create(**validated_data)

        if contact_primary:
            contact_select_list.append(contact_primary)
        # update contact select
        if contact_select_list:
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
        try:
            list_owner = []
            resp = Contact.object_normal.filter(account_name=obj)
            for item in resp:
                list_owner.append(
                    {
                        'id': item.id,
                        'fullname': item.fullname,
                    }
                )
            return list_owner
        except Contact.DoesNotExist:
            pass
        return []


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
        try:
            return Employee.get_full_name(obj, 2)
        except Employee.DoesNotExist:
            pass
        return ''

    @classmethod
    def get_account(cls, obj):
        try:
            account_list = Account.object_normal.filter(Q(manager__contains=[str(obj.id)]))
            id_list = []
            name_list = []
            for account in account_list:
                id_list.append(account.id)
                name_list.append(account.name)
            return {
                'name': name_list,
                'id': id_list
            }
        except Account.DoesNotExist:
            pass
        return None

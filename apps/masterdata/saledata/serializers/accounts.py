from rest_framework import serializers
from apps.core.hr.models import Employee
from apps.masterdata.saledata.models.accounts import (
    AccountType, Industry, Account, AccountEmployee, AccountGroup, AccountAccountTypes, AccountBanks, AccountCreditCards
)
from apps.masterdata.saledata.models.contacts import Contact
from apps.masterdata.saledata.models.price import Price, Currency
from apps.shared import AccountsMsg


# Account Type
class AccountTypeListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = AccountType
        fields = ('id', 'title', 'code', 'is_default', 'description')


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
        fields = ('id', 'title', 'code', 'is_default', 'description')


class AccountTypeUpdateSerializer(serializers.ModelSerializer): # noqa
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


# Account Group
class AccountGroupListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = AccountGroup
        fields = ('id', 'title', 'code', 'description')


class AccountGroupCreateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = AccountGroup
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_code(cls, value):
        if AccountGroup.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
        return value

    @classmethod
    def validate_title(cls, value):
        if AccountGroup.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


class AccountGroupDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountGroup
        fields = ('id', 'title', 'code', 'description')


class AccountGroupUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = AccountGroup
        fields = ('title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and AccountGroup.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


# Industry
class IndustryListSerializer(serializers.ModelSerializer): # noqa
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


# Account
class AccountListSerializer(serializers.ModelSerializer):
    account_type = serializers.SerializerMethodField()
    manager = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    shipping_address = serializers.JSONField()
    billing_address = serializers.JSONField()

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
            "shipping_address",
            "billing_address"
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


def add_account_types_information(account_types_list, account):
    bulk_info = []
    for item in account_types_list:
        if item.get('title', None) == 'Customer' and item.get('id', None) is not None:
            if item.get('detail', None) == 'individual':
                bulk_info.append(AccountAccountTypes(account=account, account_type_id=item['id'], customer_type=0))
            if item.get('detail', None) == 'organization':
                bulk_info.append(AccountAccountTypes(account=account, account_type_id=item['id'], customer_type=1))
        else:
            if item.get('title', None) is not None and item.get('id', None) is not None:
                bulk_info.append(AccountAccountTypes(account=account, account_type_id=item['id'], customer_type=None))

    if len(bulk_info) > 0:
        AccountAccountTypes.objects.filter(account=account).delete()
        AccountAccountTypes.objects.bulk_create(bulk_info)
    return True


def add_employees_information(account):
    bulk_info = [] # noqa
    manager_field = []
    get_employees = Employee.objects.filter_current(fill__tenant=True, fill__company=True, id__in=account.manager)
    for employee in get_employees:
        bulk_info.append(AccountEmployee(**{'account': account, 'employee': employee}))
        manager_field.append(
            {'id': str(employee.id), 'code': employee.code, 'fullname': employee.get_full_name(2)}
        )
    account.manager = manager_field
    account.save()

    if len(bulk_info) > 0:
        AccountEmployee.objects.filter(account=account).delete()
        AccountEmployee.objects.bulk_create(bulk_info)
    return True


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
            "account_group",
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
        if Account.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
            raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
        return value

    @classmethod
    def validate_account_group(cls, value):
        if value:
            return value
        raise serializers.ValidationError(AccountsMsg.ACCOUNT_GROUP_NOT_NONE)

    def validate(self, validate_data):
        account_types = []
        for item in validate_data.get('account_type', None):
            account_type = AccountType.objects.filter_current(fill__tenant=True, fill__company=True, id=item).first()
            if account_type:
                detail = self.initial_data.get('customer_detail_type', '')
                account_types.append(
                    {'id': str(item), 'code': account_type.code, 'title': account_type.title, 'detail': detail}
                )
                tax_code = validate_data.get('tax_code', None)
                if detail == 'organization':  # tax_code is required
                    if tax_code is None:
                        raise serializers.ValidationError(AccountsMsg.TAX_CODE_NOT_NONE)
                elif detail == 'individual':
                    validate_data.update({'parent_account': None})

                account_mapped_tax_code = Account.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    tax_code=tax_code
                ).exists()
                if account_mapped_tax_code:
                    raise serializers.ValidationError(AccountsMsg.TAX_CODE_IS_EXIST)
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
        default_price_list = Price.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_default=True
        ).first()
        if 'currency' not in validated_data:
            default_currency = Currency.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                is_default=True).first()
        else:
            default_currency = validated_data['currency']

        account = Account.objects.create(
            **validated_data,
            price_list_mapped=default_price_list,
            currency=default_currency
        )
        # add employee information
        add_employees_information(account)
        # add account type detail information
        add_account_types_information(validated_data.get('account_type', None), account)

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
                if len(contact_list) == 1:
                    contact_list[0].is_primary = True
                    contact_list[0].account_name = account
                    contact_list[0].save()
                else:
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
            "account_group",
            'tax_code',
            'industry',
            'annual_revenue',
            'total_employees',
            'phone',
            'email',
            'shipping_address',
            'billing_address',
            'payment_term_mapped',
            'price_list_mapped',
            'credit_limit',
            'currency',
            'owner',
            'contact_mapped',
            'bank_accounts_information',
            'credit_cards_information'
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
        return {}

    @classmethod
    def get_contact_mapped(cls, obj):
        contact_mapped = Contact.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            account_name=obj
        )
        if contact_mapped.count() > 0:
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
    bulk_info = [] # noqa
    instance_manager_field = []
    get_employees = Employee.objects.filter_current(fill__tenant=True, fill__company=True, id__in=instance.manager)
    for employee in get_employees:
        bulk_info.append(AccountEmployee(**{'account': instance, 'employee': employee}))
        instance_manager_field.append(
            {'id': str(employee.id), 'code': employee.code, 'fullname': employee.get_full_name(2)}
        )
    instance.manager = instance_manager_field
    instance.save()

    if len(bulk_info) > 0:
        AccountEmployee.objects.filter(account=instance).delete()
        AccountEmployee.objects.bulk_create(bulk_info)
    return True


def update_account_owner(instance, account_owner):
    Contact.objects.filter_current(fill__tenant=True, fill__company=True, account_name=instance).update(
        account_name=None,
        is_primary=False
    )
    if account_owner:
        Contact.objects.filter_current(fill__tenant=True, fill__company=True, id=account_owner).update(
            account_name=instance,
            is_primary=True
        )
    return True


def add_banking_accounts_information(instance, banking_accounts_list):
    bulk_info = []
    for item in banking_accounts_list:
        bulk_info.append(
            AccountBanks(**item, account=instance)
        )
    if len(bulk_info) > 0:
        AccountBanks.objects.filter(account=instance).delete()
        AccountBanks.objects.bulk_create(bulk_info)
    return True


def add_credit_cards_information(instance, credit_cards_list):
    bulk_info = []
    for item in credit_cards_list:
        bulk_info.append(
            AccountCreditCards(**item, account=instance)
        )
    if len(bulk_info) > 0:
        AccountCreditCards.objects.filter(account=instance).delete()
        AccountCreditCards.objects.bulk_create(bulk_info)
    return True


class AccountUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=150)
    account_type = serializers.JSONField()
    parent_account = serializers.UUIDField(required=False, allow_null=True)
    bank_accounts_information = serializers.JSONField()
    credit_cards_information = serializers.JSONField()

    class Meta:
        model = Account
        fields = (
            'name',
            'website',
            'account_type',
            'manager',
            'parent_account',
            'account_group',
            'tax_code',
            'industry',
            'annual_revenue',
            'total_employees',
            'phone',
            'email',
            'currency',
            'shipping_address',
            'billing_address',
            'payment_term_mapped',
            'price_list_mapped',
            'credit_limit',
            'bank_accounts_information',
            'credit_cards_information'
        )

    @classmethod
    def validate_account_group(cls, value):
        if value:
            return value
        raise serializers.ValidationError(AccountsMsg.ACCOUNT_GROUP_NOT_NONE)

    @classmethod
    def validate_bank_accounts_information(cls, value):
        for item in value:
            for key in item:
                if item[key] is None:
                    raise serializers.ValidationError(AccountsMsg.BANK_ACCOUNT_MISSING_VALUE)
        return value

    @classmethod
    def validate_credit_cards_information(cls, value):
        for item in value:
            for key in item:
                if item[key] is None:
                    raise serializers.ValidationError(AccountsMsg.CREDIT_CARD_MISSING_VALUE)
        return value

    def validate(self, validate_data):
        account_types = []
        for item in validate_data.get('account_type', None):
            account_type = AccountType.objects.filter_current(fill__tenant=True, fill__company=True, id=item).first()
            if account_type:
                detail = self.initial_data.get('customer_detail_type', '')
                account_types.append(
                    {'id': str(item), 'code': account_type.code, 'title': account_type.title, 'detail': detail}
                )
                tax_code = validate_data.get('tax_code', None)
                if detail == 'organization':  # tax_code is required
                    if tax_code is None:
                        raise serializers.ValidationError(AccountsMsg.TAX_CODE_NOT_NONE)
                elif detail == 'individual':
                    validate_data.update({'parent_account': None})

                account_mapped_tax_code = Account.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    tax_code=tax_code
                ).first()
                if account_mapped_tax_code and account_mapped_tax_code != self.instance:
                    raise serializers.ValidationError(AccountsMsg.TAX_CODE_IS_EXIST)
            else:
                raise serializers.ValidationError(AccountsMsg.ACCOUNTTYPE_NOT_EXIST)
        validate_data['account_type'] = account_types
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # update account owner
        update_account_owner(instance, self.initial_data.get('account-owner', None))
        # recreate in AccountEmployee (Account Manager)
        recreate_employee_map_account(instance)
        # add account type detail information
        add_account_types_information(validated_data.get('account_type', None), instance)
        # add banking accounts
        add_banking_accounts_information(instance, validated_data.get('bank_accounts_information', None))
        # add credit cards
        add_credit_cards_information(instance, validated_data.get('credit_cards_information', None))
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

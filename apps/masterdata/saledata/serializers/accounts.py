from rest_framework import serializers
from apps.core.hr.models import Employee
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models.accounts import (
    AccountType, Industry, Account, AccountEmployee, AccountGroup, AccountAccountTypes, AccountBanks,
    AccountCreditCards, AccountShippingAddress, AccountBillingAddress, PaymentTerm
)
from apps.masterdata.saledata.models.contacts import Contact
from apps.masterdata.saledata.models.price import Price, Currency
from apps.shared import AccountsMsg, HRMsg, AbstractDetailSerializerModel


# Account Type
class AccountTypeListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = AccountType
        fields = ('id', 'title', 'code', 'is_default', 'description')


class AccountTypeCreateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150) # noqa

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


class AccountTypeUpdateSerializer(serializers.ModelSerializer):  # noqa
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
class IndustryListSerializer(serializers.ModelSerializer):  # noqa
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
    contact_mapped = serializers.SerializerMethodField()
    account_type = serializers.SerializerMethodField()
    manager = serializers.SerializerMethodField()
    industry = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            "id",
            'code',
            "name",
            "website",
            "code",
            "account_type",
            "industry",
            "manager",
            "owner",
            "phone",
            'annual_revenue',
            'contact_mapped'
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
        if obj.owner:
            return {'id': obj.owner_id, 'fullname': obj.owner.fullname}
        return {}

    @classmethod
    def get_industry(cls, obj):
        if obj.industry:
            return {
                'id': obj.industry_id,
                'title': obj.industry.title
            }
        return {}

    @classmethod
    def get_contact_mapped(cls, obj):
        contact_mapped = obj.contact_account_name.all()
        if contact_mapped.count() > 0:
            list_contact_mapped = []
            for i in contact_mapped:
                list_contact_mapped.append(str(i.id))
            return list_contact_mapped
        return []


def create_employee_map_account(account):
    bulk_info = []
    for manager_obj in account.manager:
        bulk_info.append(AccountEmployee(account=account, employee_id=manager_obj.get('id', None)))
    if len(bulk_info) > 0:
        AccountEmployee.objects.filter(account=account).delete()
        AccountEmployee.objects.bulk_create(bulk_info)
    return True


def add_banking_accounts_information(instance, banking_accounts_list):
    bulk_info = []
    for item in banking_accounts_list:
        bulk_info.append(AccountBanks(**item, account=instance))
    if len(bulk_info) > 0:
        AccountBanks.objects.filter(account=instance).delete()
        AccountBanks.objects.bulk_create(bulk_info)
    return True


def add_credit_cards_information(instance, credit_cards_list):
    bulk_info = []
    for item in credit_cards_list:
        if item.get('credit_card_type', None) == 'Mastercard':
            item['credit_card_type'] = 1
        if item.get('credit_card_type', None) == 'Visa':
            item['credit_card_type'] = 2
        if item.get('credit_card_type', None) == 'American express':
            item['credit_card_type'] = 3
        bulk_info.append(AccountCreditCards(**item, account=instance))
    if len(bulk_info) > 0:
        AccountCreditCards.objects.filter(account=instance).delete()
        AccountCreditCards.objects.bulk_create(bulk_info)
    return True


def add_account_types_information(account):
    bulk_info = []
    for account_type_obj in account.account_type:
        bulk_info.append(AccountAccountTypes(account=account, account_type_id=account_type_obj.get('id', None)))
    if len(bulk_info) > 0:
        AccountAccountTypes.objects.filter(account=account).delete()
        AccountAccountTypes.objects.bulk_create(bulk_info)
    return True


def add_shipping_address_information(account, shipping_address_list):
    bulk_info = []
    for item in shipping_address_list:
        bulk_info.append(AccountShippingAddress(**item, account=account))
    AccountShippingAddress.objects.bulk_create(bulk_info)
    return True


def add_billing_address_information(account, billing_address_list):
    bulk_info = []
    for item in billing_address_list:
        bulk_info.append(AccountBillingAddress(**item, account=account))
    AccountBillingAddress.objects.bulk_create(bulk_info)
    return True


def update_shipping_address_information(account, old_shipping_address_id_dict):
    for item in AccountShippingAddress.objects.filter(account=account):
        if item.full_address not in [i.get('full_address', None) for i in old_shipping_address_id_dict]:
            item.delete()
        else:
            item.is_default = False
            item.save()
    try:
        new_default = [k for k in old_shipping_address_id_dict if k['is_default']][0].get('full_address', None)
        AccountShippingAddress.objects.filter(account=account, full_address=new_default).update(is_default=True)
    except AccountShippingAddress.DoesNotExist:
        raise serializers.ValidationError({'Account Shipping Address': AccountsMsg.ACCOUNT_SHIPPING_NOT_EXIST})
    return True


def update_billing_address_information(account, old_billing_address_id_dict):
    for item in AccountBillingAddress.objects.filter(account=account):
        if item.full_address not in [i.get('full_address', None) for i in old_billing_address_id_dict]:
            item.delete()
        else:
            item.is_default = False
            item.save()
    try:
        new_default = [k for k in old_billing_address_id_dict if k['is_default']][0].get('full_address', None)
        AccountBillingAddress.objects.filter(account=account, full_address=new_default).update(is_default=True)
    except AccountBillingAddress.DoesNotExist:
        raise serializers.ValidationError({'Account Billing Address': AccountsMsg.ACCOUNT_BILLING_NOT_EXIST})
    return True


class AccountCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=150)
    tax_code = serializers.CharField(max_length=150, required=False, allow_null=True)
    owner = serializers.UUIDField(required=False, allow_null=True)
    account_group = serializers.UUIDField(required=False, allow_null=True)
    industry = serializers.UUIDField(required=False, allow_null=True)
    account_type = serializers.ListField(child=serializers.UUIDField(required=True))
    manager = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    parent_account = serializers.UUIDField(required=False, allow_null=True)
    contact_select_list = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    system_status = serializers.ChoiceField(choices=[0, 1], help_text='0: draft, 1: created', default=0,)

    class Meta:
        model = Account
        fields = (
            'name',
            'code',
            'website',
            'account_type',
            'account_type_selection',
            'account_group',
            'owner',
            'manager',
            'parent_account',
            'tax_code',
            'industry',
            'annual_revenue',
            'total_employees',
            'phone',
            'email',
            'contact_select_list',
            'system_status'
        )

    @classmethod
    def validate_code(cls, value):
        if value:
            if Account.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
            return value
        raise serializers.ValidationError({"code": AccountsMsg.CODE_NOT_NULL})

    @classmethod
    def validate_tax_code(cls, value):
        if Account.objects.filter_current(fill__tenant=True, fill__company=True, tax_code=value).exists():
            raise serializers.ValidationError({"Tax code": AccountsMsg.TAX_CODE_IS_EXIST})
        return value

    @classmethod
    def validate_owner(cls, value):
        if value:
            try:
                return Contact.objects.get(id=value)
            except Contact.DoesNotExist:
                raise serializers.ValidationError({"Owner": AccountsMsg.CONTACT_NOT_EXIST})
        return None

    @classmethod
    def validate_account_type(cls, value):
        if isinstance(value, list):
            account_type = AccountType.objects.filter(id__in=value)
            if account_type.count() == len(value):
                return [
                    {'id': str(item.id), 'code': item.code, 'title': item.title}
                    for item in account_type
                ]
            raise serializers.ValidationError({'Account Type': HRMsg.ACCOUNT_TYPE_NOT_EXIST})
        raise serializers.ValidationError({'Account Type': HRMsg.ACCOUNT_TYPE_IS_ARRAY})

    @classmethod
    def validate_account_group(cls, value):
        if value:
            try:
                return AccountGroup.objects.get(id=value)
            except AccountGroup.DoesNotExist:
                raise serializers.ValidationError({"Account Group": AccountsMsg.ACCOUNT_GROUP_NOT_EXIST})
        raise serializers.ValidationError(AccountsMsg.ACCOUNT_GROUP_NOT_NONE)

    @classmethod
    def validate_manager(cls, value):
        if isinstance(value, list):
            employee_list = Employee.objects.filter(id__in=value)
            if employee_list.count() == len(value):
                return [
                    {'id': str(item.id), 'code': item.code, 'full_name': item.get_full_name(2)}
                    for item in employee_list
                ]
            raise serializers.ValidationError({'Manager': HRMsg.EMPLOYEES_NOT_EXIST})
        raise serializers.ValidationError({'Manager': HRMsg.EMPLOYEE_IS_ARRAY})

    @classmethod
    def validate_parent_account(cls, value):
        if value:
            try:
                return Account.objects.get(id=value)
            except AccountGroup.DoesNotExist:
                raise serializers.ValidationError({"Parent Account": AccountsMsg.PARENT_ACCOUNT_NOT_EXIST})
        return None

    @classmethod
    def validate_industry(cls, value):
        if value:
            try:
                return Industry.objects.get(id=value)
            except Industry.DoesNotExist:
                raise serializers.ValidationError({"Industry": AccountsMsg.INDUSTRY_NOT_EXIST})
        raise serializers.ValidationError({"Industry": AccountsMsg.INDUSTRY_NOT_NULL})

    def validate(self, validate_data):
        if validate_data.get('account_type_selection', None):
            if 'tax_code' not in validate_data:
                raise serializers.ValidationError({"Tax code": AccountsMsg.TAX_CODE_NOT_NONE})
            if 'total_employees' not in validate_data:
                raise serializers.ValidationError({"Total employee": AccountsMsg.TOTAL_EMPLOYEES_NOT_NONE})

        try:
            validate_data['price_list_mapped'] = Price.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                is_default=True
            )
        except Price.DoesNotExist:
            raise serializers.ValidationError({"Price List": AccountsMsg.PRICE_LIST_DEFAULT_NOT_EXIST})

        try:
            validate_data['currency'] = Currency.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                is_primary=True
            )
        except Currency.DoesNotExist:
            raise serializers.ValidationError({"Currency": AccountsMsg.CURRENCY_DEFAULT_NOT_EXIST})

        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        contact_mapped = self.initial_data.get('contact_mapped', None)

        account = Account.objects.create(**validated_data)

        create_employee_map_account(account)
        add_account_types_information(account)

        add_shipping_address_information(account, self.initial_data.get('shipping_address_id_dict', []))
        add_billing_address_information(account, self.initial_data.get('billing_address_id_dict', []))

        if contact_mapped:
            for obj in contact_mapped:
                try:
                    contact = Contact.objects.get(id=obj.get('id', None))
                    contact.is_primary = obj['owner']
                    contact.account_name = account
                    contact.save()
                except Contact.DoesNotExist:
                    raise serializers.ValidationError({"Contact": AccountsMsg.CONTACT_NOT_EXIST})
        return account


class AccountDetailSerializer(AbstractDetailSerializerModel):
    contact_mapped = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    account_group = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    price_list_mapped = serializers.SerializerMethodField()
    parent_account = serializers.SerializerMethodField()
    industry = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()
    billing_address = serializers.SerializerMethodField()
    payment_term_customer_mapped = serializers.SerializerMethodField()
    payment_term_supplier_mapped = serializers.SerializerMethodField()
    bank_accounts_mapped = serializers.SerializerMethodField()
    credit_cards_mapped = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
            'name',
            'code',
            'website',
            'account_type',
            "owner",
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
            'payment_term_customer_mapped',
            'payment_term_supplier_mapped',
            'bank_accounts_mapped',
            'credit_cards_mapped',
            'price_list_mapped',
            'credit_limit_customer',
            'credit_limit_supplier',
            'currency',
            'owner',
            'contact_mapped',
            'account_type_selection',
            'workflow_runtime_id',
        )

    @classmethod
    def get_account_group(cls, obj):
        if obj.account_group:
            return {
                'id': obj.account_group_id,
                'code': obj.account_group.code,
                'title': obj.account_group.title,
            }
        return {}

    @classmethod
    def get_currency(cls, obj):
        if obj.currency:
            return {
                'id': obj.currency_id,
                'abbreviation': obj.currency.abbreviation,
                'title': obj.currency.title,
            }
        return {}

    @classmethod
    def get_price_list_mapped(cls, obj):
        if obj.price_list_mapped:
            return {
                'id': obj.price_list_mapped_id,
                'title': obj.price_list_mapped.title,
            }
        return {}

    @classmethod
    def get_industry(cls, obj):
        if obj.industry:
            return {
                'id': obj.industry_id,
                'code': obj.industry.code,
                'title': obj.industry.title,
            }
        return {}

    @classmethod
    def get_parent_account(cls, obj):
        if obj.parent_account:
            return {
                'id': obj.parent_account_id,
                'code': obj.parent_account.code,
                'name': obj.parent_account.name,
            }
        return {}

    @classmethod
    def get_owner(cls, obj):
        if obj.owner:
            contact_owner_information = {'id': str(obj.owner.owner_id), 'fullname': obj.owner.owner.get_full_name(2)}
            return {
                'id': obj.owner_id,
                'fullname': obj.owner.fullname,
                'job_title': obj.owner.job_title,
                'email': obj.owner.email,
                'mobile': obj.owner.mobile,
                'contact_owner': contact_owner_information
            }
        return {}

    @classmethod
    def get_payment_term_customer_mapped(cls, obj):
        if obj.payment_term_customer_mapped:
            return {
                'id': str(obj.payment_term_customer_mapped_id),
                'title': obj.payment_term_customer_mapped.title
            }
        return {}

    @classmethod
    def get_payment_term_supplier_mapped(cls, obj):
        if obj.payment_term_supplier_mapped:
            return {
                'id': str(obj.payment_term_supplier_mapped_id),
                'title': obj.payment_term_supplier_mapped.title
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
                if i.is_primary:
                    list_contact_mapped.insert(
                        0, (
                            {
                                'id': i.id,
                                'fullname': i.fullname,
                                'job_title': i.job_title,
                                'email': i.email,
                                'mobile': i.mobile,
                                'owner': i.is_primary
                            })
                    )
                else:
                    list_contact_mapped.append(
                        {
                            'id': i.id,
                            'fullname': i.fullname,
                            'job_title': i.job_title,
                            'email': i.email,
                            'mobile': i.mobile,
                            'owner': i.is_primary
                        }
                    )
            return list_contact_mapped
        return []

    @classmethod
    def get_shipping_address(cls, obj):
        shipping_address_list = []
        for item in obj.account_mapped_shipping_address.all():
            shipping_address_list.append({
                'id': item.id,
                'full_address': item.full_address,
                'is_default': item.is_default
            })
        return shipping_address_list

    @classmethod
    def get_billing_address(cls, obj):
        billing_address_list = []
        for item in obj.account_mapped_billing_address.all():
            billing_address_list.append({
                'id': item.id,
                'full_address': item.full_address,
                'is_default': item.is_default
            })
        return billing_address_list

    @classmethod
    def get_bank_accounts_mapped(cls, obj):
        bank_accounts_mapped_list = []
        for item in obj.account_banks_mapped.all():
            bank_accounts_mapped_list.append(
                {
                    'bank_country_id': item.country_id,
                    'bank_name': item.bank_name,
                    'bank_code': item.bank_code,
                    'bank_account_name': item.bank_account_name,
                    'bank_account_number': item.bank_account_number,
                    'bic_swift_code': item.bic_swift_code,
                    'is_default': item.is_default
                }
            )
        return bank_accounts_mapped_list

    @classmethod
    def get_credit_cards_mapped(cls, obj):
        credit_cards_mapped_list = []
        for item in obj.credit_cards_mapped.all():
            credit_cards_mapped_list.append(
                {
                    'credit_card_type': item.credit_card_type,
                    'credit_card_number': item.credit_card_number,
                    'credit_card_name': item.credit_card_name,
                    'card_expired_date': item.expired_date,
                    'is_default': item.is_default
                }
            )
        return credit_cards_mapped_list


class AccountUpdateSerializer(serializers.ModelSerializer):
    tax_code = serializers.CharField(max_length=150, required=False, allow_null=True)
    owner = serializers.UUIDField(required=False, allow_null=True)
    account_group = serializers.UUIDField(required=False, allow_null=True)
    industry = serializers.UUIDField(required=False, allow_null=True)
    account_type = serializers.ListField(child=serializers.UUIDField(required=True))
    manager = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    parent_account = serializers.UUIDField(required=False, allow_null=True)
    contact_select_list = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    system_status = serializers.ChoiceField(choices=[0, 1], help_text='0: draft, 1: created', default=0)
    price_list_mapped = serializers.UUIDField(required=False, allow_null=True)
    currency = serializers.UUIDField()
    payment_term_customer_mapped = serializers.UUIDField(required=False, allow_null=True)
    payment_term_supplier_mapped = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Account
        fields = (
            'name',
            'website',
            'account_type',
            'account_type_selection',
            'account_group',
            'owner',
            'manager',
            'parent_account',
            'tax_code',
            'industry',
            'annual_revenue',
            'total_employees',
            'phone',
            'email',
            'contact_select_list',
            'system_status',
            # from-detail
            'price_list_mapped',
            'currency',
            'payment_term_customer_mapped',
            'payment_term_supplier_mapped',
            'credit_limit_customer',
            'credit_limit_supplier'
        )

    @classmethod
    def validate_tax_code(cls, value):
        if Account.objects.filter_current(fill__tenant=True, fill__company=True, tax_code=value).count() > 1:
            raise serializers.ValidationError({"Tax code": AccountsMsg.TAX_CODE_IS_EXIST})
        return value

    @classmethod
    def validate_owner(cls, value):
        if value:
            try:
                return Contact.objects.get(id=value)
            except Contact.DoesNotExist:
                raise serializers.ValidationError({"Owner": AccountsMsg.CONTACT_NOT_EXIST})
        return None

    @classmethod
    def validate_account_type(cls, value):
        if isinstance(value, list):
            account_type = AccountType.objects.filter(id__in=value)
            if account_type.count() == len(value):
                return [
                    {'id': str(item.id), 'code': item.code, 'title': item.title}
                    for item in account_type
                ]
            raise serializers.ValidationError({'Account Type': HRMsg.ACCOUNT_TYPE_NOT_EXIST})
        raise serializers.ValidationError({'Account Type': HRMsg.ACCOUNT_TYPE_IS_ARRAY})

    @classmethod
    def validate_account_group(cls, value):
        if value:
            try:
                return AccountGroup.objects.get(id=value)
            except AccountGroup.DoesNotExist:
                raise serializers.ValidationError({"Account Group": AccountsMsg.ACCOUNT_GROUP_NOT_EXIST})
        raise serializers.ValidationError(AccountsMsg.ACCOUNT_GROUP_NOT_NONE)

    @classmethod
    def validate_manager(cls, value):
        if isinstance(value, list):
            employee_list = Employee.objects.filter(id__in=value)
            if employee_list.count() == len(value):
                return [
                    {'id': str(item.id), 'code': item.code, 'full_name': item.get_full_name(2)}
                    for item in employee_list
                ]
            raise serializers.ValidationError({'Manager': HRMsg.EMPLOYEES_NOT_EXIST})
        raise serializers.ValidationError({'Manager': HRMsg.EMPLOYEE_IS_ARRAY})

    @classmethod
    def validate_parent_account(cls, value):
        if value:
            try:
                return Account.objects.get(id=value)
            except AccountGroup.DoesNotExist:
                raise serializers.ValidationError({"Parent Account": AccountsMsg.PARENT_ACCOUNT_NOT_EXIST})
        return None

    @classmethod
    def validate_industry(cls, value):
        if value:
            try:
                return Industry.objects.get(id=value)
            except Industry.DoesNotExist:
                raise serializers.ValidationError({"Industry": AccountsMsg.INDUSTRY_NOT_EXIST})
        raise serializers.ValidationError({"Industry": AccountsMsg.INDUSTRY_NOT_NULL})

    @classmethod
    def validate_currency(cls, value):
        if value:
            try:
                return Currency.objects.get(id=value)
            except Currency.DoesNotExist:
                raise serializers.ValidationError({"Currency": AccountsMsg.CURRENCY_DEFAULT_NOT_EXIST})
        raise serializers.ValidationError({"Currency": AccountsMsg.CURRENCY_NOT_NULL})

    @classmethod
    def validate_payment_term_customer_mapped(cls, value):
        if value:
            try:
                return PaymentTerm.objects.get(id=value)
            except PaymentTerm.DoesNotExist:
                raise serializers.ValidationError({"Payment Term": AccountsMsg.PAYMENT_TERM_NOT_EXIST})
        return None

    @classmethod
    def validate_payment_term_supplier_mapped(cls, value):
        if value:
            try:
                return PaymentTerm.objects.get(id=value)
            except PaymentTerm.DoesNotExist:
                raise serializers.ValidationError({"Payment Term": AccountsMsg.PAYMENT_TERM_NOT_EXIST})
        return None

    @classmethod
    def validate_price_list_mapped(cls, value):
        if value:
            try:
                return Price.objects.get(id=value)
            except Price.DoesNotExist:
                raise serializers.ValidationError({"Price": AccountsMsg.PRICE_LIST_DEFAULT_NOT_EXIST})
        return None

    def validate(self, validate_data):
        if validate_data.get('account_type_selection', None):
            if 'tax_code' not in validate_data:
                raise serializers.ValidationError({"Tax code": AccountsMsg.TAX_CODE_NOT_NONE})
            if 'total_employees' not in validate_data:
                raise serializers.ValidationError({"Total employee": AccountsMsg.TOTAL_EMPLOYEES_NOT_NONE})
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        Contact.objects.filter(account_name=instance).update(account_name=None)
        update_shipping_address_information(instance, self.initial_data.get('update_shipping_address', []))
        update_billing_address_information(instance, self.initial_data.get('update_billing_address', []))

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        contact_mapped = self.initial_data.get('contact_mapped', []) # noqa
        create_employee_map_account(instance) # noqa
        add_account_types_information(instance)

        add_shipping_address_information(instance, self.initial_data.get('shipping_address_id_dict', []))
        add_billing_address_information(instance, self.initial_data.get('billing_address_id_dict', []))

        add_banking_accounts_information(instance, self.initial_data.get('bank_accounts_information', []))
        add_credit_cards_information(instance, self.initial_data.get('credit_cards_information', []))

        for obj in contact_mapped:
            try:
                contact = Contact.objects.get(id=obj.get('id', None))
                contact.is_primary = obj['owner']
                contact.account_name = instance
                contact.save()
            except Contact.DoesNotExist:
                raise serializers.ValidationError({"Contact": AccountsMsg.CONTACT_NOT_EXIST})
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


class AccountForSaleListSerializer(serializers.ModelSerializer):
    account_type = serializers.SerializerMethodField()
    manager = serializers.SerializerMethodField()
    industry = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()
    billing_address = serializers.SerializerMethodField()
    payment_term_customer_mapped = serializers.SerializerMethodField()
    payment_term_supplier_mapped = serializers.SerializerMethodField()
    price_list_mapped = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            "id",
            'code',
            "name",
            "website",
            "code",
            "account_type",
            "industry",
            "manager",
            "owner",
            "phone",
            "shipping_address",
            "billing_address",
            "payment_term_customer_mapped",
            'payment_term_supplier_mapped',
            "price_list_mapped"
        )

    @classmethod
    def get_account_type(cls, obj):
        return [account_type.get('title', None) for account_type in obj.account_type] if obj.account_type else []

    @classmethod
    def get_manager(cls, obj):
        return obj.manager if obj.manager else []

    @classmethod
    def get_owner(cls, obj):
        return {'id': obj.owner_id, 'fullname': obj.owner.fullname} if obj.owner else {}

    @classmethod
    def get_industry(cls, obj):
        return {
            'id': obj.industry_id,
            'title': obj.industry.title
        } if obj.industry else {}

    @classmethod
    def get_payment_term_customer_mapped(cls, obj):
        return {
            'id': obj.payment_term_customer_mapped_id,
            'title': obj.payment_term_customer_mapped.title,
            'code': obj.payment_term_customer_mapped.code
        } if obj.payment_term_customer_mapped else {}

    @classmethod
    def get_payment_term_supplier_mapped(cls, obj):
        return {
            'id': obj.payment_term_supplier_mapped_id,
            'title': obj.payment_term_supplier_mapped.title,
            'code': obj.payment_term_supplier_mapped.code
        } if obj.payment_term_supplier_mapped else {}

    @classmethod
    def get_price_list_mapped(cls, obj):
        return {
            'id': obj.price_list_mapped_id,
            'title': obj.price_list_mapped.title,
            'code': obj.price_list_mapped.code
        } if obj.price_list_mapped else {}

    @classmethod
    def get_shipping_address(cls, obj):
        return [
            {'id': shipping.id, 'full_address': shipping.full_address}
            for shipping in obj.account_mapped_shipping_address.all()
        ]

    @classmethod
    def get_billing_address(cls, obj):
        return [
            {'id': billing.id, 'full_address': billing.full_address}
            for billing in obj.account_mapped_billing_address.all()
        ]

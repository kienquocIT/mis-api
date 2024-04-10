import datetime

from rest_framework import serializers
from django.utils import timezone
from apps.core.hr.models import Employee
from apps.masterdata.saledata.models import Term
from apps.masterdata.saledata.models.accounts import (
    AccountType, Industry, Account, AccountEmployee, AccountGroup, AccountAccountTypes, AccountBanks,
    AccountCreditCards, AccountShippingAddress, AccountBillingAddress, PaymentTerm
)
from apps.masterdata.saledata.models.contacts import Contact
from apps.masterdata.saledata.models.price import Price, Currency
from apps.shared import AccountsMsg, HRMsg


# Account
class AccountListSerializer(serializers.ModelSerializer):
    contact_mapped = serializers.SerializerMethodField()
    account_type = serializers.SerializerMethodField()
    manager = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    bank_accounts_mapped = serializers.SerializerMethodField()
    revenue_information = serializers.SerializerMethodField()
    billing_address = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            "id",
            'code',
            "name",
            "website",
            "code",
            "tax_code",
            "account_type",
            "manager",
            "owner",
            "phone",
            'annual_revenue',
            'contact_mapped',
            'bank_accounts_mapped',
            'revenue_information',
            'billing_address'
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
    def get_contact_mapped(cls, obj):
        contact_mapped = obj.contact_account_name.all()
        if contact_mapped.count() > 0:
            list_contact_mapped = []
            for item in contact_mapped:
                list_contact_mapped.append(str(item.id))
            return list_contact_mapped
        return []

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
    def get_revenue_information(cls, obj):
        current_date = timezone.now()
        revenue_ytd = 0
        order_number = 0
        for period in obj.company.saledata_periods_belong_to_company.all():
            if period.fiscal_year == current_date.year:
                start_date_str = str(period.start_date) + ' 00:00:00'
                start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
                for customer_revenue in obj.report_customer_customer.all():
                    if customer_revenue.date_approved:
                        if start_date <= customer_revenue.date_approved <= current_date:
                            revenue_ytd += customer_revenue.revenue
                            order_number += 1
        return {
            'revenue_ytd': revenue_ytd,
            'order_number': order_number,
            'revenue_average': round(revenue_ytd / order_number) if order_number > 0 else 0,
        }

    @classmethod
    def get_billing_address(cls, obj):
        billing_address_list = []
        for item in obj.account_mapped_billing_address.all():
            billing_address_list.append({
                'id': item.id,
                'account_name': item.account_name,
                'email': item.email,
                'tax_code': item.tax_code,
                'account_address': item.account_address,
                'full_address': item.full_address,
                'is_default': item.is_default
            })
        return billing_address_list


def create_employee_map_account(account):
    bulk_info = []
    for manager_obj in account.manager:
        bulk_info.append(AccountEmployee(account=account, employee_id=manager_obj.get('id', None)))
    if len(bulk_info) > 0:
        AccountEmployee.objects.filter(account=account).delete()
        AccountEmployee.objects.bulk_create(bulk_info)
    return True


def add_banking_accounts_information(account, banking_accounts_list):
    bulk_info = []
    for item in banking_accounts_list:
        bulk_info.append(AccountBanks(**item, account=account))
    if len(bulk_info) > 0:
        AccountBanks.objects.filter(account=account).delete()
        AccountBanks.objects.bulk_create(bulk_info)
    return True


def add_credit_cards_information(account, credit_cards_list):
    bulk_info = []
    for item in credit_cards_list:
        if item.get('credit_card_type', None) == 'Mastercard':
            item['credit_card_type'] = 1
        if item.get('credit_card_type', None) == 'Visa':
            item['credit_card_type'] = 2
        if item.get('credit_card_type', None) == 'American express':
            item['credit_card_type'] = 3
        bulk_info.append(AccountCreditCards(**item, account=account))
    if len(bulk_info) > 0:
        AccountCreditCards.objects.filter(account=account).delete()
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
    AccountShippingAddress.objects.filter(account=account).delete()
    AccountShippingAddress.objects.bulk_create(bulk_info)
    return True


def add_billing_address_information(account, billing_address_list):
    bulk_info = []
    for item in billing_address_list:
        bulk_info.append(AccountBillingAddress(**item, account=account))
    AccountBillingAddress.objects.filter(account=account).delete()
    AccountBillingAddress.objects.bulk_create(bulk_info)
    return True


class AccountCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=150)
    code = serializers.CharField(max_length=150)
    tax_code = serializers.CharField(max_length=150, required=False, allow_null=True)
    account_group = serializers.UUIDField(required=False, allow_null=True)
    industry = serializers.UUIDField(required=False, allow_null=True)
    account_type = serializers.ListField(child=serializers.UUIDField(required=True))
    manager = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    parent_account_mapped = serializers.UUIDField(required=False, allow_null=True)
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
            'manager',
            'parent_account_mapped',
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
    def validate_name(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"name": AccountsMsg.NAME_NOT_NULL})

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
    def validate_parent_account_mapped(cls, value):
        if value:
            try:
                return Account.objects.get(id=value)
            except Account.DoesNotExist:
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

    def create(self, validated_data):
        contact_mapped = self.initial_data.get('contact_mapped', None)

        account = Account.objects.create(**validated_data)

        create_employee_map_account(account)
        add_account_types_information(account)

        add_shipping_address_information(account, self.initial_data.get('shipping_address_dict', []))
        add_billing_address_information(account, self.initial_data.get('billing_address_dict', []))

        if contact_mapped:
            for obj in contact_mapped:
                try:
                    contact = Contact.objects.get(id=obj.get('id', None))
                    contact.is_primary = obj['is_account_owner']
                    contact.account_name = account
                    contact.save()
                    if obj['is_account_owner']:
                        account.owner = contact
                        account.save()
                except Contact.DoesNotExist:
                    raise serializers.ValidationError({"Contact": AccountsMsg.CONTACT_NOT_EXIST})
        return account


class AccountDetailSerializer(serializers.ModelSerializer):
    contact_mapped = serializers.SerializerMethodField()
    account_group = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    price_list_mapped = serializers.SerializerMethodField()
    parent_account_mapped = serializers.SerializerMethodField()
    industry = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()
    billing_address = serializers.SerializerMethodField()
    payment_term_customer_mapped = serializers.SerializerMethodField()
    payment_term_supplier_mapped = serializers.SerializerMethodField()
    bank_accounts_mapped = serializers.SerializerMethodField()
    credit_cards_mapped = serializers.SerializerMethodField()
    activity = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            'id',
            'name',
            'code',
            'website',
            'account_type',
            'manager',
            'parent_account_mapped',
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
            'contact_mapped',
            'account_type_selection',
            "activity",
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
    def get_parent_account_mapped(cls, obj):
        if obj.parent_account_mapped:
            return {
                'id': obj.parent_account_mapped_id,
                'code': obj.parent_account_mapped.code,
                'name': obj.parent_account_mapped.name,
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
            for item in contact_mapped:
                if item.is_primary:
                    list_contact_mapped.insert(
                        0, (
                            {
                                'id': item.id,
                                'fullname': item.fullname,
                                'job_title': item.job_title,
                                'email': item.email,
                                'mobile': item.mobile,
                                'is_account_owner': item.is_primary,
                                'owner': {
                                    'id': item.owner_id,
                                    'fullname': item.owner.get_full_name(2)
                                } if item.owner else {}
                            })
                    )
                else:
                    list_contact_mapped.append(
                        {
                            'id': item.id,
                            'fullname': item.fullname,
                            'job_title': item.job_title,
                            'email': item.email,
                            'mobile': item.mobile,
                            'is_account_owner': item.is_primary,
                            'owner': {
                                'id': item.owner_id,
                                'fullname': item.owner.get_full_name(2)
                            } if item.owner else {}
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
                'country_id': item.country_id,
                'city_id': item.city_id,
                'district_id': item.district_id,
                'ward_id': item.ward_id,
                'detail_address': item.detail_address,
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
                'account_name': item.account_name,
                'email': item.email,
                'tax_code': item.tax_code,
                'account_address': item.account_address,
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
        credit_cards_type_title_list = ['Mastercard', 'Visa', 'American express']
        for item in obj.credit_cards_mapped.all():
            credit_cards_mapped_list.append(
                {
                    'credit_card_type': credit_cards_type_title_list[item.credit_card_type-1],
                    'credit_card_number': item.credit_card_number,
                    'credit_card_name': item.credit_card_name,
                    'card_expired_date': item.expired_date,
                    'is_default': item.is_default
                }
            )
        return credit_cards_mapped_list

    @classmethod
    def get_activity(cls, obj):
        return [
            {
                'app_code': activity.app_code,
                'document_id': activity.document_id,
                'title': activity.title,
                'code': activity.code,
                'date_activity': activity.date_activity,
                'revenue': activity.revenue,
            } for activity in obj.account_activity_account.all()
        ]


class AccountUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=150)
    tax_code = serializers.CharField(max_length=150, required=False, allow_null=True)
    account_group = serializers.UUIDField(required=False, allow_null=True)
    industry = serializers.UUIDField(required=False, allow_null=True)
    account_type = serializers.ListField(child=serializers.UUIDField(required=True))
    manager = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    parent_account_mapped = serializers.UUIDField(required=False, allow_null=True)
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
            'manager',
            'parent_account_mapped',
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
    def validate_name(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"name": AccountsMsg.NAME_NOT_NULL})

    @classmethod
    def validate_tax_code(cls, value):
        if Account.objects.filter_current(fill__tenant=True, fill__company=True, tax_code=value).count() > 1:
            raise serializers.ValidationError({"Tax code": AccountsMsg.TAX_CODE_IS_EXIST})
        return value

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
    def validate_parent_account_mapped(cls, value):
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

    # @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        contact_mapped = self.initial_data.get('contact_mapped', []) # noqa
        create_employee_map_account(instance) # noqa
        add_account_types_information(instance)

        add_shipping_address_information(instance, self.initial_data.get('shipping_address_dict', []))
        add_billing_address_information(instance, self.initial_data.get('billing_address_dict', []))

        add_banking_accounts_information(instance, self.initial_data.get('bank_accounts_information', []))
        add_credit_cards_information(instance, self.initial_data.get('credit_cards_information', []))

        Contact.objects.filter(account_name=instance).update(account_name=None)
        for obj in contact_mapped:
            try:
                contact = Contact.objects.get(id=obj.get('id', None))
                contact.is_primary = obj['is_account_owner']
                contact.account_name = instance
                contact.save()
                if obj['is_account_owner']:
                    instance.owner = contact
                    instance.save()
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


class TermSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = (
            'id',
            'value',
            'unit_type',
            'day_type',
            'no_of_days',
            'after',
            'order',
        )


# Account serializer use for sale apps
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
        return {
            'id': obj.owner_id,
            'fullname': obj.owner.fullname,
            'email': obj.owner.email,
            'mobile': obj.owner.mobile,
            'job_title': obj.owner.job_title,
        } if obj.owner else {}

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
            'code': obj.payment_term_customer_mapped.code,
            'term': TermSubSerializer(obj.payment_term_customer_mapped.term_payment_term.all(), many=True).data
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

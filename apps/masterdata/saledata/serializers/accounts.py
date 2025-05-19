import datetime
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.core.company.models import CompanyFunctionNumber
from apps.core.hr.models import Employee
from apps.masterdata.saledata.models import Term, Periods
from apps.masterdata.saledata.models.accounts import (
    AccountType, Industry, Account, AccountEmployee, AccountGroup, AccountAccountTypes, AccountBanks,
    AccountCreditCards, AccountShippingAddress, AccountBillingAddress, PaymentTerm
)
from apps.masterdata.saledata.models.contacts import Contact
from apps.masterdata.saledata.models.price import Price, Currency
from apps.shared import AccountsMsg, HRMsg, BaseMsg


# Account
class AccountListSerializer(serializers.ModelSerializer):
    contact_mapped = serializers.SerializerMethodField()
    account_type = serializers.SerializerMethodField()
    manager = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    bank_accounts_mapped = serializers.SerializerMethodField()
    revenue_information = serializers.SerializerMethodField()
    billing_address = serializers.SerializerMethodField()
    industry = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            "id",
            'code',
            "name",
            "website",
            "tax_code",
            "account_type",
            "manager",
            "owner",
            "phone",
            'annual_revenue',
            'contact_mapped',
            'bank_accounts_mapped',
            'revenue_information',
            'billing_address',
            'industry',
            'date_created',
            'employee_created'
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
            'code': obj.owner.code,
            'fullname': obj.owner.fullname,
        } if obj.owner else {}

    @classmethod
    def get_contact_mapped(cls, obj):
        return [str(item.id) for item in obj.contact_account_name.all()]

    @classmethod
    def get_bank_accounts_mapped(cls, obj):
        return [{
            'id': str(item.id),
            'bank_country_id': str(item.country_id),
            'bank_name': item.bank_name,
            'bank_code': item.bank_code,
            'bank_account_name': item.bank_account_name,
            'bank_account_number': item.bank_account_number,
            'bic_swift_code': item.bic_swift_code,
            'is_default': item.is_default
        } for item in obj.account_banks_mapped.all()]

    @classmethod
    def get_revenue_information(cls, obj):
        current_date = timezone.now()
        this_period = Periods.get_current_period(obj.tenant_id, obj.company_id)
        revenue_ytd = 0
        order_number = 0
        if this_period:
            for period in obj.company.saledata_periods_belong_to_company.all():
                if period.fiscal_year == this_period.fiscal_year:
                    start_date_str = str(period.start_date) + ' 00:00:00'
                    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
                    for customer_revenue in obj.report_customer_customer.filter(
                            group_inherit__is_delete=False, sale_order__system_status=3
                    ):
                        if (customer_revenue.date_approved and
                                start_date <= customer_revenue.date_approved <= current_date):
                            revenue_ytd += customer_revenue.revenue
                            order_number += 1
        return {
            'revenue_ytd': revenue_ytd,
            'order_number': order_number,
            'revenue_average': round(revenue_ytd / order_number) if order_number > 0 else 0,
        }

    @classmethod
    def get_billing_address(cls, obj):
        return [{
            'id': str(item.id),
            'account_name': item.account_name,
            'email': item.email,
            'tax_code': item.tax_code,
            'account_address': item.account_address,
            'full_address': item.full_address,
            'is_default': item.is_default
        } for item in obj.account_mapped_billing_address.all()]

    @classmethod
    def get_industry(cls, obj):
        return {
            'id': obj.industry_id,
            'code': obj.industry.code,
            'title': obj.industry.title,
        } if obj.industry else {}

    @classmethod
    def get_employee_created(cls, obj):
        return {
            'id': obj.employee_created_id,
            'code': obj.employee_created.code,
            'full_name': obj.employee_created.get_full_name(2),
            'group': {
                'id': obj.employee_created.group_id,
                'title': obj.employee_created.group.title,
                'code': obj.employee_created.group.code
            } if obj.employee_created.group else {}
        } if obj.employee_created else {}


class AccountCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=150)
    tax_code = serializers.CharField(max_length=150, required=False, allow_null=True, allow_blank=True)
    account_group = serializers.UUIDField(required=False, allow_null=True)
    industry = serializers.UUIDField(required=False, allow_null=True)
    account_type = serializers.ListField(child=serializers.UUIDField(required=True))
    manager = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    parent_account_mapped = serializers.UUIDField(required=False, allow_null=True)
    contact_mapped = serializers.ListField(required=False)

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
            'contact_mapped',
        )

    @classmethod
    def validate_code(cls, value):
        if value:
            if Account.objects.filter_on_company(code=value).exists():
                raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
            return value
        code_generated = CompanyFunctionNumber.gen_auto_code(app_code='account')
        if code_generated:
            return code_generated
        raise serializers.ValidationError({"code": f"{AccountsMsg.CODE_NOT_NULL}. {BaseMsg.NO_CONFIG_AUTO_CODE}"})

    @classmethod
    def validate_name(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"name": AccountsMsg.NAME_NOT_NULL})

    @classmethod
    def validate_tax_code(cls, value):
        if value:
            if Account.objects.filter_on_company(tax_code=value).exists():
                raise serializers.ValidationError({"tax_code": AccountsMsg.TAX_CODE_IS_EXIST})
            return value
        return ''

    @classmethod
    def validate_account_type(cls, value):
        if isinstance(value, list):
            if len(value) == 0:
                raise serializers.ValidationError({'account_type': _('Account type is required')})
            account_type = AccountType.objects.filter(id__in=value)
            if account_type.count() == len(value):
                return [{'id': str(item.id), 'code': item.code, 'title': item.title} for item in account_type]
            raise serializers.ValidationError({'account_type': HRMsg.ACCOUNT_TYPE_NOT_EXIST})
        raise serializers.ValidationError({'account_type': HRMsg.ACCOUNT_TYPE_IS_ARRAY})

    @classmethod
    def validate_account_group(cls, value):
        if value:
            try:
                return AccountGroup.objects.get(id=value)
            except AccountGroup.DoesNotExist:
                raise serializers.ValidationError({"account_group": AccountsMsg.ACCOUNT_GROUP_NOT_EXIST})
        raise serializers.ValidationError(AccountsMsg.ACCOUNT_GROUP_NOT_NONE)

    @classmethod
    def validate_manager(cls, value):
        if isinstance(value, list):
            if len(value) == 0:
                raise serializers.ValidationError({'manager': _('Manager is required')})
            employee_list = Employee.objects.filter(id__in=value)
            if employee_list.count() == len(value):
                return [
                    {'id': str(item.id), 'code': item.code, 'full_name': item.get_full_name(2)}
                    for item in employee_list
                ]
            raise serializers.ValidationError({'manager': HRMsg.EMPLOYEES_NOT_EXIST})
        raise serializers.ValidationError({'manager': HRMsg.EMPLOYEE_IS_ARRAY})

    @classmethod
    def validate_parent_account_mapped(cls, value):
        if value:
            try:
                return Account.objects.get(id=value)
            except Account.DoesNotExist:
                raise serializers.ValidationError({"parent_account_mapped": AccountsMsg.PARENT_ACCOUNT_NOT_EXIST})
        return None

    @classmethod
    def validate_industry(cls, value):
        if value:
            try:
                return Industry.objects.get(id=value)
            except Industry.DoesNotExist:
                raise serializers.ValidationError({"industry": AccountsMsg.INDUSTRY_NOT_EXIST})
        return None

    def validate(self, validate_data):
        if validate_data.get('account_type_selection') == 0:
            if len(validate_data.get('contact_mapped', [])) != 1:
                raise serializers.ValidationError(
                    {"contact_mapped": _('Contact is required (only 1) for individual account')}
                )
            contact_mapped_obj = Contact.objects.filter_on_company(
                id=validate_data['contact_mapped'][0].get('id')
            ).first()
            if contact_mapped_obj:
                validate_data['name'] = contact_mapped_obj.fullname
                validate_data['phone'] = contact_mapped_obj.mobile
                validate_data['email'] = contact_mapped_obj.email
            else:
                raise serializers.ValidationError({"contact_mapped": AccountsMsg.CONTACT_NOT_EXIST})
        else:
            if not validate_data.get('tax_code'):
                raise serializers.ValidationError({"tax_code": AccountsMsg.TAX_CODE_NOT_NONE})
        try:
            validate_data['price_list_mapped'] = Price.objects.filter_on_company(is_default=True).first()
        except Price.DoesNotExist:
            raise serializers.ValidationError({"price_list_mapped": AccountsMsg.PRICE_LIST_DEFAULT_NOT_EXIST})
        try:
            validate_data['currency'] = Currency.objects.filter_on_company(is_primary=True).first()
        except Currency.DoesNotExist:
            raise serializers.ValidationError({"currency": AccountsMsg.CURRENCY_DEFAULT_NOT_EXIST})
        return validate_data

    def create(self, validated_data):
        contact_mapped = validated_data.pop('contact_mapped', [])
        account = Account.objects.create(**validated_data)
        AccountCommonFunc.add_employee_map_account(account)
        AccountCommonFunc.add_account_types(account)
        AccountCommonFunc.update_account_type_fields(account)
        AccountCommonFunc.add_shipping_address(account, self.initial_data.get('shipping_address_dict', []))
        AccountCommonFunc.add_billing_address(account, self.initial_data.get('billing_address_dict', []))
        AccountCommonFunc.add_contact_mapped(account, contact_mapped)
        CompanyFunctionNumber.auto_code_update_latest_number(app_code='account')
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
    revenue_information = serializers.SerializerMethodField()

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
            'activity',
            'revenue_information'
        )

    @classmethod
    def get_account_group(cls, obj):
        return {
            'id': obj.account_group_id,
            'code': obj.account_group.code,
            'title': obj.account_group.title,
        } if obj.account_group else {}

    @classmethod
    def get_currency(cls, obj):
        return {
            'id': obj.currency_id,
            'abbreviation': obj.currency.abbreviation,
            'title': obj.currency.title,
        } if obj.currency else {}

    @classmethod
    def get_price_list_mapped(cls, obj):
        return {
            'id': obj.price_list_mapped_id,
            'title': obj.price_list_mapped.title,
        } if obj.price_list_mapped else {}

    @classmethod
    def get_industry(cls, obj):
        return {
            'id': obj.industry_id,
            'code': obj.industry.code,
            'title': obj.industry.title,
        } if obj.industry else {}

    @classmethod
    def get_parent_account_mapped(cls, obj):
        return {
            'id': obj.parent_account_mapped_id,
            'code': obj.parent_account_mapped.code,
            'name': obj.parent_account_mapped.name,
        } if obj.parent_account_mapped else {}

    @classmethod
    def get_payment_term_customer_mapped(cls, obj):
        return {
            'id': str(obj.payment_term_customer_mapped_id),
            'title': obj.payment_term_customer_mapped.title
        } if obj.payment_term_customer_mapped else {}

    @classmethod
    def get_payment_term_supplier_mapped(cls, obj):
        return {
            'id': str(obj.payment_term_supplier_mapped_id),
            'title': obj.payment_term_supplier_mapped.title
        } if obj.payment_term_supplier_mapped else {}

    @classmethod
    def get_contact_mapped(cls, obj):
        list_contact_mapped = []
        for item in obj.contact_account_name.all():
            if item.is_primary:
                list_contact_mapped.insert(
                    0, ({
                        'id': item.id,
                        'code': item.code,
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
                list_contact_mapped.append({
                    'id': item.id,
                    'code': item.code,
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
        return list_contact_mapped

    @classmethod
    def get_shipping_address(cls, obj):
        return [{
            'id': item.id,
            'country_id': item.country_id,
            'city_id': item.city_id,
            'district_id': item.district_id,
            'ward_id': item.ward_id,
            'detail_address': item.detail_address,
            'full_address': item.full_address,
            'is_default': item.is_default
        } for item in obj.account_mapped_shipping_address.all()]

    @classmethod
    def get_billing_address(cls, obj):
        return [{
            'id': item.id,
            'account_name': item.account_name,
            'email': item.email,
            'tax_code': item.tax_code,
            'account_address': item.account_address,
            'full_address': item.full_address,
            'is_default': item.is_default
        } for item in obj.account_mapped_billing_address.all()]

    @classmethod
    def get_bank_accounts_mapped(cls, obj):
        return [{
            'bank_country_id': item.country_id,
            'bank_name': item.bank_name,
            'bank_code': item.bank_code,
            'bank_account_name': item.bank_account_name,
            'bank_account_number': item.bank_account_number,
            'bic_swift_code': item.bic_swift_code,
            'is_default': item.is_default
        } for item in obj.account_banks_mapped.all()]

    @classmethod
    def get_credit_cards_mapped(cls, obj):
        return [{
            'credit_card_type': ['Mastercard', 'Visa', 'American express'][item.credit_card_type - 1],
            'credit_card_number': item.credit_card_number,
            'credit_card_name': item.credit_card_name,
            'card_expired_date': item.expired_date,
            'is_default': item.is_default
        } for item in obj.credit_cards_mapped.all()]

    @classmethod
    def get_activity(cls, obj):
        return [{
            'app_code': activity.app_code,
            'document_id': activity.document_id,
            'title': activity.title,
            'code': activity.code,
            'date_activity': activity.date_activity,
            'revenue': activity.revenue,
        } for activity in obj.account_activity_account.all()]

    @classmethod
    def get_revenue_information(cls, obj):
        current_date = timezone.now()
        this_period = Periods.get_current_period(obj.tenant_id, obj.company_id)
        revenue_ytd = 0
        order_number = 0
        if this_period:
            for period in obj.company.saledata_periods_belong_to_company.all():
                if period.fiscal_year == this_period.fiscal_year:
                    start_date_str = str(period.start_date) + ' 00:00:00'
                    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
                    for customer_revenue in obj.report_customer_customer.filter(
                            group_inherit__is_delete=False, sale_order__system_status=3
                    ):
                        if (customer_revenue.date_approved and
                                start_date <= customer_revenue.date_approved <= current_date):
                            revenue_ytd += customer_revenue.revenue
                            order_number += 1
        return {
            'revenue_ytd': revenue_ytd,
            'order_number': order_number,
            'revenue_average': round(revenue_ytd / order_number) if order_number > 0 else 0,
        }


class AccountUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=150)
    tax_code = serializers.CharField(max_length=150, required=False, allow_null=True, allow_blank=True)
    account_group = serializers.UUIDField(required=False, allow_null=True)
    industry = serializers.UUIDField(required=False, allow_null=True)
    account_type = serializers.ListField(child=serializers.UUIDField(required=True))
    manager = serializers.ListField(child=serializers.UUIDField(required=False), required=False)
    parent_account_mapped = serializers.UUIDField(required=False, allow_null=True)
    contact_mapped = serializers.ListField(required=False)
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
            'contact_mapped',
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

    def validate_tax_code(self, value):
        if value:
            if Account.objects.filter_on_company(tax_code=value).exclude(id=self.instance.id).count() > 0:
                raise serializers.ValidationError({"tax_code": AccountsMsg.TAX_CODE_IS_EXIST})
            return value
        return ''

    @classmethod
    def validate_account_type(cls, value):
        if isinstance(value, list):
            if len(value) == 0:
                raise serializers.ValidationError({'account_type': _('Account type is required')})
            account_type = AccountType.objects.filter(id__in=value)
            if account_type.count() == len(value):
                return [{'id': str(item.id), 'code': item.code, 'title': item.title} for item in account_type]
            raise serializers.ValidationError({'account_type': HRMsg.ACCOUNT_TYPE_NOT_EXIST})
        raise serializers.ValidationError({'account_type': HRMsg.ACCOUNT_TYPE_IS_ARRAY})

    @classmethod
    def validate_account_group(cls, value):
        if value:
            try:
                return AccountGroup.objects.get(id=value)
            except AccountGroup.DoesNotExist:
                raise serializers.ValidationError({"account_group": AccountsMsg.ACCOUNT_GROUP_NOT_EXIST})
        raise serializers.ValidationError(AccountsMsg.ACCOUNT_GROUP_NOT_NONE)

    @classmethod
    def validate_manager(cls, value):
        if isinstance(value, list):
            if len(value) == 0:
                raise serializers.ValidationError({'manager': _('Manager is required')})
            employee_list = Employee.objects.filter(id__in=value)
            if employee_list.count() == len(value):
                return [
                    {'id': str(item.id), 'code': item.code, 'full_name': item.get_full_name(2)}
                    for item in employee_list
                ]
            raise serializers.ValidationError({'manager': HRMsg.EMPLOYEES_NOT_EXIST})
        raise serializers.ValidationError({'manager': HRMsg.EMPLOYEE_IS_ARRAY})

    @classmethod
    def validate_parent_account_mapped(cls, value):
        if value:
            try:
                return Account.objects.get(id=value)
            except AccountGroup.DoesNotExist:
                raise serializers.ValidationError({"parent_account_mapped": AccountsMsg.PARENT_ACCOUNT_NOT_EXIST})
        return None

    @classmethod
    def validate_industry(cls, value):
        if value:
            try:
                return Industry.objects.get(id=value)
            except Industry.DoesNotExist:
                raise serializers.ValidationError({"industry": AccountsMsg.INDUSTRY_NOT_EXIST})
        return None

    @classmethod
    def validate_currency(cls, value):
        if value:
            try:
                return Currency.objects.get(id=value)
            except Currency.DoesNotExist:
                raise serializers.ValidationError({"currency": AccountsMsg.CURRENCY_DEFAULT_NOT_EXIST})
        raise serializers.ValidationError({"currency": AccountsMsg.CURRENCY_NOT_NULL})

    @classmethod
    def validate_payment_term_customer_mapped(cls, value):
        if value:
            try:
                return PaymentTerm.objects.get(id=value)
            except PaymentTerm.DoesNotExist:
                raise serializers.ValidationError({"payment_term_customer_mapped": AccountsMsg.PAYMENT_TERM_NOT_EXIST})
        return None

    @classmethod
    def validate_payment_term_supplier_mapped(cls, value):
        if value:
            try:
                return PaymentTerm.objects.get(id=value)
            except PaymentTerm.DoesNotExist:
                raise serializers.ValidationError({"payment_term_supplier_mapped": AccountsMsg.PAYMENT_TERM_NOT_EXIST})
        return None

    @classmethod
    def validate_price_list_mapped(cls, value):
        if value:
            try:
                return Price.objects.get(id=value)
            except Price.DoesNotExist:
                raise serializers.ValidationError({"price_list_mapped": AccountsMsg.PRICE_LIST_DEFAULT_NOT_EXIST})
        return None

    def validate(self, validate_data):
        if validate_data.get('account_type_selection') == 0:
            if len(validate_data.get('contact_mapped', [])) != 1:
                raise serializers.ValidationError(
                    {"contact_mapped": _('Contact is required (only 1) for individual account')}
                )
            contact_mapped_obj = Contact.objects.filter_on_company(
                id=validate_data['contact_mapped'][0].get('id')
            ).first()
            if contact_mapped_obj:
                validate_data['name'] = contact_mapped_obj.fullname
                validate_data['phone'] = contact_mapped_obj.mobile
                validate_data['email'] = contact_mapped_obj.email
            else:
                raise serializers.ValidationError({"contact_mapped": AccountsMsg.CONTACT_NOT_EXIST})
        else:
            if not validate_data.get('tax_code'):
                raise serializers.ValidationError({"tax_code": AccountsMsg.TAX_CODE_NOT_NONE})
        return validate_data

    def update(self, instance, validated_data):
        contact_mapped = validated_data.pop('contact_mapped', [])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.owner = None
        instance.save()
        AccountCommonFunc.add_employee_map_account(instance)
        AccountCommonFunc.add_account_types(instance)
        AccountCommonFunc.update_account_type_fields(instance)
        AccountCommonFunc.add_shipping_address(instance, self.initial_data.get('shipping_address_dict', []))
        AccountCommonFunc.add_billing_address(instance, self.initial_data.get('billing_address_dict', []))
        AccountCommonFunc.add_contact_mapped(instance, contact_mapped)
        AccountCommonFunc.add_banking_accounts(instance, self.initial_data.get('bank_accounts_information', []))
        AccountCommonFunc.add_credit_cards(instance, self.initial_data.get('credit_cards_information', []))
        return instance


class CustomerListSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            "id",
            'code',
            "name",
            "tax_code"
        )


class SupplierListSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            "id",
            'code',
            "name",
            "tax_code"
        )


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
        } if obj.account else {}


class AccountCommonFunc:
    @staticmethod
    def add_employee_map_account(account):
        AccountEmployee.objects.filter(account=account).delete()
        AccountEmployee.objects.bulk_create(
            AccountEmployee(account=account, employee_id=manager_obj.get('id')) for manager_obj in account.manager
        )
        return True

    @staticmethod
    def add_banking_accounts(account, banking_accounts_list):
        AccountBanks.objects.filter(account=account).delete()
        AccountBanks.objects.bulk_create(
            AccountBanks(**item, account=account) for item in banking_accounts_list
        )
        return True

    @staticmethod
    def add_credit_cards(account, credit_cards_list):
        bulk_info = []
        for item in credit_cards_list:
            if item.get('credit_card_type') == 'Mastercard':
                item['credit_card_type'] = 1
            if item.get('credit_card_type') == 'Visa':
                item['credit_card_type'] = 2
            if item.get('credit_card_type') == 'American express':
                item['credit_card_type'] = 3
            bulk_info.append(AccountCreditCards(**item, account=account))
        AccountCreditCards.objects.filter(account=account).delete()
        AccountCreditCards.objects.bulk_create(bulk_info)
        return True

    @staticmethod
    def add_account_types(account):
        AccountAccountTypes.objects.filter(account=account).delete()
        AccountAccountTypes.objects.bulk_create(
            AccountAccountTypes(account=account, account_type_id=account_type_obj.get('id'))
            for account_type_obj in account.account_type
        )
        return True

    @staticmethod
    def add_contact_mapped(account, contact_mapped):
        account.contact_account_name.all().update(account_name=None)
        for item in contact_mapped:
            contact = Contact.objects.filter(id=item.get('id')).first()
            if contact:
                contact.account_name = account
                if item.get('is_account_owner'):
                    contact.is_primary = True
                    account.owner = contact
                    account.save()
                else:
                    contact.is_primary = False
                contact.save()
            else:
                raise serializers.ValidationError({"contact": AccountsMsg.CONTACT_NOT_EXIST})
        return True

    @staticmethod
    def add_shipping_address(account, shipping_address_list):
        AccountShippingAddress.objects.filter(account=account).delete()
        AccountShippingAddress.objects.bulk_create(
            AccountShippingAddress(**item, account=account) for item in shipping_address_list
        )
        return True

    @staticmethod
    def add_billing_address(account, billing_address_list):
        AccountBillingAddress.objects.filter(account=account).delete()
        AccountBillingAddress.objects.bulk_create(
            AccountBillingAddress(**item, account=account) for item in billing_address_list
        )
        return True

    @staticmethod
    def update_account_type_fields(instance):
        account_type_data = {
            'is_customer_account': False,
            'is_supplier_account': False,
            'is_partner_account': False,
            'is_competitor_account': False
        }
        for item in instance.account_account_types_mapped.all():
            if item.account_type.account_type_order == 0:
                account_type_data['is_customer_account'] = True
            elif item.account_type.account_type_order == 1:
                account_type_data['is_supplier_account'] = True
            elif item.account_type.account_type_order == 2:
                account_type_data['is_partner_account'] = True
            elif item.account_type.account_type_order == 3:
                account_type_data['is_competitor_account'] = True
        for key, value in account_type_data.items():
            setattr(instance, key, value)
        instance.save(update_fields=list(account_type_data.keys()))
        return True


# Serializer use for sale apps
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
            'title',
        )


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
        return [{
            'id': shipping.id, 'full_address': shipping.full_address
        } for shipping in obj.account_mapped_shipping_address.all()]

    @classmethod
    def get_billing_address(cls, obj):
        return [{
            'id': billing.id, 'full_address': billing.full_address
        } for billing in obj.account_mapped_billing_address.all()]

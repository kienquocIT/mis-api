from rest_framework import serializers
from apps.core.hr.models import Employee
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models.accounts import (
    AccountType, Industry, Account, AccountEmployee, AccountGroup, AccountAccountTypes, AccountBanks,
    AccountCreditCards, AccountShippingAddress, AccountBillingAddress,
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
    shipping_address = serializers.JSONField()
    billing_address = serializers.JSONField()

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
            "bank_accounts_information",
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


def create_employee_map_account(instance):
    bulk_info = []
    for manager in instance.manager:
        bulk_info.append(
            AccountEmployee(
                account=instance,
                employee_id=manager.get('id', None)
            )
        )
    if len(bulk_info) > 0:
        AccountEmployee.objects.filter(account=instance).delete()
        AccountEmployee.objects.bulk_create(bulk_info)
    return True


def update_account_owner(instance, account_owner):
    Contact.objects.filter_current(fill__tenant=True, fill__company=True, account_name=instance).update(
        account_name=None,
        is_primary=False
    )
    instance.owner = None
    instance.save()
    if account_owner:
        Contact.objects.filter_current(fill__tenant=True, fill__company=True, id=account_owner).update(
            account_name=instance,
            is_primary=True
        )
        instance.owner_id = account_owner
        instance.save()
    return True


def add_banking_accounts_information(instance, banking_accounts_list):
    bulk_info = []
    for item in banking_accounts_list:
        if item['bank_name'] and item['bank_code'] and item['bank_account_name'] and item['bank_account_number']:
            bulk_info.append(
                AccountBanks(**item, account=instance)
            )
        else:
            raise serializers.ValidationError(AccountsMsg.BANK_ACCOUNT_MISSING_VALUE)
    if len(bulk_info) > 0:
        AccountBanks.objects.filter(account=instance).delete()
        AccountBanks.objects.bulk_create(bulk_info)
    return True


def add_credit_cards_information(instance, credit_cards_list):
    bulk_info = []
    for item in credit_cards_list:
        if item['credit_card_type'] and item['credit_card_number'] and item['credit_card_name'] \
                and item['expired_date']:
            bulk_info.append(
                AccountCreditCards(**item, account=instance)
            )
        else:
            raise serializers.ValidationError(AccountsMsg.CREDIT_CARD_MISSING_VALUE)
    if len(bulk_info) > 0:
        AccountCreditCards.objects.filter(account=instance).delete()
        AccountCreditCards.objects.bulk_create(bulk_info)
    return True


def add_account_types_information(account_types_list, account):
    bulk_info = []
    for item in account_types_list:
        bulk_info.append(AccountAccountTypes(account=account, account_type_id=item['id']))
    if len(bulk_info) > 0:
        AccountAccountTypes.objects.filter(account=account).delete()
        AccountAccountTypes.objects.bulk_create(bulk_info)
    return True


def add_shipping_address_information(instance, shipping_address_sub_create_list):
    AccountShippingAddress.objects.filter(account=instance).exclude(full_address__in=instance.shipping_address).delete()
    bulk_info = []
    for item in shipping_address_sub_create_list:
        if not AccountShippingAddress.objects.filter(**item).exists():
            bulk_info.append(AccountShippingAddress(**item, account=instance))
    AccountShippingAddress.objects.bulk_create(bulk_info)
    # update default
    if len(instance.shipping_address) > 0:
        AccountShippingAddress.objects.filter(account=instance).update(is_default=False)
        AccountShippingAddress.objects.filter(
            account=instance,
            full_address=instance.shipping_address[0]
        ).update(is_default=True)
    return True


def add_billing_address_information(instance, billing_address_sub_create_list):
    AccountBillingAddress.objects.filter(account=instance).exclude(full_address__in=instance.billing_address).delete()
    bulk_info = []
    for item in billing_address_sub_create_list:
        if not item['account_name_id']:
            item['account_name_id'] = instance.id
        if not AccountBillingAddress.objects.filter(**item).exists():
            bulk_info.append(AccountBillingAddress(**item, account=instance))
    AccountBillingAddress.objects.bulk_create(bulk_info)
    # update default
    if len(instance.billing_address) > 0:
        AccountBillingAddress.objects.filter(account=instance).update(is_default=False)
        AccountBillingAddress.objects.filter(
            account=instance,
            full_address=instance.billing_address[0]
        ).update(is_default=True)
    return True


class AccountCreateSerializer(serializers.ModelSerializer):
    contact_select_list = serializers.ListField(
        child=serializers.UUIDField(required=False),
        required=False
    )
    manager = serializers.JSONField()
    contact_primary = serializers.UUIDField(required=False)
    parent_account = serializers.UUIDField(required=False, allow_null=True)
    name = serializers.CharField(max_length=150)
    code = serializers.CharField(max_length=150)
    account_type = serializers.JSONField()
    system_status = serializers.ChoiceField(
        choices=[0, 1],
        help_text='0: draft, 1: created',
        default=0,
    )

    class Meta:
        model = Account
        fields = (
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
            'contact_select_list',
            'contact_primary',
            'account_type_selection',
            'system_status',
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

    @classmethod
    def validate_manager(cls, value):
        if isinstance(value, list):
            employee_list = Employee.objects.filter(id__in=value)
            if employee_list.count() == len(value):
                return [
                    {'id': str(employee.id), 'code': employee.code, 'fullname': employee.get_full_name(2)}
                    for employee in employee_list
                ]
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEES_NOT_EXIST})
        raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_IS_ARRAY})

    def validate(self, validate_data):
        account_types = []
        for item in validate_data.get('account_type', None):
            account_type = AccountType.objects.filter_current(fill__tenant=True, fill__company=True, id=item).first()
            if account_type:
                account_types.append(
                    {'id': str(item), 'code': account_type.code, 'title': account_type.title}
                )
                tax_code = validate_data.get('tax_code', None)
                if validate_data['account_type_selection'] == 1:  # tax_code is required
                    if not tax_code:
                        raise serializers.ValidationError(AccountsMsg.TAX_CODE_NOT_NONE)
                elif validate_data['account_type_selection'] == 0:
                    validate_data.update({'parent_account': None})

                if tax_code:
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

    @decorator_run_workflow
    def create(self, validated_data):
        """
        step 1: contact_select_list: get list contact selected
        step 2: get primary contact
        step 3: contact_select_list = contact_select_list append primary contact
        step 4: update is_primary in which id == primary
        """
        contact_select_list = []
        contact_primary = []
        if 'contact_select_list' in validated_data:
            contact_select_list = validated_data.get('contact_select_list', [])
            del validated_data['contact_select_list']
        if 'contact_primary' in validated_data:
            contact_primary = validated_data.get('contact_primary', [])
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
                is_default=True
            ).first()
        else:
            default_currency = validated_data['currency']

        account = Account.objects.create(
            **validated_data,
            price_list_mapped=default_price_list,
            currency=default_currency,
        )
        # add employee information
        create_employee_map_account(account)
        # add account type detail information
        add_account_types_information(validated_data.get('account_type', []), account)
        # add shipping address
        add_shipping_address_information(account, self.initial_data.get('shipping_address_id_dict', []))
        # add billing address
        add_billing_address_information(account, self.initial_data.get('billing_address_id_dict', []))

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
                    account.owner = contact_list[0]
                    account.save()
                else:
                    for contact in contact_list:
                        if contact.id == contact_primary:
                            contact.is_primary = True
                        contact.account_name = account
                        contact.save()
        return account


class AccountDetailSerializer(AbstractDetailSerializerModel):
    contact_mapped = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

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
            'payment_term_mapped',
            'price_list_mapped',
            'credit_limit',
            'currency',
            'owner',
            'contact_mapped',
            'bank_accounts_information',
            'credit_cards_information',
            'account_type_selection',
            'workflow_runtime_id',
        )

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
                                'mobile': i.mobile
                            })
                    )
                else:
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


class AccountUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=150)
    manager = serializers.JSONField()
    account_type = serializers.JSONField()
    parent_account = serializers.UUIDField(required=False, allow_null=True)
    bank_accounts_information = serializers.JSONField()
    credit_cards_information = serializers.JSONField()
    contact_list = serializers.ListField(required=False)
    owner_id = serializers.CharField(required=False)

    class Meta:
        model = Account
        fields = (
            'name',
            'website',
            'account_type',
            'manager',
            'owner_id',
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
            'credit_cards_information',
            'account_type_selection',
            'contact_list'
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
                if key != 'bic_swift_code':
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

    @classmethod
    def validate_manager(cls, value):
        if isinstance(value, list):
            employee_list = Employee.objects.filter(id__in=value)
            if employee_list.count() == len(value):
                return [
                    {'id': str(employee.id), 'code': employee.code, 'fullname': employee.get_full_name(2)}
                    for employee in employee_list
                ]
            raise serializers.ValidationError({'detail': HRMsg.EMPLOYEES_NOT_EXIST})
        raise serializers.ValidationError({'detail': HRMsg.EMPLOYEE_IS_ARRAY})

    def validate(self, validate_data):
        account_types = []
        for item in validate_data.get('account_type', []):
            account_type = AccountType.objects.filter_current(fill__tenant=True, fill__company=True, id=item).first()
            if account_type:
                account_types.append(
                    {'id': str(item), 'code': account_type.code, 'title': account_type.title}
                )
                tax_code = validate_data.get('tax_code', None)
                if validate_data['account_type_selection'] == 1:  # tax_code is required
                    if not tax_code:
                        raise serializers.ValidationError(AccountsMsg.TAX_CODE_NOT_NONE)
                elif validate_data['account_type_selection'] == 0:
                    validate_data.update({'parent_account': None})

                if tax_code:
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

    @classmethod
    def update_contact(cls, instance, data):
        Contact.objects.filter(account_name=instance).update(account_name=None)
        for item in data:
            contact = Contact.objects.get(id=item['id'])
            contact.account_name = instance
            contact.is_primary = item['is_primary']
            contact.save()
        return True

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # recreate in AccountEmployee (Account Manager)
        create_employee_map_account(instance)
        # add account type detail information
        add_account_types_information(validated_data.get('account_type', []), instance)
        # add shipping address
        add_shipping_address_information(instance, self.initial_data.get('shipping_address_id_dict', []))
        # add billing address
        add_billing_address_information(instance, self.initial_data.get('billing_address_id_dict', []))
        # add banking accounts
        add_banking_accounts_information(instance, validated_data.get('bank_accounts_information', []))
        # add credit cards
        add_credit_cards_information(instance, validated_data.get('credit_cards_information', []))

        # update contact
        if 'contact_list' in validated_data:
            data_contact = validated_data.pop('contact_list')
            self.update_contact(instance, data_contact)
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
    shipping_address = serializers.JSONField()
    billing_address = serializers.JSONField()
    payment_term_mapped = serializers.SerializerMethodField()
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
            "bank_accounts_information",
            "payment_term_mapped",
            "price_list_mapped"
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
    def get_payment_term_mapped(cls, obj):
        if obj.payment_term_mapped:
            return {
                'id': obj.payment_term_mapped_id,
                'title': obj.payment_term_mapped.title,
                'code': obj.payment_term_mapped.code
            }
        return {}

    @classmethod
    def get_price_list_mapped(cls, obj):
        if obj.price_list_mapped:
            return {
                'id': obj.price_list_mapped_id,
                'title': obj.price_list_mapped.title,
                'code': obj.price_list_mapped.code
            }
        return {}

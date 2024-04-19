from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.masterdata.saledata.models.price import Price, Currency
from apps.masterdata.saledata.models.config import PaymentTerm
from apps.masterdata.saledata.models.contacts import Contact
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SimpleAbstractModel

__all__ = [
    'AccountType',
    'AccountGroup',
    'Industry',
    'Account',
    'AccountEmployee',
    'AccountBanks',
    'AccountCreditCards',
    'AccountAccountTypes',
    'AccountShippingAddress',
    'AccountBillingAddress',
    'Contact',
    'PaymentTerm',
    'ANNUAL_REVENUE_SELECTION',
    'AccountActivity',
]


ACCOUNT_TYPE_ORDER = [
    (0, _('Customer')),
    (1, _('Supplier')),
    (2, _('Partner')),
    (3, _('Competitor')),
]

ACCOUNT_TYPE_SELECTION = [
    (0, _('individual')),
    (1, _('organization')),
]

ANNUAL_REVENUE_SELECTION = [
    (1, _('1-10 billions')),
    (2, _('10-20 billions')),
    (3, _('20-50 billions')),
    (4, _('50-200 billions')),
    (5, _('200-1000 billions')),
    (6, _('> 1000 billions')),
]

TOTAL_EMPLOYEES_SELECTION = [
    (1, _('< 20 people')),
    (2, _('20-50 people')),
    (3, _('50-200 people')),
    (4, _('200-500 people')),
    (5, _('> 500 people')),
]

CREDIT_CARD_TYPES = [
    (1, _('Mastercard')),
    (2, _('Visa')),
    (3, _('American express')),
]


# Create your models here.
class AccountType(MasterDataAbstractModel):
    description = models.CharField(blank=True, max_length=200)
    is_default = models.BooleanField(default=False)
    account_type_order = models.IntegerField(choices=ACCOUNT_TYPE_ORDER, null=True)

    class Meta:
        verbose_name = 'AccountType'
        verbose_name_plural = 'AccountTypes'
        ordering = ('code',)
        default_permissions = ()
        permissions = ()


class AccountGroup(MasterDataAbstractModel):
    description = models.CharField(blank=True, max_length=200)

    class Meta:
        verbose_name = 'AccountGroup'
        verbose_name_plural = 'AccountGroups'
        ordering = ('code',)
        unique_together = ('company', 'code')
        default_permissions = ()
        permissions = ()


class Industry(MasterDataAbstractModel):
    description = models.CharField(blank=True, max_length=200)

    class Meta:
        verbose_name = 'Industry'
        verbose_name_plural = 'Industries'
        ordering = ('code',)
        unique_together = ('company', 'code')
        default_permissions = ()
        permissions = ()


# Accounts
class Account(DataAbstractModel):
    avatar = models.TextField(
        null=True,
        verbose_name='avatar path'
    )
    name = models.CharField(
        verbose_name='account name',
        blank=True,
        null=True,
        max_length=150
    )
    code = models.CharField(
        verbose_name='account code',
        blank=True,
        null=True,
        max_length=150
    )
    website = models.CharField(
        verbose_name='account website',
        blank=True,
        null=True,
        max_length=150
    )
    account_type = models.JSONField(
        default=list
    )
    account_type_selection = models.SmallIntegerField(choices=ACCOUNT_TYPE_SELECTION, default=1)
    account_group = models.ForeignKey(
        AccountGroup,
        on_delete=models.CASCADE,
        null=True
    )
    owner = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        null=True
    )
    manager = models.JSONField(
        default=list
    )
    employee = models.ManyToManyField(
        'hr.Employee',
        through='AccountEmployee',
        symmetrical=False,
        blank=True,
        related_name='account_map_employee'
    )
    account_types_mapped = models.ManyToManyField(
        AccountType,
        through='AccountAccountTypes',
        symmetrical=False,
        blank=True,
        related_name='account_map_account_types'
    )
    parent_account = models.CharField(
        verbose_name='parent account',
        null=True,
        max_length=150
    )
    parent_account_mapped = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True
    )
    tax_code = models.CharField(
        verbose_name='tax code',
        blank=True,
        null=True,
        max_length=150
    )
    industry = models.ForeignKey(
        'saledata.Industry',
        on_delete=models.CASCADE,
        null=False
    )
    # annual_revenue = models.SmallIntegerField(choices=ANNUAL_REVENUE_SELECTION, null=True)
    # total_employees = models.SmallIntegerField(choices=TOTAL_EMPLOYEES_SELECTION, default=1)
    annual_revenue = models.CharField(
        choices=ANNUAL_REVENUE_SELECTION,
        verbose_name='annual revenue of account',
        blank=True,
        null=True,
        max_length=150
    )
    total_employees = models.CharField(
        choices=TOTAL_EMPLOYEES_SELECTION,
        verbose_name='total employees of account',
        null=True,
        max_length=150
    )
    phone = models.CharField(
        verbose_name='account phone number',
        blank=True,
        null=True,
        max_length=25
    )
    email = models.CharField(
        verbose_name='account email',
        blank=True,
        null=True,
        max_length=150
    )
    payment_term_customer_mapped = models.ForeignKey(
        PaymentTerm,
        on_delete=models.CASCADE,
        null=True,
        related_name='payment_term_customer_mapped'
    )
    price_list_mapped = models.ForeignKey(Price, on_delete=models.CASCADE, null=True)
    credit_limit_customer = models.FloatField(null=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)

    payment_term_supplier_mapped = models.ForeignKey(
        PaymentTerm,
        on_delete=models.CASCADE,
        null=True,
        related_name='payment_term_supplier_mapped'
    )
    credit_limit_supplier = models.FloatField(null=True)

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ('-date_created',)
        unique_together = ('company', 'code')
        default_permissions = ()
        permissions = ()


# AccountEmployee
class AccountEmployee(SimpleAbstractModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_employees_mapped')
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Account Employee'
        verbose_name_plural = 'Accounts Employees'
        default_permissions = ()
        permissions = ()


# AccountBanks
class AccountBanks(SimpleAbstractModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_banks_mapped')
    country = models.ForeignKey('base.Country', on_delete=models.CASCADE)
    bank_name = models.CharField(
        verbose_name='Name of bank',
        blank=True,
        null=True,
        max_length=150
    )
    bank_code = models.CharField(
        verbose_name='Code of bank',
        blank=True,
        null=True,
        max_length=50
    )
    bank_account_name = models.CharField(
        verbose_name='Bank account name',
        blank=True,
        null=True,
        max_length=150
    )
    bank_account_number = models.CharField(
        verbose_name='Bank account number',
        blank=True,
        null=True,
        max_length=150
    )
    bic_swift_code = models.CharField(
        verbose_name='BIC/SWIFT code',
        blank=True,
        null=True,
        max_length=150
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Account Banks'
        verbose_name_plural = 'Accounts Banks'
        default_permissions = ()
        permissions = ()


# AccountCreditCards
class AccountCreditCards(SimpleAbstractModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='credit_cards_mapped')
    credit_card_type = models.SmallIntegerField(
        verbose_name='Credit card type',
        choices=CREDIT_CARD_TYPES,
        default=0
    )
    credit_card_number = models.CharField(
        verbose_name='Credit card number',
        blank=True,
        null=True,
        max_length=150
    )
    credit_card_name = models.CharField(
        verbose_name='Credit card name',
        blank=True,
        null=True,
        max_length=150
    )
    expired_date = models.CharField(
        verbose_name='EXP date',
        blank=True,
        null=True,
        max_length=10
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Account Credit Cards'
        verbose_name_plural = 'Accounts Credit Cards'
        default_permissions = ()
        permissions = ()


# AccountAccountTypes
class AccountAccountTypes(SimpleAbstractModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_account_types_mapped')
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Account AccountTypes'
        verbose_name_plural = 'Accounts AccountTypes'
        default_permissions = ()
        permissions = ()


# AccountShippingAddress
class AccountShippingAddress(SimpleAbstractModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="account_mapped_shipping_address")
    country = models.ForeignKey('base.Country', on_delete=models.CASCADE)
    detail_address = models.CharField(
        verbose_name='Detail address',
        blank=True,
        null=True,
        max_length=150
    )
    city = models.ForeignKey('base.City', on_delete=models.CASCADE)
    district = models.ForeignKey('base.District', on_delete=models.CASCADE)
    ward = models.ForeignKey('base.Ward', on_delete=models.CASCADE, null=True)
    full_address = models.CharField(
        verbose_name='Full address',
        blank=True,
        max_length=500
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Account Shipping Address'
        verbose_name_plural = 'Account Shipping Addresses'
        default_permissions = ()
        permissions = ()


# AccountShippingAddress
class AccountBillingAddress(SimpleAbstractModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="account_mapped_billing_address")
    account_name = models.CharField(
        verbose_name='billing account name',
        blank=True,
        null=True,
        max_length=150
    )
    email = models.CharField(
        verbose_name='account email',
        blank=True,
        null=True,
        max_length=150
    )
    tax_code = models.CharField(
        verbose_name='tax code',
        blank=True,
        null=True,
        max_length=150
    )
    account_address = models.CharField(
        verbose_name='Account address',
        blank=True,
        null=True,
        max_length=150
    )
    full_address = models.CharField(
        verbose_name='Full address',
        blank=True,
        max_length=500
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Account Billing Address'
        verbose_name_plural = 'Account Billing Addresses'
        default_permissions = ()
        permissions = ()


# Account activity
class AccountActivity(MasterDataAbstractModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="account_activity_account")
    app_code = models.CharField(
        max_length=100,
        verbose_name='Code of application',
        help_text='{app_label}.{model}',
        null=True,
    )
    document_id = models.UUIDField(verbose_name='Document that has foreign key to customer', null=True)
    date_activity = models.DateTimeField(null=True, help_text='date of activity (date_created, date_approved,...)')
    revenue = models.FloatField(null=True)

    @classmethod
    def push_activity(
            cls,
            tenant_id,
            company_id,
            account_id,
            app_code,
            document_id,
            title,
            code,
            date_activity,
            revenue,
    ):
        cls.objects.create(
            tenant_id=tenant_id,
            company_id=company_id,
            account_id=account_id,
            app_code=app_code,
            document_id=document_id,
            title=title,
            code=code,
            date_activity=date_activity,
            revenue=revenue,
        )
        return True

    class Meta:
        verbose_name = 'Account Activity'
        verbose_name_plural = 'Account Activities'
        ordering = ('-date_activity',)
        default_permissions = ()
        permissions = ()

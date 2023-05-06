from django.db import models
from apps.masterdata.saledata.models.price import Price
from apps.masterdata.saledata.models.config import PaymentTerm
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SimpleAbstractModel

__all__ = ['Salutation', 'Interest', 'AccountType', 'AccountGroup', 'Industry', 'Account', 'AccountEmployee', 'Contact']


# Create your models here.
class Salutation(MasterDataAbstractModel):  # noqa
    description = models.CharField(blank=True, max_length=200)

    class Meta:
        verbose_name = 'Salutation'
        verbose_name_plural = 'Salutations'
        ordering = ('code',)
        default_permissions = ()
        permissions = ()


class Interest(MasterDataAbstractModel):
    description = models.CharField(blank=True, max_length=200)

    class Meta:
        verbose_name = 'Interest'
        verbose_name_plural = 'Interests'
        ordering = ('code',)
        default_permissions = ()
        permissions = ()


class AccountType(MasterDataAbstractModel):
    description = models.CharField(blank=True, max_length=200)

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
        default_permissions = ()
        permissions = ()


class Industry(MasterDataAbstractModel):
    description = models.CharField(blank=True, max_length=200)

    class Meta:
        verbose_name = 'Industry'
        verbose_name_plural = 'Industries'
        ordering = ('code',)
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
    # [
    #   {"title": "Customer", "detail": "individual/organization"},
    #   {"title": "Personal", "detail": ""},
    # ]
    account_type = models.JSONField(
        default=list
    )
    account_group = models.ForeignKey(
        AccountGroup,
        on_delete=models.CASCADE,
        null=True
    )
    # ["e3e416d7-ae74-4bb8-a55f-169c5fde53a0", "d2f9397d-3a6c-46d6-9a67-442bc43554a8"]
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
    bank_accounts_information = models.JSONField(
        default=list
    )
    credit_cards_information = models.JSONField(
        default=list
    )
    parent_account = models.CharField(
        verbose_name='parent account',
        null=True,
        max_length=150
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
    annual_revenue = models.CharField(
        verbose_name='annual revenue of account',
        blank=True,
        null=True,
        max_length=150
    )
    total_employees = models.CharField(
        verbose_name='total employees of account',
        null=False,
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
    payment_term_mapped = models.ForeignKey(PaymentTerm, on_delete=models.CASCADE, null=True)
    price_list_mapped = models.ForeignKey(Price, on_delete=models.CASCADE, null=True)
    credit_limit = models.FloatField(null=True)

    # [
    #   "Số 2/8, Xã Định An, Huyện Dầu Tiếng, Bình Dương",
    #   "Số 22/20, Phường Lê Hồng Phong, Thành Phố Phủ Lý, Hà Nam"
    # ]
    # địa chỉ đầu tiên là default
    shipping_address = models.JSONField(
        default=list,
    )

    # [
    #   "Tầng 2, TGDD, Số 22/20, xã Bình Hưng, huyện Bình Chánh, TP HCM (email: tgdd@gmail.com, tax code: 123123)"
    #   "Tầng 10, TGDD, Số 7/10, xã Bình Hưng, huyện Bình Chánh, TP HCM (email: tgdd@gmail.com, tax code: 123123)"
    # ]
    # địa chỉ đầu tiên là default
    billing_address = models.JSONField(
        default=list,
    )

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


# AccountEmployee
class AccountEmployee(SimpleAbstractModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)


# AccountBanks
class AccountBanks(SimpleAbstractModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
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


# AccountCreditCards
class AccountCreditCards(SimpleAbstractModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    credit_card_type = models.CharField(
        verbose_name='Credit card type',
        blank=True,
        null=True,
        max_length=150
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


# Contact
class Contact(DataAbstractModel):
    owner = models.UUIDField(
        help_text='employee is contact owner'
    )
    biography = models.CharField(
        blank=True,
        null=True,
        max_length=150
    )
    avatar = models.TextField(
        null=True,
        verbose_name='avatar path'
    )
    fullname = models.CharField(
        verbose_name='contact fullname',
        null=False,
        max_length=150
    )
    salutation = models.ForeignKey(
        'saledata.Salutation',
        on_delete=models.CASCADE,
        null=True
    )
    phone = models.CharField(
        verbose_name='contact phone number',
        blank=True,
        null=True,
        max_length=25
    )
    mobile = models.CharField(
        verbose_name='contact mobile',
        blank=True,
        null=True,
        max_length=25
    )
    account_name = models.ForeignKey(
        'saledata.Account',
        verbose_name='account name',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='contact_account_name'
    )
    email = models.CharField(
        verbose_name='contact email',
        blank=True,
        null=True,
        max_length=150
    )
    job_title = models.CharField(
        verbose_name='contact job title',
        blank=True,
        null=True,
        max_length=150
    )
    report_to = models.UUIDField(
        null=True,
        blank=True,
        help_text='report to a contact'
    )

    # {
    #   "work_address": "Số 2/8, Xã Định An, Huyện Dầu Tiếng, Bình Dương",
    #   "home_address": "Số 22/20, Phường Lê Hồng Phong, Thành Phố Phủ Lý, Hà Nam"
    # }
    address_information = models.JSONField(
        default=dict,
    )

    # {
    #   'facebook': 'nva.facebook.com',
    #   'twitter': 'nva.twitter.com',
    #   'linkedln': 'nva.linkedln.com',
    #   'gmail': 'nva@gmail.com',
    #   'interests': ["e3e416d7-ae74-4bb8-a55f-169c5fde53a0", "d2f9397d-3a6c-46d6-9a67-442bc43554a8"],
    #   'tags': 'tags',
    # }
    additional_information = models.JSONField(
        default=dict,
    )
    is_primary = models.BooleanField(
        help_text='is account owner',
        default=False
    )

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

from django.db import models
from apps.shared.models import MasterDataModel, TenantModel


# Create your models here.
class Salutation(MasterDataModel):
    description = models.CharField(verbose_name='description', blank=True, max_length=200)
    user_created = models.UUIDField(null=True)
    user_modified = models.UUIDField(null=True)

    class Meta:
        verbose_name = 'Salutation'
        verbose_name_plural = 'Salutations'
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        super(Salutation, self).save(*args, **kwargs)


class Interest(MasterDataModel):
    description = models.CharField(verbose_name='description', blank=True, max_length=200)
    user_created = models.UUIDField(null=True)
    user_modified = models.UUIDField(null=True)

    class Meta:
        verbose_name = 'Interest'
        verbose_name_plural = 'Interests'
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        super(Interest, self).save(*args, **kwargs)


class AccountType(MasterDataModel):
    description = models.CharField(verbose_name='description', blank=True, max_length=200)
    user_created = models.UUIDField(null=True)
    user_modified = models.UUIDField(null=True)

    class Meta:
        verbose_name = 'AccountType'
        verbose_name_plural = 'AccountTypes'
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        super(AccountType, self).save(*args, **kwargs)


class Industry(MasterDataModel):
    description = models.CharField(verbose_name='description', blank=True, max_length=200)
    user_created = models.UUIDField(null=True)
    user_modified = models.UUIDField(null=True)

    class Meta:
        verbose_name = 'Industry'
        verbose_name_plural = 'Industries'
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        super(Industry, self).save(*args, **kwargs)


# Accounts
class Account(TenantModel):
    avatar = models.TextField(
        null=True,
        verbose_name='avatar path'
    )
    name = models.CharField(
        verbose_name='account_name',
        null=False,
        max_length=150
    )
    code = models.CharField(
        verbose_name='account_code',
        blank=True,
        null=True,
        max_length=150
    )
    website = models.CharField(
        verbose_name='website',
        blank=True,
        null=True,
        max_length=150
    )
    account_type = models.JSONField(
        null=False,
        default=list
    )
    manager = models.JSONField(
        null=False
    )
    parent_account = models.CharField(
        verbose_name='parent_account',
        null=True,
        max_length=150
    )
    tax_code = models.CharField(
        verbose_name='text_code',
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
        verbose_name='annual_revenue',
        blank=True,
        null=True,
        max_length=150
    )
    total_employees = models.CharField(
        verbose_name='total_employees',
        null=False,
        max_length=150)
    phone = models.CharField(
        verbose_name='phone',
        blank=True,
        null=True,
        max_length=25
    )
    email = models.CharField(
        verbose_name='email',
        blank=True,
        null=True,
        max_length=150
    )
    shipping_address = models.JSONField(
        default=list,
        null=True
    )
    billing_address = models.JSONField(
        default=list,
        null=True
    )

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        super(Account, self).save(*args, **kwargs)


# Contact
class Contact(TenantModel):
    owner = models.UUIDField(
        help_text='employee'
    )
    bio = models.CharField(
        verbose_name='bio',
        blank=True,
        null=True,
        max_length=150
    )
    avatar = models.TextField(
        null=True,
        verbose_name='avatar path'
    )
    fullname = models.CharField(
        verbose_name='fullname',
        null=False,
        max_length=150
    )
    salutation = models.ForeignKey(
        'saledata.Salutation',
        on_delete=models.SET_NULL,
        null=True
    )
    phone = models.CharField(
        verbose_name='phone',
        blank=True,
        null=True,
        max_length=25
    )
    mobile = models.CharField(
        verbose_name='mobile',
        blank=True,
        null=True,
        max_length=25
    )
    account_name = models.ForeignKey(
        'saledata.Account',
        verbose_name='account_name',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contacts'
    )
    email = models.CharField(
        verbose_name='email',
        blank=True,
        null=True,
        max_length=150
    )
    job_title = models.CharField(
        verbose_name='job_title',
        blank=True,
        null=True,
        max_length=150
    )
    report_to = models.UUIDField(
        null=True,
        blank=True,
        help_text='employee'
    )
    address_infor = models.JSONField(
        default=dict,
        null=True
    )
    additional_infor = models.JSONField(
        default=dict,
        null=True
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        super(Contact, self).save(*args, **kwargs)


# class ContactDraft(TenantModel):
#     owner = models.CharField(
#         verbose_name='owner',
#         blank=True,
#         null=True,
#         max_length=150
#     )
#     bio = models.CharField(
#         verbose_name='bio',
#         blank=True,
#         null=True,
#         max_length=150
#     )
#     avatar = models.TextField(
#         null=True,
#         verbose_name='avatar path'
#     )
#     fullname = models.CharField(
#         verbose_name='fullname',
#         null=True,
#         max_length=150
#     )
#     salutation = models.CharField(
#         verbose_name='salutation',
#         blank=True,
#         null=True,
#         max_length=150
#     )
#     phone = models.CharField(
#         verbose_name='phone',
#         blank=True,
#         null=True,
#         max_length=25
#     )
#     mobile = models.CharField(
#         verbose_name='mobile',
#         blank=True,
#         null=True,
#         max_length=25
#     )
#     account_name = models.CharField(
#         verbose_name='account_name',
#         blank=True,
#         max_length=150
#     )
#     email = models.CharField(
#         verbose_name='email',
#         blank=True,
#         null=True,
#         max_length=150
#     )
#     job_title = models.CharField(
#         verbose_name='job_title',
#         blank=True,
#         null=True,
#         max_length=150
#     )
#     report_to = models.CharField(
#         verbose_name='report_to',
#         blank=True,
#         null=True,
#         max_length=150
#     )
#     address_infor = models.JSONField(default=dict)
#     additional_infor = models.JSONField(default=dict)
#
#     class Meta:
#         verbose_name = 'Contact Draft'
#         verbose_name_plural = 'Contact Draft'
#         ordering = ('-date_created',)
#         default_permissions = ()
#         permissions = ()
#
#     def save(self, *args, **kwargs):
#         super(ContactDraft, self).save(*args, **kwargs)

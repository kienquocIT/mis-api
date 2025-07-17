from django.db import models
from apps.shared import MasterDataAbstractModel


__all__ = [
    'Bank',
    'BankAccount'
]


class Bank(MasterDataAbstractModel):
    bank_abbreviation = models.CharField(max_length=150)
    bank_name = models.CharField(max_length=150, blank=True)
    bank_foreign_name = models.CharField(max_length=150, blank=True)
    is_default = models.BooleanField(default=False)
    vietqr_json_data = models.JSONField(default=dict)
    head_office_address = models.TextField(null=True, blank=True)
    head_office_address_data = models.JSONField(default=dict)
    # head_office_address_data = {
    #   country_data: {id, title},
    #   province_data: {id, fullname},
    #   ward_data: {id, fullname},
    #   address: str
    # }

    class Meta:
        verbose_name = 'Bank'
        verbose_name_plural = 'Banks'
        ordering = ('-date_created',)


class BankAccount(MasterDataAbstractModel):
    bank_mapped = models.ForeignKey(
        Bank,
        on_delete=models.CASCADE,
        related_name='bank_accounts'
    )
    bank_mapped_data = models.JSONField(default=dict)
    # bank_mapped_data = {
    #   abbreviation: str
    #   bank_name: str
    #   bank_foreign_name: str
    # }
    bank_account_number = models.CharField(max_length=150)
    bank_account_owner = models.CharField(max_length=150)
    is_default = models.BooleanField(default=False)
    currency = models.ForeignKey(
        'saledata.Currency',
        on_delete=models.SET_NULL,
        null=True,
        related_name='currency_bank_accounts'
    )
    currency_data = models.JSONField(default=dict)
    is_brand = models.BooleanField(default=False)
    brand_name = models.CharField(max_length=150, blank=True, null=True)
    brand_address = models.TextField(null=True, blank=True)
    brand_address_data = models.JSONField(default=dict)
    # brand_address_data = {
    #   country_data: {id, title},
    #   province_data: {id, fullname},
    #   ward_data: {id, fullname},
    #   address: str
    # }

    class Meta:
        verbose_name = 'Bank Account'
        verbose_name_plural = 'Bank Accounts'
        ordering = ('-date_created',)

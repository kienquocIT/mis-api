from django.db import models
from apps.shared import MasterDataAbstractModel

__all__ = [
    'Bank',
    'BankAccount'
]

class Bank(MasterDataAbstractModel):
    abbreviation = models.CharField(max_length=150)
    vietnamese_name = models.CharField(max_length=150)
    english_name = models.CharField(max_length=150)
    is_default = models.BooleanField(default=False)

    country = models.ForeignKey(
        'base.Country',
        on_delete=models.SET_NULL,
        null=True,
        related_name='country_banks'
    )
    city = models.ForeignKey(
        'base.City',
        on_delete=models.SET_NULL,
        null=True,
        related_name='city_banks'
    )
    district = models.ForeignKey(
        'base.District',
        on_delete=models.SET_NULL,
        null=True,
        related_name='district_banks'
    )
    ward = models.ForeignKey(
        'base.Ward',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ward_banks'
    )
    address = models.TextField(null=True)
    full_address = models.TextField(null=True)

    class Meta:
        verbose_name = 'Bank'
        verbose_name_plural = 'Bank'
        ordering = ('abbreviation',)

class BankAccount(MasterDataAbstractModel):
    bank_abbreviation = models.ForeignKey(
        'Bank',
        on_delete=models.CASCADE,
        related_name='bank_accounts'
    )
    bank_name = models.CharField(max_length=150)
    bank_account_number = models.CharField(max_length=150)
    bank_owner = models.CharField(max_length=150)
    is_brand = models.BooleanField(default=False)
    brand_name = models.CharField(max_length=150, null=True)
    is_default = models.BooleanField(default=False)
    currency = models.ForeignKey(
        'saledata.Currency',
        on_delete=models.SET_NULL,
        null=True,
        related_name='currency_bank_accounts'
    )

    brand_country = models.ForeignKey(
        'base.Country',
        on_delete=models.SET_NULL,
        null=True,
        related_name='country_bank_accounts'
    )
    brand_city = models.ForeignKey(
        'base.City',
        on_delete=models.SET_NULL,
        null=True,
        related_name='city_bank_accounts'
    )
    brand_district = models.ForeignKey(
        'base.District',
        on_delete=models.SET_NULL,
        null=True,
        related_name='district_bank_accounts'
    )
    brand_ward = models.ForeignKey(
        'base.Ward',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ward_bank_accounts'
    )
    brand_address = models.TextField(null=True)
    brand_full_address = models.TextField(null=True)

    class Meta:
        verbose_name = 'BankAccount'
        verbose_name_plural = 'BankAccountS'
        ordering = ('bank_account_number',)

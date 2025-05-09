from django.db import models

from apps.shared import MasterDataAbstractModel


class ZaloToken(MasterDataAbstractModel):
    company = models.OneToOneField(
        'company.Company', null=True, on_delete=models.CASCADE,
        related_name='zalo_token_of_company',
    )
    access_token = models.TextField(blank=True, null=True, help_text='Zalo Access Token was encrypted')
    refresh_token = models.TextField(blank=True, null=True, help_text='Zalo Refresh Token was encrypted')
    expires = models.DateTimeField(null=True, help_text='Time expired of token')
    is_syncing = models.BooleanField(default=False)
    is_sync_accounts = models.BooleanField(default=False)
    oa_id = models.CharField(max_length=50)

    @classmethod
    def get_current(cls, company_id):
        try:
            return ZaloToken.objects.get(company_id=company_id)
        except ZaloToken.DoesNotExist:
            return None

    class Meta:
        verbose_name = 'Zalo Token'
        verbose_name_plural = 'Zalo Token'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ZaloPerson(MasterDataAbstractModel):
    token = models.ForeignKey(
        ZaloToken,
        null=True,
        on_delete=models.SET_NULL,
        help_text='Person chat with OA',
    )
    oa_id = models.CharField(max_length=50)
    account_id = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Zalo Person'
        verbose_name_plural = 'Zalo Person'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ZaloMessage(MasterDataAbstractModel):
    person = models.ForeignKey(
        ZaloPerson,
        on_delete=models.CASCADE,
        help_text='Person chat with OA',
    )
    sender = models.CharField(max_length=50, blank=True, help_text='Sender ID')
    recipient = models.CharField(max_length=50, blank=True, help_text='Recipient ID')
    mid = models.TextField(help_text='Message ID')
    text = models.TextField(blank=True, help_text='Message')
    attachments = models.JSONField(default=list, help_text='Attachments')
    is_echo = models.BooleanField(default=False, help_text='True is send from page')
    timestamp = models.BigIntegerField(help_text='Epoch unix time')

    class Meta:
        verbose_name = 'Zalo Message'
        verbose_name_plural = 'Zalo Message'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

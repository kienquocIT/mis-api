from django.db import models

from apps.shared import MasterDataAbstractModel


class MessengerToken(MasterDataAbstractModel):
    company = models.OneToOneField(
        'company.Company', null=True, on_delete=models.CASCADE,
        related_name='messenger_token_of_company',
    )
    token = models.TextField(blank=True, null=True, help_text='Facebook Token was encrypted')
    expires = models.DateTimeField(null=True, help_text='Time expired of token')
    is_syncing = models.BooleanField(default=False)
    is_sync_accounts = models.BooleanField(default=False)

    @classmethod
    def get_current(cls, company_id):
        try:
            return MessengerToken.objects.get(company_id=company_id)
        except MessengerToken.DoesNotExist:
            return None

    class Meta:
        verbose_name = 'Messenger Token'
        verbose_name_plural = 'Messenger Token'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class MessengerPageToken(MasterDataAbstractModel):
    parent = models.ForeignKey(MessengerToken, on_delete=models.CASCADE, help_text='Account Token from parent token')
    token = models.TextField(blank=True, null=True, help_text='Facebook Token was encrypted')
    category = models.TextField(blank=True, help_text='Category response')
    name = models.TextField(blank=True, help_text='Name response')
    account_id = models.CharField(max_length=50)
    tasks = models.JSONField(default=list, help_text='Task response')
    picture = models.JSONField(default=dict, null=True, help_text='Pictures of page')
    link = models.TextField(null=True, help_text='Link to page')

    class Meta:
        verbose_name = 'Messenger Account Token'
        verbose_name_plural = 'Messenger Account Token'
        ordering = ('-name',)
        default_permissions = ()
        permissions = ()


class MessengerPerson(MasterDataAbstractModel):
    page = models.ForeignKey(MessengerPageToken, on_delete=models.CASCADE)
    account_id = models.CharField(max_length=50)
    name = models.TextField(blank=True, help_text='Name of sender')
    avatar = models.TextField(blank=True, help_text='Avatar of sender')
    last_updated = models.DateTimeField(auto_now=True)
    link = models.TextField(blank=True, help_text='Link to Profile')
    contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.SET_NULL,
        null=True,
    )
    lead = models.ForeignKey(
        'lead.Lead',
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = 'Messenger Account Server'
        verbose_name_plural = 'Messenger Account Server'
        ordering = ('-last_updated',)
        default_permissions = ()
        permissions = ()


class MessengerMessage(MasterDataAbstractModel):
    page = models.ForeignKey(MessengerPageToken, on_delete=models.CASCADE)
    person = models.ForeignKey(MessengerPerson, on_delete=models.CASCADE)
    sender = models.CharField(max_length=50, blank=True, help_text='Sender ID')
    recipient = models.CharField(max_length=50, blank=True, help_text='Recipient ID')
    mid = models.TextField(help_text='Message ID')
    text = models.TextField(blank=True, help_text='Message')
    attachments = models.JSONField(default=list, help_text='Attachments')
    is_echo = models.BooleanField(default=False, help_text='True is send from page')
    timestamp = models.BigIntegerField(help_text='Epoch unix time')

    class Meta:
        verbose_name = 'Messenger Sender Message'
        verbose_name_plural = 'Messenger Sender Message'
        ordering = ('-timestamp',)
        default_permissions = ()
        permissions = ()

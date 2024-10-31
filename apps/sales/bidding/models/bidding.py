from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SimpleAbstractModel

BIDDING_STATUS = [
    (0, _('Waiting')),
    (1, _('Won')),
    (2, _('Lost')),
]

class Bidding(DataAbstractModel):
    status = models.SmallIntegerField(choices=BIDDING_STATUS, default=0)
    bid_value = models.FloatField(default=0)
    bid_date = models.DateField(null=True, blank=True)
    opportunity = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE,
        verbose_name="opportunity",
        related_name="bidding_opportunity",
        null=True
    )
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="bidding_customer",
        null=True,
        help_text="sale data Accounts have type customer"
    )
    venture_partner = models.ManyToManyField(
        'saledata.Account',
        through='BiddingPartnerAccount',
        symmetrical=False,
        blank=True,
        related_name='bidding_venture_partner',
    )
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='BiddingAttachment',
        symmetrical=False,
        blank=True,
        related_name='file_of_bidding',
    )
    tinymce_content = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Bidding'
        verbose_name_plural = 'Biddings'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("BD")[1])
                    if num_max is None or (isinstance(num_max, int) and tmp > num_max):
                        num_max = tmp
            except Exception as err:
                print(err)
        return num_max

    @classmethod
    def generate_code(cls, company_id):
        existing_codes = cls.objects.filter(company_id=company_id).values_list('code', flat=True)
        num_max = cls.find_max_number(existing_codes)
        if num_max is None:
            code = 'BD0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'BD{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    @classmethod
    def push_code(cls, instance, kwargs):
        if not instance.code:
            instance.code = cls.generate_code(company_id=instance.company_id)
            kwargs['update_fields'].append('code')
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3] and 'update_fields' in kwargs:  # added, finish
            # check if date_approved then call related functions
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    # code
                    self.push_code(instance=self, kwargs=kwargs)
        # hit DB
        super().save(*args, **kwargs)


class BiddingDocument(MasterDataAbstractModel):
    bidding = models.ForeignKey(
        'bidding.Bidding',
        on_delete=models.CASCADE,
        verbose_name="bidding",
        related_name="bidding_document_bidding",
    )
    document_type = models.ForeignKey(
        'saledata.DocumentType',
        on_delete=models.CASCADE,
        verbose_name="document type",
        related_name="bidding_document_document_type",
        null=True,
        blank=True
    )
    remark = models.TextField(verbose_name="remark", blank=True, null=True)
    attachment_data = models.JSONField(default=list, help_text='data json of attachment')
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Bidding document'
        verbose_name_plural = 'Bidding documents'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class BiddingAttachment(M2MFilesAbstractModel):
    bidding = models.ForeignKey(
        'bidding.Bidding',
        on_delete=models.CASCADE,
        verbose_name="bidding",
        related_name="bidding_attachment_bidding",
    )
    document = models.ForeignKey(
        'bidding.BiddingDocument',
        on_delete=models.CASCADE,
        verbose_name="document",
        related_name="bidding_attachment_bidding_document",
        null=True
    )
    @classmethod
    def get_doc_field_name(cls):
        return 'bidding'

    class Meta:
        verbose_name = 'Bidding attachment'
        verbose_name_plural = 'Bidding attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class BiddingPartnerAccount(SimpleAbstractModel):
    is_leader = models.BooleanField(default=False)
    bidding = models.ForeignKey(
        'bidding.Bidding',
        on_delete=models.CASCADE,
        verbose_name="bidding partner account bidding",
        related_name="bidding_partner_account_bidding",
    )
    partner_account = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="bidding partner account",
        related_name="bidding_partner_account_partner_account",
    )

    class Meta:
        verbose_name = 'Bidding partner account'
        verbose_name_plural = 'Bidding partner accounts'
        default_permissions = ()
        permissions = ()
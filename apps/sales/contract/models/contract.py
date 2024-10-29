from django.db import models

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import DataAbstractModel, MasterDataAbstractModel


class ContractApproval(DataAbstractModel):
    document_data = models.JSONField(default=list, help_text='data json of document')
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='ContractAttachment',
        symmetrical=False,
        blank=True,
        related_name='file_of_contract_approval',
    )
    abstract_content = models.TextField(blank=True, null=True)
    trade_content = models.TextField(blank=True, null=True)
    legal_content = models.TextField(blank=True, null=True)
    payment_content = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Contract Approval'
        verbose_name_plural = 'Contracts Approval'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("CA")[1])
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
            code = 'CA0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'CA{num_str}'
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


class ContractDocument(MasterDataAbstractModel):
    contract_approval = models.ForeignKey(
        'contract.ContractApproval',
        on_delete=models.CASCADE,
        verbose_name="contract",
        related_name="contract_doc_contract_approval",
    )
    remark = models.TextField(verbose_name="remark", blank=True, null=True)
    attachment_data = models.JSONField(default=list, help_text='data json of attachment')
    order = models.IntegerField(default=1)
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='ContractDocumentAttachment',
        symmetrical=False,
        blank=True,
        related_name='file_of_contract_document',
    )

    class Meta:
        verbose_name = 'Contract document'
        verbose_name_plural = 'Contract documents'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ContractAttachment(M2MFilesAbstractModel):
    contract_approval = models.ForeignKey(
        'contract.ContractApproval',
        on_delete=models.CASCADE,
        verbose_name="contract",
        related_name="contract_attachment_contract_approval",
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'contract_approval'

    class Meta:
        verbose_name = 'Contract attachment'
        verbose_name_plural = 'Contract attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ContractDocumentAttachment(M2MFilesAbstractModel):
    contract_document = models.ForeignKey(
        'contract.ContractDocument',
        on_delete=models.CASCADE,
        verbose_name='contract document',
        related_name="contract_doc_attachment_doc"
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'contract_document'

    class Meta:
        verbose_name = 'Contract document attachment'
        verbose_name_plural = 'Contract document attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

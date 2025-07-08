from django.db import models

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.shared import DataAbstractModel, MasterDataAbstractModel, BastionFieldAbstractModel


class ContractApproval(DataAbstractModel, BastionFieldAbstractModel):
    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return "58385bcf-f06c-474e-a372-cadc8ea30ecc"

    opportunity_data = models.JSONField(default=dict, help_text='data json of opportunity')
    employee_inherit_data = models.JSONField(default=dict, help_text='data json of employee_inherit')
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

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config('contract', True, self, kwargs)
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

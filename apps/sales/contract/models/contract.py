from django.db import models

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import DataAbstractModel, MasterDataAbstractModel


class Contract(DataAbstractModel):
    document_data = models.JSONField(default=list, help_text='data json of document')

    class Meta:
        verbose_name = 'Contract'
        verbose_name_plural = 'Contracts'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ContractDocument(MasterDataAbstractModel):
    contract = models.ForeignKey(
        'contract.Contract',
        on_delete=models.CASCADE,
        verbose_name="contract",
        related_name="contract_doc_contract",
    )
    remark = models.TextField(verbose_name="remark", blank=True, null=True)
    attachment_data = models.JSONField(default=list, help_text='data json of attachment')
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Contract'
        verbose_name_plural = 'Contracts'
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

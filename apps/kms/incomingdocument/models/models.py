import json

from django.db import models
from apps.core.company.models import CompanyFunctionNumber
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SECURITY_LEVEL

KIND = (
    (1, 'employee'),
    (2, 'group')
)

KIND_PERM = (
    (1, 'preview'),
    (2, 'viewer'),
    (3, 'editor'),
    (4, 'custom')
)


class KMSIncomingDocument(DataAbstractModel):
    remark = models.TextField(blank=True)
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='IncomingAttachDocumentMapAttachFile',
        symmetrical=False,
        blank=True,
        related_name='kms_incoming_document_attachment_m2m'
    )
    sender = models.CharField(max_length=250, blank=True)
    document_type = models.ForeignKey(
        'documentapproval.KMSDocumentType',
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name='kms_incoming_document_document_types'
    )
    content_group = models.ForeignKey(
        'documentapproval.KMSContentGroup',
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name='kms_incoming_document_content_groups'
    )
    effective_date = models.DateTimeField(null=True)
    expired_date = models.DateTimeField(null=True)
    security_level = models.SmallIntegerField(
        default=0,
        choices=SECURITY_LEVEL
    )

    class Meta:
        verbose_name = 'Incoming document of KMS'
        verbose_name_plural = 'Incoming documents of KMS'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class IncomingAttachDocumentMapAttachFile(M2MFilesAbstractModel):
    incoming_document = models.ForeignKey(
        KMSIncomingDocument,
        on_delete=models.CASCADE,
        verbose_name='Attachment File of KMS attached Incoming Document',
        null=True
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'incoming document'

    class Meta:
        verbose_name = 'KMS incoming document attachment'
        verbose_name_plural = 'KMS incoming document attachment'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()




import json

from django.db import models
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SECURITY_LEVEL, SimpleAbstractModel
from apps.core.company.models import CompanyFunctionNumber


class KMSIncomingDocument(DataAbstractModel):
    remark = models.TextField(blank=True)
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='IncomingAttachDocumentMapAttachFile',
        symmetrical=False,
        blank=True,
        related_name='kms_incoming_document_attachment_m2m'
    )

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config(
                        app_code=None, instance=self, in_workflow=True, kwargs=kwargs
                    )
        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Incoming document of KMS'
        verbose_name_plural = 'Incoming documents of KMS'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class KMSAttachIncomingDocuments(MasterDataAbstractModel):
    incoming_document = models.ForeignKey(
        KMSIncomingDocument,
        on_delete=models.CASCADE,
        related_name='kms_attach_incoming_documents'
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
    folder = models.ForeignKey(
        'attachments.Folder',
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name='kms_incoming_document_folders'
    )
    attachment = models.JSONField(
        default=list,
        null=True,
        verbose_name='Attachment File',
        help_text=json.dumps(["uuid4", "uuid4"])
    )

    class Meta:
        verbose_name = 'Attached Incoming Documents of KMS'
        verbose_name_plural = 'list Attached Incoming Documents of KMS'
        default_permissions = ()
        permissions = ()


class IncomingAttachDocumentMapAttachFile(M2MFilesAbstractModel):
    incoming_document = models.ForeignKey(
        KMSIncomingDocument,
        on_delete=models.CASCADE,
        verbose_name='Attachment File of KMS attached Incoming Document',
        related_name="incoming_document_attachment_incoming_document",
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'incoming_document'

    class Meta:
        verbose_name = 'KMS incoming document attachment'
        verbose_name_plural = 'KMS incoming document attachment'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class KMSInternalRecipientIncomingDocument(SimpleAbstractModel):
    incoming_document = models.ForeignKey(
        KMSIncomingDocument,
        on_delete=models.CASCADE,
        verbose_name='Internal Recipient of KMS Incoming Document',
        related_name='kms_kmsinternalrecipient_incoming_doc'
    )
    employee = models.ForeignKey(
        'hr.Employee',
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Employee',
        related_name='kms_kmsinternalrecipient_employee'
    )
    employee_access = models.JSONField(
        default=dict,
        verbose_name="employee list has access this file",
        help_text='store json data of employee'
    )

    class Meta:
        verbose_name = 'Internal recipient incoming document'
        verbose_name_plural = 'Internal recipients incoming document'
        ordering = ()
        default_permissions = ()
        permissions = ()

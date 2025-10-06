from django.db import models

from apps.shared import MasterDataAbstractModel, SimpleAbstractModel


class KMSDocumentType(MasterDataAbstractModel):
    folder = models.ForeignKey(
        'attachments.Folder',
        on_delete=models.SET_NULL,
        null=True,
        related_name='kms_doc_type_map_folder'
    )
    applications_data = models.JSONField(default=list)
    applications = models.ManyToManyField(
        'base.Application',
        through="KMSDocumentTypeApplication",
        symmetrical=False,
        blank=True,
        related_name='document_type_m2m_application'
    )

    class Meta:
        verbose_name = 'Master data Document type of KMS'
        verbose_name_plural = 'Document type of KMS'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class KMSDocumentTypeApplication(SimpleAbstractModel):
    document_type = models.ForeignKey(
        KMSDocumentType,
        on_delete=models.CASCADE,
        verbose_name="document type",
        related_name="document_type_application_document_type",
    )
    application = models.ForeignKey(
        'base.Application',
        on_delete=models.CASCADE,
        verbose_name="application",
        related_name="document_type_application_application",
    )

    class Meta:
        verbose_name = 'Document Type Application'
        verbose_name_plural = 'Document Type Applications'
        ordering = ()
        default_permissions = ()
        permissions = ()


class KMSContentGroup(MasterDataAbstractModel):

    class Meta:
        verbose_name = 'Master data Content group of KMS'
        verbose_name_plural = 'Content group of KMS'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

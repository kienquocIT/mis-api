from django.db import models

from apps.shared import MasterDataAbstractModel


class KMSDocumentType(MasterDataAbstractModel):
    folder = models.ForeignKey(
        'attachments.Folder',
        on_delete=models.SET_NULL,
        null=True,
        related_name='kms_doc_type_map_folder'
    )

    class Meta:
        verbose_name = 'Master data Document type of KMS'
        verbose_name_plural = 'Document type of KMS'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class KMSContentGroup(MasterDataAbstractModel):

    class Meta:
        verbose_name = 'Master data Content group of KMS'
        verbose_name_plural = 'Content group of KMS'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

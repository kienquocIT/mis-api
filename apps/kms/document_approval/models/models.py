import json

from django.db import models

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import DataAbstractModel, MasterDataAbstractModel


SECURITY_LV = (
    (0, 'low'),
    (1, 'medium'),
    (2, 'high')
)

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


class KMSDocumentApproval(DataAbstractModel):
    remark = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Document approval of KMS'
        verbose_name_plural = 'Document approval of KMS'
        default_permissions = ()
        permissions = ()


class KSMAttachedDocuments(MasterDataAbstractModel):
    document_approval = models.ForeignKey(
        KMSDocumentApproval,
        on_delete=models.CASCADE,
        related_name='kms_kmsattached_document_approval'
    )
    document_type = models.ForeignKey(
        'document_approval.KMSDocumentType',
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name='kms_kmsattached_document_types'
    )
    content_group = models.ForeignKey(
        'document_approval.KMSContentGroup',
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name='kms_kmsattached_content_groups'
    )
    security_lv = models.SmallIntegerField(
        default=0,
        help_text='choices= ' + str(SECURITY_LV),
    )
    published_place = models.ForeignKey(
        'hr.Group',
        on_delete=models.CASCADE,
        verbose_name="published place",
        related_name="kms_kmsattached_published_place",
        null=True
    )
    effective_date = models.DateTimeField(
        verbose_name='effect date', null=True
    )
    expired_date = models.DateTimeField(
        verbose_name='expired date', null=True
    )
    folder = models.ForeignKey(
        'attachments.Folder',
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name='kms_kmsattached_folders'
    )
    attachment = models.JSONField(
        default=list,
        null=True,
        verbose_name='Attachment file',
        help_text=json.dumps(
            ["uuid4", "uuid4"]
        )
    )
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='AttachDocumentMapAttachmentFile',
        symmetrical=False,
        blank=True,
        related_name='kms_kmsattached_attach_m2m',
    )

    class Meta:
        verbose_name = 'Attached documents of KMS'
        verbose_name_plural = 'list Attached documents of KMS'
        default_permissions = ()
        permissions = ()


class AttachDocumentMapAttachmentFile(M2MFilesAbstractModel):
    kms_attached_doc = models.ForeignKey(
        KSMAttachedDocuments,
        on_delete=models.CASCADE,
        verbose_name='Attachment file of KMS attached document'
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'document_approval'

    class Meta:
        verbose_name = 'KMS document approval attachment'
        verbose_name_plural = 'KMS document approval attachment'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class KMSInternalRecipient(MasterDataAbstractModel):
    document_approval = models.ForeignKey(
        KMSDocumentApproval,
        on_delete=models.CASCADE,
        related_name='kms_kmsinternal_recipient_document_approval'
    )
    kind = models.SmallIntegerField(
        default=2,
        help_text='choices= ' + str(KIND),
    )
    employee_access = models.JSONField(
        default=list,
        null=True,
        verbose_name='employee list has access this file',
        help_text=json.dumps(
            ["uuid4", "uuid4"]
        )
    )
    group_access = models.JSONField(
        default=list,
        null=True,
        verbose_name='permission of group',
        help_text=json.dumps(
            ["uuid4", "uuid4"]
        )
    )
    document_permission_list = models.JSONField(
        default=dict,
        null=True,
        verbose_name='permission of employee',
        help_text=json.dumps(
            {
                "permission_kind": [1, 2, 3, 4, 5, 6, 7]
            }
        )
    )

    expiration_date = models.DateField(
        verbose_name='expiration date', null=True
    )

    class Meta:
        verbose_name = 'Internal recipient'
        verbose_name_plural = 'Internal recipient'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

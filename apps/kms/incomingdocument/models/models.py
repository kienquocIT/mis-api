import json

from django.db import models
from apps.core.company.models import CompanyFunctionNumber
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SECURITY_LEVEL, DOCUMENT_TYPE

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
    sender = models.CharField(max_length=250, blank=True)
    # document_type = models.SmallIntegerField(
    #     default=9,
    #     choices=str(DOCUMENT_TYPE)
    # )
    effective_date = models.DateTimeField(null=True)
    expired_date = models.DateTimeField(null=True)
    security_level = models.SmallIntegerField(
        default=0,
        choices=SECURITY_LEVEL
    )
    # content_group = models.ForeignKey(
    #     'documentapproval.KMSContentGroup',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     related_name='kms_incoming_document_content_group'
    # )

    class Meta:
        verbose_name = 'Incoming document of KMS'
        verbose_name_plural = 'Incoming documents of KMS'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()





from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SimpleAbstractModel

class DocumentType(MasterDataAbstractModel):

    class Meta:
        verbose_name = 'Document type'
        verbose_name_plural = 'Document types'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


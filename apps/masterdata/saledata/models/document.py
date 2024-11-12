from django.db import models
from apps.shared import MasterDataAbstractModel

class DocumentType(MasterDataAbstractModel):
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Document type'
        verbose_name_plural = 'Document types'
        ordering = ('-is_default', 'code')
        default_permissions = ()
        permissions = ()

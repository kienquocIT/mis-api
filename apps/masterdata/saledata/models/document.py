from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import MasterDataAbstractModel


DOC_CATEGORY_CHOICES = [
    ('bidding', _('Bidding')),
    ('consulting', _('Consulting')),
]

class DocumentType(MasterDataAbstractModel):
    is_default = models.BooleanField(default=False)
    doc_type_category = models.CharField(
        max_length=20,
        choices=DOC_CATEGORY_CHOICES,
        verbose_name='Document category',
        null=True,
    )

    class Meta:
        verbose_name = 'Document type'
        verbose_name_plural = 'Document types'
        ordering = ('-is_default', 'code')
        default_permissions = ()
        permissions = ()

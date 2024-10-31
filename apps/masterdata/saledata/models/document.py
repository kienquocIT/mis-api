from apps.shared import MasterDataAbstractModel

class DocumentType(MasterDataAbstractModel):

    class Meta:
        verbose_name = 'Document type'
        verbose_name_plural = 'Document types'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

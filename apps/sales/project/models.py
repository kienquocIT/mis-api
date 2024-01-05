from apps.shared import MasterDataAbstractModel


class Project(MasterDataAbstractModel):
    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Project'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

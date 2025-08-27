from django.db import models

from apps.shared import MasterDataAbstractModel


class ContainerTypeInfo(MasterDataAbstractModel):
    class Meta:
        verbose_name = 'Container Type information'
        verbose_name_plural = 'Container Type information'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        if not self.code:
            count = ContainerTypeInfo.objects.filter_on_company().count() + 1
            self.code = f'CON00{count}'
        super().save(*args, **kwargs)

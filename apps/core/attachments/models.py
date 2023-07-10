from django.db import models

from apps.shared import MasterDataAbstractModel


class Files(MasterDataAbstractModel):
    relate_app = models.ForeignKey(
        'base.Application',
        null=True,
        on_delete=models.SET_NULL,
    )
    relate_app_code = models.CharField(max_length=100)
    relate_doc_id = models.UUIDField()

    media_file_id = models.UUIDField(unique=True)
    file_name = models.TextField()
    file_size = models.IntegerField()
    file_type = models.CharField(max_length=50)

    def before_save(self, force_insert=False):
        if force_insert is True and self.relate_app and not self.relate_app_code:
            self.relate_app_code = self.relate_app.code

    def save(self, *args, **kwargs):
        self.before_save(force_insert=kwargs.get('force_insert', False))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Files'
        verbose_name_plural = 'Files'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

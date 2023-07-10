from typing import Union

from crum import get_current_user
from django.db import models

from apps.shared import MasterDataAbstractModel, MediaForceAPI, TypeCheck


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

    def get_detail(self):
        return {
            'id': str(self.id),
            'relate_app_id': str(self.relate_app_id),
            'relate_app_code': str(self.relate_app_code),
            'relate_doc_id': str(self.relate_doc_id),
            'media_file_id': str(self.media_file_id),
            'file_name': str(self.file_name),
            'file_size': self.file_size,
            'file_type': str(self.file_type),
        }

    def before_save(self, force_insert=False):
        if force_insert is True and self.relate_app and not self.relate_app_code:
            self.relate_app_code = self.relate_app.code

    @classmethod
    def check_media_file(cls, media_file_id, media_user_id=None) -> (bool, any):
        if not media_user_id:
            user_obj = get_current_user()
            if user_obj and isinstance(user_obj, models.Model):
                employee_obj = getattr(user_obj, 'employee_current', None)
                if employee_obj:
                    media_user_id = getattr(employee_obj, 'media_user_id', None)

        if media_user_id and TypeCheck.check_uuid(media_user_id):
            return MediaForceAPI.get_file_check(media_file_id=media_file_id, media_user_id=media_user_id)
        return False, 'MEDIA_USER_ID_IS_REQUIRED_IN_CHECK_METHOD'

    @classmethod
    def regis_media_file(
            cls, relate_app, relate_doc_id, relate_app_code=None,
            user_obj=None,
            **kwargs
    ) -> Union[ValueError, models.Model]:
        # get file properties from media_result
        media_result = kwargs.pop('media_result', {})
        if media_result:
            kwargs.update(
                {
                    'media_file_id': media_result['id'],
                    'file_name': media_result['file_name'],
                    'file_size': media_result['file_size'],
                    'file_type': media_result['file_type'],
                }
            )
        # get relate_app_code from relate_app if dont have value
        if relate_app and not relate_app_code:
            relate_app_code = relate_app.code
        # get employee_id from current_user if dont have value
        if not user_obj:
            user_obj = get_current_user()
        if user_obj and isinstance(user_obj, models.Model) and hasattr(user_obj, 'tenant_current'):
            tenant_id = getattr(user_obj, 'tenant_current_id', None)
            company_id = getattr(user_obj, 'company_current_id', None)
            employee_created_id = getattr(user_obj, 'employee_current_id', None)

            # check then call create
            if all(
                    [
                        relate_app,
                        relate_doc_id,
                        relate_app_code,
                        employee_created_id,
                        tenant_id,
                        company_id,
                    ]
            ):
                return cls.objects.create(
                    relate_app=relate_app, relate_app_code=relate_app_code, relate_doc_id=relate_doc_id,
                    employee_created_id=employee_created_id,
                    **kwargs
                )
        raise ValueError('SOME_REQUIRED_DATA_DONT_HAVE_VALUE')

    def save(self, *args, **kwargs):
        self.before_save(force_insert=kwargs.get('force_insert', False))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Files'
        verbose_name_plural = 'Files'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

from typing import Union
from uuid import UUID

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.text import slugify

from apps.shared import MasterDataAbstractModel, TypeCheck, StringHandler, HrMsg, AttMsg
from apps.core.attachments.storages.aws.storages_backend import PrivateMediaStorage


FILE_BELONG_TO = (
    (0, 'Self'),
    (1, 'Company'),
)


def generate_path_file(instance, filename):
    def make_sure_filename_length(_filename):
        if len(_filename) > 30:
            arr_tmp = _filename.split(".")
            f_name, f_ext = slugify("".join(arr_tmp[:-1])), arr_tmp[-1]
            f_name = f'{f_name[:20]}_{StringHandler.random_str(9 - len(f_ext) - 1)}'
            return f'{f_name.lower()}.{f_ext.lower()}'
        return _filename

    if instance.company_id:
        if instance.employee_created_id:
            company_path = str(instance.company_id).replace('-', '')
            employee_path = str(instance.employee_created_id).replace('-', '')
            return f"{company_path}/{employee_path}/{make_sure_filename_length(filename)}"
        raise ValueError('Attachment require employee related')
    raise ValueError('Attachment require company related')


class Files(MasterDataAbstractModel):
    """
    Attachment was uploaded by Employee

    Stage 1: Upload file
        Field require: tenant, company, employee_created, file, file_name, file_size, file_type
    Stage 2: Related attachment to Document Objects
        Field require: relate_app, relate_app_code, relate_doc_id
    """
    relate_app = models.ForeignKey(
        'base.Application',
        null=True,
        on_delete=models.SET_NULL,
    )
    relate_app_code = models.CharField(max_length=100, null=True)
    relate_doc_id = models.UUIDField(null=True)

    file_name = models.TextField()
    file_size = models.IntegerField()
    file_type = models.CharField(max_length=50)

    file = models.FileField(storage=PrivateMediaStorage, upload_to=generate_path_file)

    belong_to = models.SmallIntegerField(
        choices=FILE_BELONG_TO,
        default=0,
    )

    remarks = models.TextField(blank=True)

    def get_url(self):
        if self.file:
            return self.file.url
        return None

    def get_detail(self):
        return {
            'id': str(self.id),
            'relate_app_id': str(self.relate_app_id),
            'relate_app_code': str(self.relate_app_code),
            'relate_doc_id': str(self.relate_doc_id),
            'file_name': str(self.file_name),
            'file_size': self.file_size,
            'file_type': str(self.file_type),
            'remarks': self.remarks,
        }

    def before_save(self, force_insert=False):
        if force_insert is True and self.relate_app and not self.relate_app_code:
            self.relate_app_code = self.relate_app.code

    @classmethod
    def get_used_size(cls, **kwargs) -> int | None:
        file_size__sum = Files.objects.filter_current(**kwargs).aggregate(
            file_size__sum=models.Sum('file_size', default=0)
        )['file_size__sum']
        if isinstance(file_size__sum, int):
            return file_size__sum
        return None

    @classmethod
    def check_available_size_employee(cls, employee_id, new_size=None) -> (bool, str, str):
        if employee_id and TypeCheck.check_uuid(employee_id):
            file_size__sum = cls.get_used_size(
                fill__tenant=True, fill__company=True, employee_created_id=employee_id, belong_to=0,
            )
            if isinstance(file_size__sum, int):
                file_size__check = file_size__sum + (new_size if isinstance(new_size, int) else 0)
                if file_size__check < settings.FILE_SIZE_OF_EMPLOYEE_TOTAL:
                    return True, '', ''
                return False, 'SIZE_SUM_EXCEED_LIMIT', AttMsg.FILE_SUM_EXCEED_LIMIT
            return False, 'SIZE_SUM_RETURN', AttMsg.FILE_SUM_NOT_RETURN
        return False, 'EMPLOYEE_REQUIRED', HrMsg.EMPLOYEE_REQUIRED

    @classmethod
    def check_media_file(
            cls, file_ids: list[UUID | str], employee_id: UUID | str, doc_id: UUID | str = None
    ) -> (bool, any):
        """
        Verify File ID available or match rule before related it with document.
        Args:
            file_ids (list[UUID or str]): File IDs need check rules.
            employee_id (UUID or str): Employee need check file owner
            doc_id (UUID or str): Doc ID for case update - default it is null.
        Returns:
            (bool, any) : (State, Object File or Remarks Errors)
        """
        if (
                file_ids and isinstance(file_ids, list) and TypeCheck.check_uuid_list(file_ids)
                and employee_id and TypeCheck.check_uuid(employee_id)
        ):
            kwargs = {
                'id__in': file_ids,
                'employee_created_id': employee_id,
            }
            kwargs_q = Q(relate_doc_id__isnull=True)
            if doc_id and TypeCheck.check_uuid(doc_id):
                kwargs_q |= Q(relate_doc_id=doc_id)
            att_obj = cls.objects.filter(**kwargs).filter(kwargs_q)
            if att_obj:
                # "Case: success"
                return True, att_obj
        # "Case: raise Errors"
        return False, 'MEDIA_USER_ID_IS_REQUIRED_IN_CHECK_METHOD'

    @classmethod
    def regis_media_file(
            cls, relate_app, relate_doc_id, file_objs: models.QuerySet, unused_resolve='unlink', **kwargs
    ) -> Union[ValueError, list[models.Model]]:
        if file_objs and isinstance(file_objs, models.QuerySet) and file_objs.model is Files and relate_app:
            relate_app_code = relate_app.code
            result = []
            doc_ids_registered = []

            # file_objs register with args:relate_doc_id
            for obj in file_objs:
                obj.relate_app = relate_app
                obj.relate_app_code = relate_app_code
                obj.relate_doc_id = relate_doc_id
                obj.save(update_fields=[
                    'relate_app', 'relate_app_code', 'relate_doc_id',
                ])
                doc_ids_registered.append(obj.id)
                result.append(obj)

            # reset Files registered with  args:relate_doc_id
            unused_linked = cls.objects.filter(relate_doc_id=relate_doc_id).exclude(id__in=doc_ids_registered)
            if unused_linked:
                if unused_resolve == 'unlink':
                    # "Case: Unlink file to relate_doc_id (and field reference)"
                    for obj_unused in unused_linked:
                        obj_unused.relate_app = None
                        obj_unused.relate_app_code = None
                        obj_unused.relate_doc_id = None
                        obj_unused.save(update_fields=[
                            'relate_app', 'relate_app_code', 'relate_doc_id',
                        ])
                elif unused_resolve == 'delete':
                    # "Case: Unused was destroyed permanent"
                    unused_linked.delete()

            return result
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

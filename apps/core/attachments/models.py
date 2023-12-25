__all__ = [
    'Files', 'M2MFilesAbstractModel',
]

import logging

from typing import Union
from uuid import UUID

from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from apps.shared import MasterDataAbstractModel, TypeCheck, StringHandler, HrMsg, AttMsg, SimpleAbstractModel
from apps.core.attachments.storages.aws.storages_backend import PrivateMediaStorage


logger = logging.getLogger(__name__)

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

    def get_url(self, expire=None):
        if self.file:
            return self.file.storage.url(self.file.name, expire=expire if expire else settings.FILE_STORAGE_EXPIRED)
        return None

    def get_detail(self, has_link: bool = False):
        return {
            'id': str(self.id),
            'relate_app_id': str(self.relate_app_id),
            'relate_app_code': str(self.relate_app_code),
            'relate_doc_id': str(self.relate_doc_id),
            'file_name': str(self.file_name),
            'file_size': self.file_size,
            'file_type': str(self.file_type),
            'remarks': self.remarks,
            **(
                {'link': self.get_url()} if has_link else {}
            )
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

    def check_available_file(self, employee_id: UUID | str, doc_id: UUID | str = None):
        if str(self.employee_created_id) != str(employee_id):
            return False
        if doc_id is None and self.relate_doc_id is not None:
            return False
        if doc_id and self.relate_doc_id and str(doc_id) != str(self.relate_doc_id):
            return False
        return True

    @classmethod
    def regis_media_file(
            cls,
            relate_app: models.Model,
            relate_doc_id: UUID | str,
            file_objs_or_ids: models.QuerySet | list[UUID or str],
            unused_resolve='unlink',
            **kwargs
    ) -> Union[ValueError, list[models.Model]]:
        if file_objs_or_ids and relate_app:
            file_objs = None
            if isinstance(file_objs_or_ids, models.QuerySet) and file_objs_or_ids.model is Files:
                file_objs = file_objs_or_ids
            elif isinstance(file_objs_or_ids, list) and TypeCheck.check_uuid_list(file_objs_or_ids):
                file_objs = Files.objects.filter(id__in=file_objs_or_ids)
                if file_objs.count() != len(file_objs_or_ids):
                    file_objs = None

            if file_objs:
                relate_app_code = getattr(relate_app, 'code', '')
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

    def link(self, doc_id, doc_app):
        self.relate_doc_id = doc_id
        self.relate_app = doc_app
        self.relate_app_code = getattr(doc_app, 'code', None)
        self.save(force_update=True, update_fields=['relate_doc_id', 'relate_app', 'relate_app_code'])
        return True

    def unlink(self):
        self.relate_doc_id = None
        self.relate_app = None
        self.relate_app_code = None
        self.save(force_update=True, update_fields=['relate_doc_id', 'relate_app', 'relate_app_code'])
        return True

    class Meta:
        verbose_name = 'Files'
        verbose_name_plural = 'Files'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


# for M2M of Files
class M2MFilesAbstractModel(SimpleAbstractModel):
    """
    Class abstract of Model ManyToMany to attachment.Files
    Using general name of attachment, order, date_created and utility function.
    """
    attachment = models.OneToOneField(
        'attachments.Files',
        on_delete=models.CASCADE,
        verbose_name='Attachment files',
        help_text='Many attachment file',
        related_name='%(app_label)s_%(class)s_files',
    )
    order = models.SmallIntegerField(
        default=1
    )
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )

    @classmethod
    def has_change(cls, current_ids: list[str], old_ids: list[str] = None, **kwargs) -> None or bool:
        """
        Get File IDs current of M2M
        """
        if old_ids is None and kwargs:
            old_ids = cls.get_old(**kwargs)
        return not (
                len(list(set(current_ids) - set(old_ids))) == 0  # current diff old
                and len(list(set(old_ids) - set(current_ids))) == 0  # old diff current
        )

    @classmethod
    def get_old(cls, **kwargs) -> list[str]:
        """
        Get File IDs current of M2M
        """
        if kwargs:
            return [
                str(file_id) for file_id in
                cls.objects.filter_current(**kwargs).values_list('attachment_id', flat=True)
            ]
        return []

    @classmethod
    def get_new(cls, current_ids: list[str], old_ids: list[str] = None, **kwargs) -> list[str]:
        """
        Get File IDs difference with OLD IDs
        """
        if old_ids is None and kwargs:
            old_ids = cls.get_old(**kwargs)
        return list(set(current_ids) - set(old_ids))

    @classmethod
    def get_keep(cls, current_ids, old_ids: list[str] = None, **kwargs) -> list[str]:
        """
        Get File IDs keep with OLD IDs
        """
        if old_ids is None and kwargs:
            old_ids = cls.get_old(**kwargs)
        return list(set(current_ids) & set(old_ids))

    @classmethod
    def get_remove(cls, current_ids: list[str], old_ids: list[str] = None, **kwargs) -> list[str]:
        """
        Get File IDs keep with OLD IDs
        """
        if old_ids is None and kwargs:
            old_ids = cls.get_old(**kwargs)
        return list(set(old_ids) - set(current_ids))

    @classmethod
    def get_doc_field_name(cls):
        raise NotImplementedError

    @classmethod
    def valid_change(  # pylint: disable=R0914
            cls,
            current_ids: list[str],
            employee_id: UUID | str,
            doc_id: UUID | str | None = None,
    ) -> (bool, dict):
        """
        Valid attachment sent to serve update.
        Args:
            current_ids:
            employee_id:
            doc_id:

        Returns:
            Dict:
                new: List[Files]
                keep: List[Files]
                remove: List[Files]
                errors: List[Files]
        """
        result = {'new': [], 'keep': [], 'remove': [], 'errors': []}
        doc_field_name = cls.get_doc_field_name()

        if employee_id and doc_field_name:
            old_objs = cls.objects.filter(
                **{doc_field_name + '_id': doc_id}
            ) if doc_id and doc_field_name else cls.objects.none()
            old_ids = [str(obj.attachment_id) for obj in old_objs]

            if not cls.has_change(current_ids=current_ids, old_ids=old_ids):
                result['keep'] = list(old_objs)
                return True, result

            file_objs = Files.objects.filter(id__in=current_ids)
            if file_objs.count() == len(current_ids):
                new_ids = cls.get_new(current_ids=current_ids, old_ids=old_ids)
                remove_ids = cls.get_remove(current_ids=current_ids, old_ids=old_ids)

                new_errs, new_objs, keep_objs, remove_objs = [], [], [], []
                for obj in file_objs:
                    if str(obj.id) in new_ids:
                        (
                            new_objs if obj.check_available_file(employee_id=employee_id, doc_id=doc_id) else new_errs
                        ).append(obj)
                    elif str(obj.id) in remove_ids:
                        remove_objs.append(obj)
                    else:
                        keep_objs.append(obj)

                result['errors'] = new_errs
                result['new'] = new_objs
                result['keep'] = keep_objs
                result['remove'] = remove_objs

                if new_errs:
                    return False, result
                return True, result
        return False, result

    @classmethod
    def resolve_change(cls, result, doc_id, doc_app) -> (bool, str):
        """
        Resolve data after valid.
        Args:
            doc_app: Application object of feature
            doc_id: Document ID related
            result: [Dict]
                Errors: List[Files]
                New: List[Files]
                Keep: List[Files]
                Remove: List[Files]

        Returns:
            Bool: State resolve change
        """
        doc_field_name = cls.get_doc_field_name()

        if result and isinstance(result, dict) and not result.get('errors', []) and doc_field_name:
            new_objs: list[Files] = result['new']
            remove_objs = result['remove']

            try:
                with transaction.atomic():
                    if new_objs:
                        # install m2m and update relate data of Files
                        counter = len(new_objs) + 1
                        m2m_bulk = []
                        for obj in new_objs:
                            tmp_obj = cls(attachment=obj, order=counter, **{doc_field_name + '_id': doc_id})
                            m2m_bulk.append(tmp_obj)
                            counter += 1
                            obj.link(doc_id=doc_id, doc_app=doc_app)
                        cls.objects.bulk_create(m2m_bulk)

                    if remove_objs:
                        # remove relate data after destroy m2m
                        for m2m_obj in cls.objects.filter(**{doc_field_name: doc_id}, attachment__in=remove_objs):
                            if m2m_obj.attachment:
                                m2m_obj.attachment.unlink()
                            m2m_obj.remove()

                    return True
            except Exception as err:
                logger.error(msg=f'[M2MFiles][resolve_change] errors: {str(err)}')
        return False

    class Meta:
        abstract = True
        ordering = ('-date_created',)
        default_permissions = ()

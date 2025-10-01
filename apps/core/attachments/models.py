__all__ = [
    'Files', 'M2MFilesAbstractModel',
    'PublicFiles', 'Folder', 'FolderPermission', 'FilePermission', 'update_files_is_approved',
    'processing_folder',
]

import json
import logging
from copy import deepcopy

from typing import Union
from uuid import UUID

from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from apps.core.attachments.folder_utils import HIERARCHY_RULES, MODULE_MAPPING, APP_FIELD, APP_NAME
from apps.shared import MasterDataAbstractModel, TypeCheck, StringHandler, HrMsg, AttMsg, SimpleAbstractModel, \
    DisperseModel
from apps.core.attachments.storages.aws.storages_backend import (
    PrivateMediaStorage, FileSystemStorage,
    PublicMediaStorage,
)

logger = logging.getLogger(__name__)

FILE_BELONG_TO = (
    (0, 'Self'),
    (1, 'Company'),
)

CAPABILITY_LIST = (
    (1, 'Preview'),
    (2, 'Viewer'),
    (3, 'Editor'),
    (4, 'Custom')
)

FOLDER_LIST = (
    (1, 'See'),
    (2, 'Upload'),
    (3, 'Download'),
    (4, 'Create subfolders'),
    (5, 'Delete'),
    (6, 'Share'),
)

FILE_LIST = (
    (1, 'Review'),
    (2, 'Download'),
    (3, 'Edit file attributes'),
    (4, 'Share'),
    (5, 'Upload version'),
    (6, 'Duplicate'),
    (7, 'Edit file'),
)


def make_sure_filename_length(_filename):
    if len(_filename) > 30:
        arr_tmp = _filename.split(".")
        f_name, f_ext = slugify("".join(arr_tmp[:-1])), arr_tmp[-1]
        f_name = f'{f_name[:20]}_{StringHandler.random_str(9 - len(f_ext) - 1)}'
        return f'{f_name.lower()}.{f_ext.lower()}'
    return _filename


def generate_path_file(instance, filename):
    if instance.company_id:
        if instance.employee_created_id:
            company_path = str(instance.company_id).replace('-', '')
            employee_path = str(instance.employee_created_id).replace('-', '')
            return f"{company_path}/{employee_path}/{make_sure_filename_length(filename)}"
        raise ValueError('Attachment require employee related')
    raise ValueError('Attachment require company related')


def generate_path_public_file(instance, filename):
    if instance.company_id:
        if instance.employee_created_id:
            now_str = timezone.now()
            company_path = str(instance.company_id).replace('-', '')
            return f"{company_path}/{now_str.year}/{now_str.month}/{now_str.day}/{make_sure_filename_length(filename)}"
        raise ValueError('Attachment require employee related')
    raise ValueError('Attachment require company related')


def update_folder_title(doc_obj=None, folder_obj=None):
    result_name = deepcopy(doc_obj.title)
    if len(result_name) > 35:
        one_third = len(result_name) // 3
        result_name = f'{result_name[:one_third]}...{result_name[-one_third:]}'
    if doc_obj and folder_obj:
        folder_obj.doc_code = doc_obj.code
        folder_obj.title = f'{doc_obj.code}-{result_name}'
        folder_obj.save(update_fields=['doc_code', 'title'])


def update_files_is_approved(doc_files_list, doc_obj):
    bulk_files_update = []
    folder_obj = None
    for file in doc_files_list:
        file.attachment.is_approved = True
        folder_obj = file.attachment.folder
        bulk_files_update.append(file.attachment)
    if bulk_files_update:
        Files.objects.bulk_update(bulk_files_update, fields=['is_approved'])
    update_folder_title(doc_obj, folder_obj)


def find_function_in_hierarchy(module_name, search_string):
    # Kiểm tra module có tồn tại không
    if module_name not in HIERARCHY_RULES:
        return ''

    def process_child_content(child_value, doc_models_code, path, base_path):
        this_path = []
        if isinstance(child_value, dict):
            this_path = search_in_dict(child_value, path, base_path)
        elif isinstance(child_value, set):
            for item in child_value:
                if item == doc_models_code:
                    full_path = f"{base_path}.{item}" if base_path else item
                    this_path.append(full_path)
        return this_path

    def search_in_dict(data, path="", parent_path=""):
        """Hàm đệ quy để tìm kiếm trong cấu trúc lồng nhau"""

        results = []
        if not isinstance(data, dict):
            return results
        for key, value in data.items():
            # Bỏ qua key 'child' vì nó không phải là tên chức năng
            if key == 'child':
                # Tiếp tục tìm kiếm trong child
                results.extend(process_child_content(value, search_string, path, parent_path))

            else:
                # Xây dựng đường dẫn hiện tại
                current_path = f"{path}.{key}" if path else key

                # Kiểm tra xem key có phải là string cần tìm không
                if key == search_string:
                    results.append(current_path)

                # Tiếp tục tìm kiếm sâu hơn
                if isinstance(value, dict):
                    # Tìm trong value
                    nested_results = search_in_dict(value, current_path, current_path)
                    results.extend(nested_results)

                    # Tìm trong child nếu có
                    if 'child' in value:
                        results.extend(process_child_content(value['child'], search_string, current_path, current_path))

        return results

    # Bắt đầu tìm kiếm từ module được chỉ định
    found_paths = search_in_dict(HIERARCHY_RULES[module_name], module_name)
    temp_lst = list(set(found_paths))
    sorted_lst = sorted(temp_lst, key=len, reverse=True)
    return sorted_lst


def get_parent_func(child_obj, parent_code):
    parent_obj = getattr(child_obj, parent_code, None)
    if parent_code == 'service_order_work_order_task_task':
        is_all = parent_obj.all()
        if is_all.exists():
            return is_all.first().work_order.service_order
        return None
    return parent_obj


def find_correct_path(object_name, object_instance, path_current_lst):
    def validate_path(path):

        path_parts = path.split('.')

        obj_index = path_parts.index(object_name)

        # Duyệt ngược từ object lên các parent
        current_obj = object_instance
        parent_obj_lst = {}
        for idx in range(obj_index - 1, -1, -1):
            lst_app_code = path_parts[idx]

            # Nếu là 'root folder' hoặc không có trong APP_FIELD -> record này không có cấp cha
            if lst_app_code in ['sale', 'e-ofice', 'hrm', 'kms'] or lst_app_code not in APP_FIELD:
                continue

            # Lấy field cần kiểm tra cho parent này
            parent_fields = APP_FIELD[lst_app_code]

            if hasattr(current_obj, parent_fields) and getattr(current_obj, parent_fields):
                temp_obj = get_parent_func(current_obj, parent_fields)
                if temp_obj:
                    current_obj = temp_obj
                    parent_obj_lst[lst_app_code] = current_obj
                else:
                    return False, {}
            else:
                return False, {}
        # Đã kiểm tra hết chain và đều hợp lệ
        return True, parent_obj_lst

    # Tìm path đúng trong danh sách
    for item in path_current_lst:
        is_check, lst_match = validate_path(item)
        if is_check:
            return item, lst_match

    return None, {}


def cu_folder_form_path(app_code, obj_doc, parent_folder):
    app_models = DisperseModel(app_model='base.Application').get_model()
    application_flt = app_models.objects.filter(model_code=app_code)
    if application_flt.exists():
        app_current_obj = application_flt.first()
    else:
        return False

    folder_label, _ = Folder.objects.get_or_create(
        company_id=obj_doc.company_id,
        tenant_id=obj_doc.tenant_id,
        parent_n=parent_folder,
        title=APP_NAME[app_code],
        is_system=True,
        defaults={
            'title': APP_NAME[app_code],
            'company_id': obj_doc.company_id,
            'tenant_id': obj_doc.tenant_id,
            'parent_n': parent_folder,
            'is_system': True
        }
    )
    # generate name for app folder
    result_name = deepcopy(obj_doc.title)
    if len(result_name) > 35:
        one_third = len(result_name) // 3
        result_name = f'{result_name[:one_third]}...{result_name[-one_third:]}'

    folder_app, _ = Folder.objects.get_or_create(
        application=app_current_obj,
        doc_id=obj_doc.id,
        # doc_code=obj_doc.code,
        is_system=True,
        parent_n=folder_label,
        defaults={
            'title': f'{obj_doc.code}-{result_name}',
            'doc_id': obj_doc.id,
            'doc_code': obj_doc.code if obj_doc.code else None,
            'application': app_current_obj,
            'company_id': obj_doc.company_id,
            'tenant_id': obj_doc.tenant_id,
            'parent_n': folder_label,
            'is_system': True
        }
    )
    current_folder = folder_app
    if app_code == 'serviceorder':
        current_folder, _ = Folder.objects.get_or_create(
            is_system=True,
            parent_n=current_folder,
            defaults={
                'title': 'Work order',
                'parent_n': current_folder,
                'is_system': True,
                'company_id': obj_doc.company_id,
                'tenant_id': obj_doc.tenant_id,
            }
        )
    return current_folder


def get_doc_obj_from_id(id_doc, app_obj):
    model_cls = DisperseModel(app_model=f'{app_obj.app_label}.{app_obj.model_code}').get_model()
    if model_cls and hasattr(model_cls, 'objects'):
        try:
            return model_cls.objects.get(pk=id_doc)
        except model_cls.DoesNotExist:
            raise ValueError('Document Object is not found ' + id_doc)
    raise ValueError('Model Doc not found: ' + id_doc)


def processing_folder(doc_id, doc_app):
    """logic của func:
    - từ thông tin có sẵn tìm ra danh sách path folder đúng của doc_obj
    - loop trong danh sách path chính xác tạo folder theo path và trả về folder của chính phiếu đó
    """

    doc_obj = get_doc_obj_from_id(doc_id, doc_app)
    # get code of doc code via config
    folder_obj_lst = Folder.objects.filter(
        application=doc_app,
        is_system=True,
        **({'doc_code': doc_obj.code} if doc_obj.code else {'title': f'-{doc_obj.title}'})
    )
    if folder_obj_lst.exists():
        folder_obj = folder_obj_lst.first()
    else:
        folder_system_obj, _ = Folder.objects.get_or_create(
            id=MODULE_MAPPING['system']['id'],
            defaults={
                'id': MODULE_MAPPING['system']['id'],
                'title': MODULE_MAPPING['system']['name'],
                'company': doc_obj.company,
                'tenant': doc_obj.tenant,
                'is_system': True
            }
        )
        result_name = doc_obj.title if len(
            doc_obj.title
        ) > 35 else f'{doc_obj.title[:len(doc_obj.title) // 3]}...{doc_obj.title[-(len(doc_obj.title) // 3):]}'
        # tạo folder theo doc_code và app
        folder_obj, _ = Folder.objects.get_or_create(
            application=doc_app,
            doc_id=doc_obj.id,
            # doc_code=doc_obj.code,
            is_system=True,
            defaults={
                'title': f'{doc_obj.code}-{result_name}',
                'company': doc_obj.company,
                'tenant': doc_obj.tenant,
                'application': doc_app,
                'doc_id': doc_obj.id,
                'doc_code': doc_obj.code if doc_obj.code else None,
                'is_system': True
            }
        )
        # lấy danh sách plan và kiểm tra doc code có trong tất cả app và plan
        list_plans = [item.title for item in doc_app.plans.all()]
        path_current_lst = []
        for plan in list_plans:
            path_current_lst += find_function_in_hierarchy(plan.lower(), doc_app.model_code)
        path_str, obj_path_dict = find_correct_path(doc_app.model_code, doc_obj, path_current_lst)
        if path_str:
            path_lst = path_str.split('.')
            current_folder_path = None
            for path in path_lst:
                if path == doc_app.model_code:
                    if len(path_lst) == 2 and path_lst[0] in ['sale', 'e-office', 'hrm', 'kms']:
                        current_folder_path, _ = Folder.objects.get_or_create(
                            title=APP_NAME[path],
                            parent_n=current_folder_path,
                            company_id=doc_obj.company_id,
                            tenant_id=doc_obj.tenant_id,
                            defaults={
                                'title': APP_NAME[path],
                                'company_id': doc_obj.company_id,
                                'tenant_id': doc_obj.tenant_id,
                                'is_system': True,
                                'parent_n': current_folder_path
                            }
                        )
                    # check folder work order
                    if current_folder_path.title == 'Work order' and current_folder_path.is_system is True:
                        folder_obj.delete()
                        folder_obj = current_folder_path
                        break
                    folder_obj.parent_n = current_folder_path
                    folder_obj.save(update_fields=['parent_n'])
                    break
                if path in MODULE_MAPPING:
                    current_folder_path, _ = Folder.objects.get_or_create(
                        id=MODULE_MAPPING[path]['id'],
                        company_id=doc_obj.company_id,
                        tenant_id=doc_obj.tenant_id,
                        defaults={
                            'id': MODULE_MAPPING[path]['id'],
                            'title': MODULE_MAPPING[path]['name'],
                            'company_id': doc_obj.company_id,
                            'tenant_id': doc_obj.tenant_id,
                            'is_system': True,
                            'parent_n': folder_system_obj
                        }
                    )
                else:
                    current_folder_path = cu_folder_form_path(path, obj_path_dict[path], current_folder_path)
    return folder_obj


class BastionFiles(MasterDataAbstractModel):
    file_name = models.TextField()
    file_size = models.IntegerField()  # bytes
    file_type = models.CharField(max_length=100)
    file = models.FileField(storage=FileSystemStorage, upload_to=generate_path_file)
    remarks = models.TextField(blank=True)

    # data link files
    relate_app = models.ForeignKey(
        'base.Application',
        null=True,
        on_delete=models.SET_NULL,
    )
    relate_app_code = models.CharField(max_length=100, null=True)
    relate_doc_id = models.UUIDField(null=True)

    # file attributes
    document_type = models.ForeignKey(
        'documentapproval.KMSDocumentType',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(app_label)s_%(class)s_document_type'
    )
    content_group = models.ForeignKey(
        'documentapproval.KMSContentGroup',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(app_label)s_%(class)s_content_group'
    )

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
            'document_type': {
                'id': str(self.document_type_id), 'title': self.document_type.title
            } if self.document_type else {},
            'content_group': {
                'id': str(self.content_group_id), 'title': self.content_group.title
            } if self.content_group else {},
            **(
                {'link': self.get_url()} if has_link else {}
            )
        }

    def delete(self, using=None, keep_parents=False, force_storage=False):
        super().delete(using=using, keep_parents=keep_parents)
        # delete in AWS
        if force_storage is True:
            self.file.storage.delete(self.file.name)

    class Meta:
        abstract = True
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def get_used_size(cls, **kwargs) -> int | None:
        file_size__sum = Files.objects.filter_current(**kwargs).aggregate(
            file_size__sum=models.Sum('file_size', default=0)
        )['file_size__sum']
        if isinstance(file_size__sum, int):
            return file_size__sum
        return None


class PublicFiles(BastionFiles):
    file = models.FileField(storage=PublicMediaStorage, upload_to=generate_path_public_file)

    # relate_app_code = 'SYS:WEB_BUILDER' for feature web_builder | because web_builder is not application

    @classmethod
    def get_used_of_web_builder(cls, company_id):
        return cls.get_used_size(company_id=company_id, relate_app_code=settings.FILE_WEB_BUILDER_RELATE_APP)

    class Meta:
        verbose_name = 'Public Files'
        verbose_name_plural = 'Public Files'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class Files(BastionFiles):
    """
    Attachment was uploaded by Employee

    Stage 1: Upload file
        Field require: tenant, company, employee_created, file, file_name, file_size, file_type
    Stage 2: Related attachment to Document Objects
        Field require: relate_app, relate_app_code, relate_doc_id
    """

    file = models.FileField(storage=PrivateMediaStorage, upload_to=generate_path_file)
    folder = models.ForeignKey(
        'attachments.Folder',
        on_delete=models.SET_NULL,
        verbose_name='folder of file',
        related_name='files_folder',
        null=True,
    )
    is_approved = models.BooleanField(
        default=False, help_text="This flag indicates that the file has been belong to system"
    )

    @classmethod
    def check_available_size_employee(cls, employee_id, new_size=None) -> (bool, str, str):
        if employee_id and TypeCheck.check_uuid(employee_id):
            file_size__sum = cls.get_used_size(
                fill__tenant=True, fill__company=True, employee_created_id=employee_id,
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
                    obj.save(
                        update_fields=[
                            'relate_app', 'relate_app_code', 'relate_doc_id',
                        ]
                    )
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
                            obj_unused.save(
                                update_fields=[
                                    'relate_app', 'relate_app_code', 'relate_doc_id',
                                ]
                            )
                    elif unused_resolve == 'delete':
                        # "Case: Unused was destroyed permanent"
                        unused_linked.delete()

                return result
        raise ValueError('SOME_REQUIRED_DATA_DONT_HAVE_VALUE')

    def save(self, *args, **kwargs):
        if not self.relate_app_code and self.relate_app:
            self.relate_app_code = getattr(self.relate_app, 'code', None)
        super().save(*args, **kwargs)

    def check_available_file(self, employee_id: UUID | str, doc_id: UUID | str = None):
        if str(self.employee_created_id) != str(employee_id):
            return False
        if doc_id is None and self.relate_doc_id is not None:
            return False
        if doc_id and self.relate_doc_id and str(doc_id) != str(self.relate_doc_id):
            return False
        return True

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
                for old_obj in old_objs:
                    if str(old_obj.attachment.id) in remove_ids:
                        remove_objs.append(old_obj.attachment)
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
                    # handle add new files
                    if new_objs:
                        # check and get folder system of files
                        folder_obj = processing_folder(doc_id, doc_app)
                        counter = len(new_objs) + 1
                        m2m_bulk = []
                        for obj in new_objs:
                            m2m_bulk.append(cls(attachment=obj, order=counter, **{doc_field_name + '_id': doc_id}))
                            counter += 1
                            obj.link(doc_id=doc_id, doc_app=doc_app)
                            update_fields = []
                            if doc_app.is_workflow is False:
                                obj.is_approved = True
                                update_fields.append('is_approved')
                            if folder_obj:
                                obj.folder = folder_obj
                                update_fields.append('folder')
                            if len(update_fields) > 0:
                                obj.save(update_fields=update_fields)
                        cls.objects.bulk_create(m2m_bulk)
                    # handle remove files
                    if remove_objs:
                        # remove relate data after destroy m2m
                        for m2m_obj in cls.objects.filter(**{doc_field_name: doc_id}, attachment__in=remove_objs):
                            if m2m_obj.attachment:
                                m2m_obj.attachment.unlink()
                                if m2m_obj.attachment.folder:
                                    m2m_obj.attachment.folder = None
                                    m2m_obj.attachment.save(update_fields=['folder'])
                            m2m_obj.delete()
                    return True
            except Exception as err:
                logger.error(msg=f'[M2MFiles][resolve_change] errors: {str(err)}')
        return False

    class Meta:
        abstract = True
        ordering = ('-date_created',)
        default_permissions = ()


# BEGIN FOLDER
class Folder(MasterDataAbstractModel):
    application = models.ForeignKey('base.Application', on_delete=models.CASCADE, null=True)
    doc_id = models.UUIDField(verbose_name='Document ID', null=True)
    doc_code = models.CharField(max_length=250, blank=True, null=True)
    parent_n = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        verbose_name="parent folder",
        related_name="folder_parent_n",
        null=True,
    )
    employee_inherit = models.ForeignKey(
        'hr.Employee', null=True, on_delete=models.SET_NULL,
        help_text='',
        related_name='folder_employee_inherit',
    )
    is_system = models.BooleanField(default=False, help_text="flag to know this folder auto created by system")
    is_owner = models.BooleanField(default=False, help_text="flag to know this folder created by owner")
    is_admin = models.BooleanField(default=False, help_text="flag to know this folder created by admin")

    class Meta:
        verbose_name = 'Folder'
        verbose_name_plural = 'Folders'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class PermissionAbstractModel(SimpleAbstractModel):
    employee_or_group = models.BooleanField(verbose_name='type of recipient', default=False)
    exp_date = models.DateTimeField(null=True)
    capability_list = models.JSONField(
        default=list,
        help_text=json.dumps(CAPABILITY_LIST),
    )
    employee_created = models.ForeignKey(
        'hr.Employee', null=True, on_delete=models.SET_NULL,
        help_text='Employee created this record',
        related_name='%(app_label)s_%(class)s_employee_creator',
    )
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )
    employee_modified = models.ForeignKey(
        'hr.Employee', on_delete=models.SET_NULL, null=True,
        help_text='Employee modified this record in last',
        related_name='%(app_label)s_%(class)s_employee_modifier'
    )
    date_modified = models.DateTimeField(
        auto_now=True,
        help_text='Date modified this record in last',
    )

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()
        indexes = [
            models.Index(fields=['id']),
        ]

    @classmethod
    def check_permission(cls, obj, employee_id, capability):
        """
        Check if an employee has the given capability on this object.
        Args:
            obj: FolderPermission or FilePermission instance
            employee_id: UUID of the employee
            capability: String like 'view', 'edit', 'delete', 'share', etc.
        Returns:
            Boolean
        """
        if not obj:
            return False
        # Normalize ID
        employee_id = str(employee_id).replace('-', '')
        # Creator always has full access
        if str(obj.employee_created_id).replace('-', '') == employee_id:
            return True
        # Capability must be in list
        if capability not in obj.capability_list:
            return False

        # Check if employee in group
        # if employee_id not in obj.group.employee_list:
        #     return False

        # Check expiration if enabled
        if obj.exp_date and obj.exp_date <= timezone.now():
            return False

        return True


class FilePermission(PermissionAbstractModel):
    file = models.ForeignKey(
        "attachments.Files",
        on_delete=models.CASCADE,
        verbose_name="file permission",
        related_name="file_permission_file",
    )
    employee_list = models.JSONField(
        help_text='{"uuid": {"id":"uuid", "full_name": "Nguyen Van A", "group": {}}}',
        default=dict
    )
    group_list = models.JSONField(
        help_text='{"uuid": {"id":"uuid", "title": "Group A", "parent_n": "uuid"}}',
        default=dict
    )
    file_perm_list = models.JSONField(
        default=list,
        help_text=json.dumps(FILE_LIST),
        null=True,
    )

    class Meta:
        verbose_name = 'File Permission'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class FolderPermission(PermissionAbstractModel):
    folder = models.ForeignKey(
        "attachments.Folder",
        on_delete=models.CASCADE,
        verbose_name="folder permission",
        related_name="folder_permission_folder",
    )
    employee_list = models.JSONField(
        help_text=json.dumps({"uuid": {"id": "uuid", "full_name": "Nguyen Van A", "group": {}}}),
        default=dict
    )
    group_list = models.JSONField(
        help_text=json.dumps({"uuid": {"id": "uuid", "title": "Group A", "parent_n": "uuid"}}),
        default=dict
    )
    folder_perm_list = models.JSONField(
        default=list,
        help_text=json.dumps(FOLDER_LIST),
        null=True,
    )
    file_in_perm_list = models.JSONField(
        default=list,
        help_text=json.dumps(FILE_LIST),
        null=True,
    )
    is_apply_sub = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Folder Permission'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

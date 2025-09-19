__all__ = [
    'Files', 'M2MFilesAbstractModel',
    'PublicFiles', 'Folder', 'FolderPermission', 'FilePermission', 'update_files_is_approved'
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

MODULE_MAPPING = {
    'system': {'name': 'System', 'id': '9ac02039-a9a4-42e9-825e-169f740b5b5b'},
    'sale': {  # SAlE
        'name': 'Sale', 'id': '76ab081b-eee4-4923-97b9-1cbb09deef78', 'plan': '4e082324-45e2-4c27-a5aa-e16a758d5627'
    },
    'kms': {  # KMS
        'name': 'KMS', 'id': 'c7a702aa-10e7-487a-ab6c-3fd219930504', 'plan': '02793f68-3548-45c1-98f5-89899a963091'
    },
    'hrm': {  # HRM
        'name': 'HRM', 'id': '3802739f-12c8-4f90-ac67-3f81e21ccffe', 'plan': '395eb68e-266f-45b9-b667-bd2086325522'
    },
    'e-office': {  # E-Office
        'name': 'E-Office', 'id': '57bc22f9-08a8-4a4b-b207-51c0f6428c56', 'plan': 'a8ca704a-11b7-4ef5-abd7-f41d05f9d9c8'
    }

}

HIERARCHY_RULES = {
    'sale': {
        'apinvoice': {},
        'arinvoice': {},
        'bidding': {},
        'advancepayment': {},
        'payment': {},
        'consulting': {},
        'contractapproval': {},
        'orderdeliverysub': {},
        'equipmentloan': {},
        'goodsissue': {},
        'goodsreceipt': {},
        'goodsreturn': {},
        'leaseorder': {},
        'opportunity': {
            'child': {
                'opportunitytask': {},
                'serviceorder': {
                    'child': {
                        'opportunitytask'
                    }
                }
            }
        },
        'purchaseorder': {},
        'purchasequotationrequest': {},
        'purchaserequest': {},
        'quotation': {},
        'saleorder': {},
        'serviceorder': {
            'child': {
                'opportunitytask'
            },
        },
        'opportunitytask': {}
    },
    'e-office': {
        'assettoolsreturn': {},
        'assettoolsdelivery': {},
        'assettoolsprovide': {},
        'businessrequest': {},
        'meetingschedule': {},
    },
    'hrm': {
        'employeeinfo': {
            'child': {
                'employeecontract': {}
            }
        },
    },
    'kms': {
        'kmsdocumentapproval': {},
        'kmsincomingdocument': {}
    }
}
# trường này để truy vấn ngược từ app con lên app cha thông qua field dược khai báo
APP_FIELD = {
    'employeeinfo': ['employee_info'],
    'serviceorder': ['service_order_work_order_task_task'],
    'opportunity': ['opportunity']
}
xx = [
    'sale.opportunitytask',
    'sale.serviceorder.opportunitytask',
    'sale.opportunity.serviceorder.opportunitytask',
    'sale.opportunity.opportunitytask'
]


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


def update_files_is_approved(doc_files_list):
    bulk_files_update = []
    for file in doc_files_list:
        file.attachment.is_approved = True
        bulk_files_update.append(file.attachment)
    if bulk_files_update:
        Files.objects.bulk_update(bulk_files_update, fields=['is_approved'])


def find_function_in_hierarchy(module_name, search_string):
    # Kiểm tra module có tồn tại không
    if module_name not in HIERARCHY_RULES:
        return ''

    def search_in_dict(data, path="", parent_path=""):
        """Hàm đệ quy để tìm kiếm trong cấu trúc lồng nhau"""
        results = []
        if isinstance(data, dict):
            for key, value in data.items():
                # Bỏ qua key 'child' vì nó không phải là tên chức năng
                if key == 'child':
                    # Tiếp tục tìm kiếm trong child
                    if isinstance(value, dict):
                        child_results = search_in_dict(value, path, parent_path)
                        results.extend(child_results)
                    elif isinstance(value, set):
                        for item in value:
                            if item == search_string:
                                full_path = f"{parent_path}.{item}" if parent_path else item
                                results.append(full_path)
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
                            child_data = value['child']
                            if isinstance(child_data, dict):
                                child_results = search_in_dict(child_data, current_path, current_path)
                                results.extend(child_results)
                            elif isinstance(child_data, set):
                                for item in child_data:
                                    if item == search_string:
                                        child_path = f"{current_path}.{item}"
                                        results.append(child_path)

        return results

    # Bắt đầu tìm kiếm từ module được chỉ định
    module_data = HIERARCHY_RULES[module_name]
    found_paths = search_in_dict(module_data, module_name)
    return list(set(found_paths))


def get_parent_func(child_obj, parent_code):
    if hasattr(child_obj, APP_FIELD[parent_code]):
        parent_obj = getattr(child_obj, APP_FIELD[parent_code])
        if parent_code == 'serviceorder':
            return parent_obj.work_order.service_order
        return parent_obj
    return None


def find_correct_path(object_name, object_instance, path_current_lst):
    """
    tìm đúng app đang trong danh sách path nào
    """

    def validate_path(path):
        """Kiểm tra một path cụ thể xem có đây đủ các record không"""

        path_parts = path.split('.')

        obj_index = path_parts.index(object_name)

        # Duyệt ngược từ object lên các parent
        current_obj = object_instance
        parent_obj_lst = {}
        for i in range(obj_index - 1, -1, -1):
            lst_app_code = path_parts[i]

            # Lấy field cần kiểm tra cho parent này
            parent_fields = APP_FIELD[lst_app_code]

            # Nếu là 'root folder' hoặc không có trong APP_FIELD -> record này không có cấp cha
            if lst_app_code in ['sale', 'e-ofice', 'hrm', 'kms'] or lst_app_code not in APP_FIELD:
                continue

            # Kiểm tra current object có parent này không
            has_this_parent = False

            for field in parent_fields:
                if hasattr(current_obj, field) and getattr(current_obj, field):
                    # Có parent, lấy parent object để kiểm tra tiếp
                    parent_obj = getattr(current_obj, field)
                    current_obj = get_parent_func(parent_fields, parent_obj)
                    parent_obj_lst[lst_app_code] = deepcopy(current_obj)
                    has_this_parent = True
                    break

            if not has_this_parent:
                # Path này không khớp vì object ko có parent này
                return False

        # Đã kiểm tra hết chain và đều hợp lệ
        return True, parent_obj_lst

    # Tìm path đúng trong danh sách
    for item in path_current_lst:
        is_check, lst_match = validate_path(item)
        if is_check:
            return item, lst_match

    return None, {}


def processing_folder(doc_id, doc_app):
    # lấy doc obj theo doc app
    # lấy code của doc (code của doc được setup để lấy theo cấu hình or generate tự động)
    # filter folder theo application và document code nếu có thì trả về nếu không thì tạo mới theo cấu trúc thư mục
    doc_code = doc_app.model_code

    def get_doc_obj_from_id(id_doc, app_obj):
        model_cls = DisperseModel(app_model=f'{app_obj.app_label}.{app_obj.model_code}').get_model()
        if model_cls and hasattr(model_cls, 'objects'):
            try:
                return model_cls.objects.get(pk=id_doc)
            except model_cls.DoesNotExist:
                logger.error( f'[processing_folder] '
                              f'Document Object is not found doc={id_doc}')
                raise ValueError('Document Object is not found ' + id_doc)
        logger.error(
            f'[processing_folder] '
            f'Model Doc not found: doc={doc_id} - app={doc_app}'
        )
        raise ValueError('Model Doc not found: ' + doc_id + ' - ' + doc_app)

    doc_obj = get_doc_obj_from_id(doc_id, doc_app)
    # get code of doc code via config
    parsed_code = doc_obj.code
    if not parsed_code:
        raise ValueError('Code of document related attachment is Null can not create folder')

    folder_obj_lst = Folder.objects.filter(application=doc_app, doc_code=parsed_code, is_system=True)
    if folder_obj_lst.exists():
        folder_obj = folder_obj_lst.first()
    else:
        # tạo hoặc get system folder
        folder_system_obj, _ = Folder.objects.get_or_create(
            id=MODULE_MAPPING['system']['id'],
            defaults={
                'title': MODULE_MAPPING['system']['name'],
                'company': doc_obj.company,
                'tenant': doc_obj.tenant,
                'application': doc_app,
                'is_system': True
            }
        )
        folder_name = deepcopy(doc_obj.title)
        folder_name_length = len(folder_name)
        result_name = deepcopy(folder_name)
        if folder_name_length > 35:
            one_third = folder_name_length // 3
            result_name = f'{folder_name[:one_third]}...{folder_name[-one_third:]}'
        # tạo folder theo doc_code và app
        folder_obj, _ = Folder.objects.create(
            title=f'{parsed_code}-{result_name}',
            doc_code=parsed_code,
            application=doc_app,
            is_system=True,
            company=doc_obj.company,
            tenant=doc_obj.tenant,
        )

        # lấy danh sách plan và kiểm tra doc code có trong tất cả app và plan
        list_plans = [item.title for item in doc_app.plans]
        path_current_lst = []
        for plan in list_plans:
            path_current_lst += find_function_in_hierarchy(plan, doc_code)

        doc_path, obj_path_dict = find_correct_path(doc_code, doc_obj, path_current_lst)

        if doc_path:
            print('doc_path: >>', doc_path)
            print('obj_path_dict: >>', obj_path_dict)

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
        on_delete=models.CASCADE,
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
                    if new_objs:
                        # folder_obj = Folder.objects.filter_on_company(application=doc_app, is_system=True)
                        folder_obj = processing_folder(doc_id, doc_app)

                        counter = len(new_objs) + 1
                        m2m_bulk = []
                        for obj in new_objs:
                            m2m_bulk.append(cls(attachment=obj, order=counter, **{doc_field_name + '_id': doc_id}))
                            counter += 1
                            obj.link(doc_id=doc_id, doc_app=doc_app)
                            if folder_obj:
                                obj.folder = folder_obj
                                obj.save(update_fields=['folder'])
                        cls.objects.bulk_create(m2m_bulk)

                    if remove_objs:
                        # remove relate data after destroy m2m
                        for m2m_obj in cls.objects.filter(**{doc_field_name: doc_id}, attachment__in=remove_objs):
                            if m2m_obj.attachment:
                                m2m_obj.attachment.unlink()
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
    doc_code = models.CharField(unique=True, max_length=250, blank=True, null=True)
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

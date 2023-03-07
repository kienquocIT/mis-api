import json
from copy import deepcopy
from typing import Union, Literal
from uuid import uuid4, UUID

from django.apps import apps
from django.db import models
from django.utils import timezone
from jsonfield import JSONField

from .utils import TypeCheck, UUIDEncoder
from .managers import GlobalManager, PrivateManager, TeamManager, NormalManager, MasterDataManager
from .constant import DOCUMENT_MODE, SYSTEM_STATUS, PERMISSION_OPTION
from .formats import FORMATTING
from .permissions import PermOption
from .caches import CacheController

__all__ = [
    'DisperseModel', 'CacheCoreModel', 'AbstractBaseModel',
    'BaseModel', 'TenantModel', 'TenantCoreModel', 'M2MModel',
    'MasterDataModel', 'PermissionCoreModel'
]


class DisperseModel:
    """
    Get model class with name of models and apps.
    """
    setup_called = False
    app_label = None
    model = None
    class_model = None

    def __init__(self, **kwargs):
        app_model = kwargs.get("app_model", None)
        if app_model:
            if '_' in app_model:
                app_tmp, model_tmp = app_model.split("_")
            elif '.' in app_model:
                app_tmp, model_tmp = app_model.split(".")
            else:
                raise AttributeError(
                    "App models must be required. It's format is  {app_name}_{model name} or {app_name}.{model name}"
                )
            self.setup(app_label=app_tmp.lower(), model_name=model_tmp.lower())
        else:
            raise AttributeError("App models must be required. It's format is  {app_name}_{model name}.")

    def setup(self, app_label, model_name):
        if app_label and model_name:
            self.app_label = app_label
            self.model = model_name
            self.setup_called = True
            return True
        raise Exception(
            f"[{str(self.__class__.__name__)}] " f"app_label, model_name are required."
        )

    def __call__(self, *args, **kwargs):
        return self.get_model()

    def get_model(self) -> models.Model:
        if self.setup_called:
            self.class_model = apps.get_model(
                app_label=self.app_label, model_name=self.model
            )
            return self.class_model
        raise Exception(
            f"[{str(self.__class__.__name__)}] "
            f"Execute setup() function before call get_model() function."
        )


# abstract model
class CacheCoreModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    @property
    def key_cache_prefix(self) -> str:
        """
        Return prefix key cache
        """
        return f'{self.__class__._meta.app_label}.{self.__class__.__name__}'

    @classmethod
    def key_cache(cls, doc_id: Union[UUID, str]) -> str:
        """
        Return key save to cache.
        """
        return str(f'{cls().key_cache_prefix}_{str(doc_id)}').lower()

    @property
    def data_cache(self) -> dict:
        """
        Return data save to cache
        """
        raise NotImplementedError('This data_cache function must be override.')

    def force_cache(self, data=None):
        """
        Force save key:data to cache
        """
        if not data:
            data = self.data_cache
        CacheController().set(
            key=self.key_cache(self.id),
            value=data,
            expires=60 * 24 * 3  # 3 days
        )
        return data

    def get_cache_obj(self, auto_cache: bool = True):
        """
        Support get cache and auto get data after save cache if not exist.
        The function was called by Object Model.
        """
        data = CacheController().get(self.key_cache(self.id))
        if not data:
            try:
                data = self.data_cache
                if auto_cache:
                    self.force_cache(data)
            except Exception as err:
                print(err)
                data = None
        return data

    @classmethod
    def get_cache(cls, doc_id, auto_cache: bool = True) -> Union[None, dict]:
        """
        Support get cache and auto get data after save cache if not exist.
        The function was called by Class Model (no hit db for get PK before).
        """
        data = CacheController().get(cls.key_cache(doc_id))
        if not data:
            try:
                obj = cls.objects.get(pk=doc_id)
                data = obj.get_cache_obj(auto_cache=auto_cache)
            except Exception as err:
                print(err)
                data = None
        return data

    @classmethod
    def destroy_cache(cls, doc_id) -> bool:
        """
        Destroy cache with key auto generate by Doc ID.
        """
        return CacheController().destroy(cls.key_cache(doc_id))

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()


class AbstractBaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    objects = NormalManager()
    object_normal = NormalManager()

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

    CACHE_EXPIRES = 60 * 24 * 30  # 30 days
    KEY_CACHE_SUFFIX = 'filter'
    FIELD_SELECT_RELATED = []  # field name list that you want select_related data.

    @property
    def key_cache_prefix(self) -> str:
        """
        Return prefix key cache
        """
        return f'{self.__class__._meta.app_label}.{self.__class__.__name__}'

    @classmethod
    def key_cache(cls):
        return str(f'{cls().key_cache_prefix}_{str(cls.KEY_CACHE_SUFFIX)}').lower()

    def parse_obj(self):
        raise NotImplementedError()

    @classmethod
    def data_list_filter(cls, filter_kwargs: dict = None):
        """
        Get data from cache if exists else hit db and save to cache

        Key cache: Base.PermissionApplication__filter
        Value: {
                    '': {...data...},
                    'app_id__xxxx': {...data_filtered...},
                    ...
                }
        """

        if not filter_kwargs:
            filter_kwargs = {}

        key__child = '.'.join([f"{k}___{v}" for k, v in filter_kwargs.items()])
        data = CacheController().get(cls.key_cache())
        if not data or (data and isinstance(data, dict) and key__child not in data):
            data__child = [
                x.parse_obj() for x in cls.objects.select_related(*cls.FIELD_SELECT_RELATED).filter(**filter_kwargs)
            ]
            data__child = json.loads(json.dumps(data__child, cls=UUIDEncoder))
            if isinstance(data, dict):
                data[key__child] = data__child
            else:
                data = {key__child: data__child}
            CacheController().set(key=cls.key_cache(), value=data, expires=cls.CACHE_EXPIRES)
        return data[key__child]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.destroy_cache()

    @classmethod
    def destroy_cache(cls):
        """
        Destroy cache when change data or deploy with restart cache.
        """
        return CacheController().destroy(cls.key_cache())


# base models extend from ABSTRACT MODELS
class BaseModel(AbstractBaseModel):
    """
    Use for normal app without reference to tenant and company
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=100, blank=True)

    user_created = models.UUIDField(null=True)
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    user_modified = models.UUIDField(null=True)
    date_modified = models.DateTimeField(auto_now_add=True)

    extras = JSONField(default={})

    is_active = models.BooleanField(verbose_name="active", default=True)
    is_delete = models.BooleanField(verbose_name="delete", default=False)

    objects = NormalManager()
    object_normal = NormalManager()

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

    def parse_obj(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'code': self.code,
            'user_created': str(self.user_created),
            'date_created': str(self.date_created),
            'is_active': self.is_active,
            'extras': self.extras,
        }

    def __str__(self):
        return f'{self.title} - {self.code}'

    def get_detail(self, excludes=None):
        return self._get_detail(excludes=excludes)

    def _get_detail(self, excludes=None):
        if not isinstance(excludes, list):
            excludes = []
        result = {
            'id': str(self.id),
            'title': str(self.title) if self.title else None,
            'code': str(self.code) if self.code else None,
            'user_created': str(self.user_created) if self.user_created else None,
            'date_created': FORMATTING.parse_datetime(self.date_created),
            'user_modified': str(self.user_modified) if self.user_modified else None,
            'date_modified': FORMATTING.parse_datetime(self.date_modified),
            'extras': self.extras
        }
        if excludes:
            for f_name in excludes:
                result.pop(f_name)
        return result

    def get_old_value(self, field_name_list: list):
        """
        Get old data before call super save for compare data change.

        Solution:
            Clone object and refresh it from database.
        """
        if self._state.adding is False:
            _original_fields_old = {field: None for field in field_name_list}
            if field_name_list and isinstance(field_name_list, list):
                try:
                    self_fetch = deepcopy(self)
                    self_fetch.refresh_from_db()
                    _original_fields_old = {
                        field: getattr(self_fetch, field) for field in field_name_list
                    }
                    return _original_fields_old
                except Exception as err:
                    print(err)
            return _original_fields_old
        return {}


class TenantModel(BaseModel):
    """
    Use for all app without core (don't use foreign key to tenant and company)
    Base + Tenant ID + Company ID
    """
    tenant_id = models.UUIDField(null=True)
    company_id = models.UUIDField(null=True)
    space_id = models.UUIDField(null=True)

    mode = models.IntegerField(
        choices=DOCUMENT_MODE,
        default=0
    )
    mode_id = models.UUIDField(null=True)

    employee_created = models.UUIDField(null=True)
    employee_inherit = models.UUIDField(null=True)

    system_status = models.IntegerField(
        choices=SYSTEM_STATUS,
        default=0
    )
    system_remarks = JSONField(default={})
    process_id = models.UUIDField(null=True)

    # manager customize
    object_global = GlobalManager()
    object_private = PrivateManager()
    object_team = TeamManager()

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

    def _get_detail(self, excludes=None):
        if not isinstance(excludes, list):
            excludes = []

        result = super()._get_detail()
        if 'space_id' not in excludes:
            result['space_id'] = self.space_id
        if 'tenant_id' not in excludes:
            result['tenant_id'] = self.tenant_id
        if 'company_id' not in excludes:
            result['company_id'] = self.company_id
        if 'mode' not in excludes:
            result['mode'] = self.mode
        if 'mode_id' not in excludes:
            result['mode_id'] = self.mode_id
        return result


class TenantCoreModel(BaseModel):
    """
    Use for app in core (foreign key to tenant and company)
    Base + Tenant Obj + Company Obj
    """
    tenant = models.ForeignKey('tenant.Tenant', on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE, null=True)
    # space = models.F

    mode = models.IntegerField(choices=DOCUMENT_MODE, default=0)
    mode_id = models.UUIDField(null=True)

    # manager customize
    object_global = GlobalManager()
    object_private = PrivateManager()
    object_team = TeamManager()

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

    def _get_detail(self, excludes=None):
        if not isinstance(excludes, list):
            excludes = []

        result = super()._get_detail()
        if 'tenant' not in excludes:
            result['tenant'] = self.tenant._get_detail()  # pylint: disable=W0212,E1101
        if 'company' not in excludes:
            result['company'] = self.company._get_detail()  # pylint: disable=W0212,E1101
        if 'mode' not in excludes:
            result['mode'] = self.mode
        if 'mode_id' not in excludes:
            result['mode_id'] = self.mode_id
        return result


class M2MModel(AbstractBaseModel):
    """
    Use for reference many to many between two apps
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    extras = JSONField(default={})

    object_normal = NormalManager()

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

    def parse_obj(self):
        return {
            'id': str(self.id),
        }

    def _get_detail(self, **_kwargs):  # pylint: disable=W0613
        return {
            'id': self.id,
            'date_created': FORMATTING.parse_datetime(self.date_created),
            'extras': self.extras,
        }

    def get_detail(self, **_kwargs):  # pylint: disable=W0613
        return self._get_detail()


class MasterDataModel(AbstractBaseModel):
    """
    Use for models in master data apps
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=100, blank=True)

    tenant_id = models.UUIDField(null=True)
    company_id = models.UUIDField(null=True)

    is_active = models.BooleanField(verbose_name="active", default=True)
    is_delete = models.BooleanField(verbose_name="delete", default=False)

    # manager customize
    object_normal = NormalManager()
    object_data = MasterDataManager()

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

    def parse_obj(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'code': self.code,
            'is_active': self.is_active,
        }


class PermissionCoreModel(AbstractBaseModel):
    # by ID
    permission_by_id_sample = {
        '{code}__{app_label}__{model}': ['id1', 'id2', ]
    }
    permission_by_id = JSONField(default={})

    # by be configured
    permission_by_configured_sample = {
        '{code}__{app_label}__{model}': {
            'option': PERMISSION_OPTION
        }
    }
    permission_by_configured = JSONField(default={})

    # summary keys
    permission_keys = ('permission_by_id', 'permission_by_configured')

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

    def parse_obj(self):
        return {
            'id': str(self.id),
            'permission_by_id': self.permission_by_id,
            'permission_by_configured': self.permission_by_configured,
        }

    @property
    def permissions(self):
        return {
            'by_id': self.permission_by_id,
            'by_configured': self.permission_by_configured,
        }

    def save_permissions(self, field_name: list[str] = None) -> bool:
        if field_name is None:
            field_name = self.permission_keys
        elif isinstance(field_name, list):
            for key in field_name:
                if key not in self.permission_keys:
                    return False
        else:
            return False

        super().save(update_fields=field_name, force_update=True)
        return True

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields', None)
        if isinstance(update_fields, list):
            for key in self.permission_keys:
                if key in update_fields:
                    update_fields.remove(key)
        else:
            update_fields = []
            for f_cls in self.__class__._meta.get_fields():
                if f_cls.name not in self.permission_keys and not f_cls.auto_created and f_cls.name != 'id':
                    if f_cls.many_to_many is False:
                        update_fields.append(f_cls.name)
        kwargs['update_fields'] = update_fields
        super().save(*args, **kwargs)

    @staticmethod
    def check_perm_code(data) -> bool:
        if data and isinstance(data, str) and len(data.split('__')) == 3:
            return True
        return False

    def force_permission_by_id(
            self,
            code_perm: str, action: Literal['add', 'remove', 'drop'],
            data: list[Union[str, UUID]] = None,
            force_fetch: bool = False,
            force_save: bool = False,
    ) -> bool:
        if code_perm and self.check_perm_code(code_perm) and action and action in ['add', 'remove', 'drop']:
            # active force fetch real-data from db
            if force_fetch is True:
                self.refresh_from_db()

            # handle data
            state = False
            match action:
                case 'add':
                    if data and TypeCheck.check_uuid_list(data):
                        data_id = self.permission_by_id.get(code_perm, [])  # pylint: disable=E1101
                        data_id += data
                        self.permission_by_id[code_perm] = list(set(data_id))  # pylint: disable=E1101,E1137
                        state = True
                case 'remove':
                    if data and TypeCheck.check_uuid_list(data):
                        data_id = self.permission_by_id.get(code_perm, [])  # pylint: disable=E1101
                        if data_id and isinstance(data_id, list):
                            for idx_val in data:
                                if str(idx_val) in data_id:
                                    data_id.remove(str(idx_val))
                                    state = True
                            if state is True:
                                self.permission_by_id[code_perm] = list(set(data_id))  # pylint: disable=E1101,E1137
                case 'drop':
                    data_id = self.permission_by_id.pop(code_perm, None)  # pylint: disable=E1101
                    if data_id is not None:
                        state = True

            # the end with active save with force hit db and return state
            if state is True:
                if force_save is True:
                    self.save_permissions(['permission_by_id'])
                return True
        return False

    @staticmethod
    def check_perm_option(data: PermOption) -> bool:
        if isinstance(data, dict):
            if 'option' in data:
                if data['option'] in [x[0] for x in PERMISSION_OPTION]:
                    return True
        return False

    def force_permission_by_configured(
            self,
            code_perm: str, action: Literal['update', 'override', 'drop'],
            data: PermOption = None,
            force_fetch: bool = False,
            force_save: bool = False,
    ) -> bool:
        if code_perm and self.check_perm_code(code_perm) and action and action in ['update', 'override', 'drop']:
            # active force fetch real-data from db
            if force_fetch is True:
                self.refresh_from_db()

            # handle data
            state = False
            match action:
                case 'update':
                    if self.check_perm_option(data):
                        data_configured = self.permission_by_configured.get(  # pylint: disable=E1101
                            code_perm, {}
                        )
                        data_configured.update(data)
                        self.permission_by_configured[code_perm] = data_configured  # pylint: disable=E1101,E1137
                        state = True
                case 'override':
                    if self.check_perm_option(data):
                        self.permission_by_configured[code_perm] = data  # pylint: disable=E1101,E1137
                        state = True
                case 'drop':
                    data_configured = self.permission_by_configured.pop(  # pylint: disable=E1101
                        code_perm, None
                    )
                    if data_configured is not None:
                        state = True

            # the end with active save with force hit db and return state
            if state is True:
                if force_save is True:
                    self.save_permissions(['permission_by_id'])
                return True
        return False

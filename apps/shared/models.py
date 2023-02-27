from copy import deepcopy
from typing import Union, Literal
from uuid import uuid4, UUID

from django.apps import apps
from django.db import models
from django.utils import timezone
from jsonfield import JSONField

from .utils import TypeCheck
from .managers import GlobalManager, PrivateManager, TeamManager, NormalManager, MasterDataManager
from .constant import DOCUMENT_MODE, SYSTEM_STATUS, PERMISSION_OPTION
from .formats import FORMATTING
from .permissions import PermOption
from .caches import CacheController


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

    def setup(self, app_label, model_name, *args, **kwargs):
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


class CacheByModel(object):
    def __init__(self):
        ...

    @staticmethod
    def get_model(app_model):
        return DisperseModel(app_model=app_model).get_model()

    @staticmethod
    def key(model_cls, doc_id):
        if hasattr(model_cls, 'key_cache') and TypeCheck.check_uuid(doc_id):
            return model_cls.key_cache(doc_id)
        return None

    @staticmethod
    def exist_cache(key):
        data = CacheController().get(key)
        return data if data else None

    @classmethod
    def get_cache(cls, app_model, doc_id) -> Union[None, dict]:
        if app_model and doc_id and TypeCheck.check_uuid(doc_id):
            model_cls = cls.get_model(app_model)
            key = cls.key(model_cls, doc_id)
            data = cls.exist_cache(key)
            if data:
                return data
            else:
                if hasattr(model_cls, 'get_cache'):
                    return model_cls.get_cache(doc_id)
        return None

    @classmethod
    def get_cache_obj(cls, doc_obj) -> Union[None, dict]:
        if doc_obj and hasattr(doc_obj, 'id'):
            model_cls = doc_obj.__class___
            key = cls.key(model_cls, doc_obj.id)
            data = cls.exist_cache(key)
            if data:
                return data
            else:
                if hasattr(model_cls, 'force_cache'):
                    return doc_obj.force_cache()
        return None

    @classmethod
    def reset_cache(cls, app_model, doc_id) -> Union[None, dict]:
        if app_model and doc_id and TypeCheck.check_uuid(doc_id):
            model_cls = cls.get_model(app_model)
            if hasattr(model_cls, 'force_cache'):
                try:
                    obj = model_cls.objects.get(pk=doc_id)
                    return obj.force_cache()
                except model_cls.DoesNotExist as err:
                    print(err)
        return None

    @classmethod
    def reset_cache_obj(cls, doc_obj) -> Union[None, dict]:
        if doc_obj and hasattr(doc_obj, 'id') and hasattr(doc_obj, 'force_cache'):
            return doc_obj.force_cache()
        return None

    @classmethod
    def destroy_cache(cls, app_model, doc_id) -> bool:
        if app_model and doc_id and TypeCheck.check_uuid(doc_id):
            model_cls = cls.get_model(app_model)
            if hasattr(model_cls, 'destroy_cache'):
                return model_cls.destroy_cache(doc_id)
        return False

    @classmethod
    def destroy_cache_obj(cls, doc_obj) -> bool:
        if doc_obj and hasattr(doc_obj, 'id') and hasattr(doc_obj, 'destroy_cache'):
            return doc_obj.destroy_cache(doc_obj.id)
        return False


class CacheCoreModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    @property
    def key_cache_prefix(self):
        raise NotImplementedError('This key_cache_prefix function must be override.')

    @classmethod
    def key_cache(cls, doc_id: Union[UUID, str]) -> str:
        return f'{cls.key_cache_prefix}__{str(doc_id)}'

    @property
    def data_cache(self) -> dict:
        """
        Return data save to cache
        """
        raise NotImplementedError('This data_cache function must be override.')

    def force_cache(self):
        """
        Force save key:data to cache
        """
        data = self.data_cache
        CacheController().set_never_expires(self.key_cache(self.id), data)
        return data

    @classmethod
    def get_cache(cls, doc_id, auto_cache: bool = True) -> Union[None, dict]:
        data = CacheController().get(cls.key_cache(doc_id))
        if not data and auto_cache is True:
            try:
                obj = cls.objects.get(pk=doc_id)
                data = obj.force_cache()
            except Exception as err:
                print(err)
                data = None
        return data

    @classmethod
    def destroy_cache(cls, doc_id) -> bool:
        return CacheController().destroy(cls.key_cache(doc_id))

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()


# abstract models
class BaseModel(models.Model):
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
        if self._state.adding is False:
            _original_fields_old = dict([(field, None) for field in field_name_list])
            if field_name_list and isinstance(field_name_list, list):
                try:
                    self_fetch = deepcopy(self)
                    self_fetch.refresh_from_db()
                    _original_fields_old = dict(
                        [(field, getattr(self_fetch, field)) for field in field_name_list]
                    )
                    return _original_fields_old
                except Exception as e:
                    print(e)
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

        result = super(TenantModel, self)._get_detail()
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

        result = super(TenantCoreModel, self)._get_detail()
        if 'tenant' not in excludes:
            result['tenant'] = self.tenant._get_detail()
        if 'company' not in excludes:
            result['company'] = self.company._get_detail()
        if 'mode' not in excludes:
            result['mode'] = self.mode
        if 'mode_id' not in excludes:
            result['mode_id'] = self.mode_id
        return result


class M2MModel(models.Model):
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

    def _get_detail(self, excludes=None):
        if not isinstance(excludes, list):
            excludes = []
        return {
            'id': self.id,
            'date_created': FORMATTING.parse_datetime(self.date_created),
            'extras': self.extras,
        }

    def get_detail(self, excludes=None):
        return self._get_detail(excludes=excludes)


class MasterDataModel(models.Model):
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


class PermissionCoreModel(models.Model):
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
    permission_keys = ['permission_by_id', 'permission_by_configured']

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

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

        super(PermissionCoreModel, self).save(update_fields=field_name, force_update=True)
        return True

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if isinstance(update_fields, list):
            for key in self.permission_keys:
                if key in update_fields:
                    update_fields.remove(key)
        super(PermissionCoreModel, self).save(force_insert, force_update, using, update_fields)

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
                        data_id = self.permission_by_id.get(code_perm, [])
                        data_id += data
                        self.permission_by_id[code_perm] = list(set(data_id))
                        state = True
                case 'remove':
                    if data and TypeCheck.check_uuid_list(data):
                        data_id = self.permission_by_id.get(code_perm, [])
                        if data_id and isinstance(data_id, list):
                            for idx_val in data:
                                if str(idx_val) in data_id:
                                    data_id.remove(str(idx_val))
                                    state = True
                            if state is True:
                                self.permission_by_id[code_perm] = list(set(data_id))
                case 'drop':
                    data_id = self.permission_by_id.pop(code_perm, None)
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
                        data_configured = self.permission_by_configured.get(code_perm, {})
                        data_configured.update(data)
                        self.permission_by_configured[code_perm] = data_configured
                        state = True
                case 'override':
                    if self.check_perm_option(data):
                        self.permission_by_configured[code_perm] = data
                        state = True
                case 'drop':
                    data_configured = self.permission_by_configured.pop(code_perm, None)
                    if data_configured is not None:
                        state = True

            # the end with active save with force hit db and return state
            if state is True:
                if force_save is True:
                    self.save_permissions(['permission_by_id'])
                return True
        return False


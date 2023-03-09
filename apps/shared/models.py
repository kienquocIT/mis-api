import json
from copy import deepcopy
from uuid import uuid4

from django.apps import apps
from django.db import models
from django.utils import timezone
from jsonfield import JSONField

from .utils import CustomizeEncoder
from .managers import NormalManager
from .constant import SYSTEM_STATUS
from .caches import CacheController

__all__ = [
    'SimpleAbstractModel', 'DataAbstractModel', 'MasterDataAbstractModel',
    'DisperseModel',
]


class SimpleAbstractModel(models.Model):
    """
    Bastion for all models in Prj and use to M2M
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    objects = NormalManager()

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

    FIELD_SELECT_RELATED = []  # field name list that you want select_related data.

    @classmethod
    def key_cache(cls):
        return str(f'{cls.__class__._meta.app_label}.{cls.__class__.__name__}_filter').lower()

    @classmethod
    def data_list_filter(cls, filter_kwargs: dict = None, get_first: bool = False):
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
        data = CacheController().get(key__child)
        if not data or (data and isinstance(data, dict) and key__child not in data):
            data__child = [
                x.parse_obj() for x in cls.objects.select_related(*cls.FIELD_SELECT_RELATED).filter(**filter_kwargs)
            ]
            data__child = json.loads(json.dumps(data__child, cls=CustomizeEncoder))
            if isinstance(data, dict):
                data[key__child] = data__child
            else:
                data = {key__child: data__child}
            CacheController().set(key=cls.key_cache(), value=data, expires=60 * 24 * 30)  # 30 days
        if get_first is True:
            return data[key__child][0] if len(data[key__child]) > 0 else {}
        return data[key__child]

    def get_old_value(self, field_name_list: list):
        """
        *** restrict the use this function ***
        ---
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if hasattr(self, 'parse_obj'):
            CacheController().destroy(self.key_cache())


class MasterDataAbstractModel(SimpleAbstractModel):
    """
    Abstract model for table data that had used by all user of company
    """
    # object_data = MasterDataManager()

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

    # base field
    title = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=100, blank=True)

    # document info
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
        'account.User', on_delete=models.SET_NULL, null=True,
        help_text='User modified this record in last',
        related_name='%(app_label)s_%(class)s_employee_modifier'
    )
    date_modified = models.DateTimeField(
        auto_now_add=True,
        help_text='Date modified this record in last',
    )

    # system flag
    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.SET_NULL,
        help_text='The tenant claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_tenant',
    )
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.SET_NULL,
        help_text='The company claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_company',
    )
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)


class DataAbstractModel(SimpleAbstractModel):
    """
    Abstract model for table data that have a lot flag for all case.
    """
    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

    # base field
    title = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=100, blank=True)

    # document info
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
        'account.User', on_delete=models.SET_NULL, null=True,
        help_text='User modified this record in last',
        related_name='%(app_label)s_%(class)s_employee_modifier'
    )
    date_modified = models.DateTimeField(
        auto_now_add=True,
        help_text='Date modified this record in last',
    )
    employee_inherit = models.ForeignKey(
        'hr.Employee', null=True, on_delete=models.SET_NULL,
        help_text='',
        related_name='%(app_label)s_%(class)s_employee_inherit',
    )

    # system flag
    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.SET_NULL,
        help_text='The tenant claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_tenant',
    )
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.SET_NULL,
        help_text='The company claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_company',
    )
    space = models.ForeignKey(
        'space.Space', null=True, on_delete=models.SET_NULL,
        help_text='The space claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_space',
    )
    process = models.ForeignKey(
        'process.Process', null=True, on_delete=models.SET_NULL,
        help_text='The process claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_process',
    )
    system_status = models.SmallIntegerField(
        choices=SYSTEM_STATUS,
        default=0
    )
    system_remarks = JSONField(default={})
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)


# Forwarder class model
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

    def get_model(self) -> SimpleAbstractModel:
        if self.setup_called:
            self.class_model = apps.get_model(
                app_label=self.app_label, model_name=self.model
            )
            return self.class_model
        raise Exception(
            f"[{str(self.__class__.__name__)}] "
            f"Execute setup() function before call get_model() function."
        )

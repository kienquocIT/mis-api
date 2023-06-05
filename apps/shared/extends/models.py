from copy import deepcopy
from uuid import uuid4

from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils import timezone
from jsonfield import JSONField

from .caching import Caching
from .managers import NormalManager
from ..constant import SYSTEM_STATUS

__all__ = [
    'SimpleAbstractModel', 'DataAbstractModel', 'MasterDataAbstractModel',
    'DisperseModel',
    'SignalRegisterMetaClass', 'CoreSignalRegisterMetaClass',
]


def post_save_handler(sender, **kwargs):
    table_name = sender._meta.db_table  # pylint: disable=protected-access / W0212
    update_fields = kwargs.get('update_fields', None)
    update_fields = list(update_fields) if update_fields else []
    if not (
            table_name == 'account_user' and
            update_fields and
            isinstance(update_fields, list) and
            len(update_fields) == 1 and
            'last_login' in update_fields
    ):
        # don't clean cache when update last_login
        Caching().clean_by_prefix(table_name=table_name)
        if settings.DEBUG_SIGNAL_CHANGE:
            print(f'Receive signal: {table_name}, ', kwargs)


class CoreSignalRegisterMetaClass(models.base.ModelBase, type):

    def register_signals(cls):
        models.signals.post_save.connect(
            post_save_handler, sender=cls
        )

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls.register_signals()  # pylint: disable=E1120


class SignalRegisterMetaClass(models.base.ModelBase, type):
    # def register_signals(cls):
    #     models.signals.post_save.connect(cls.post_save_handler, sender=cls)
    #     models.signals.post_delete.connect(cls.post_save_handler, sender=cls)
    #
    # def post_save_handler(cls, sender, **kwargs):
    #     table_name = sender._meta.db_table  # pylint: disable=protected-access / W0212
    #     update_fields = kwargs.get('update_fields', None)
    #     update_fields = list(update_fields) if update_fields else []
    #     if not (
    #             table_name == 'account_user' and
    #             update_fields and
    #             isinstance(update_fields, list) and
    #             len(update_fields) == 1 and
    #             'last_login' in update_fields
    #     ):
    #         # don't clean cache when update last_login
    #         Caching().clean_by_prefix(table_name=table_name)
    #         if getattr(settings, 'DEBUG_SIGNAL_CHANGE', False):
    #             print(f'Receive signal: {table_name}, ', kwargs)

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        # cls.register_signals()  # pylint: disable=E1120


class SimpleAbstractModel(models.Model, metaclass=SignalRegisterMetaClass):
    """
    Bastion for all models in Prj and use to M2M
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    objects = NormalManager()

    class Meta:
        abstract = True
        default_permissions = ()
        permissions = ()

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
        'hr.Employee', on_delete=models.SET_NULL, null=True,
        help_text='Employee modified this record in last',
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

    @classmethod
    def get_model_code(cls):
        app_label = cls._meta.app_label
        model_name = cls._meta.model_name
        return f"{app_label}.{model_name}".lower()

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
        'hr.Employee', on_delete=models.SET_NULL, null=True,
        help_text='Employee modified this record in last',
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
    workflow_runtime = models.ForeignKey(
        'workflow.Runtime',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Runtime Obj of Doc',
        help_text='Relate to Runtime Model is running flow of doc',
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

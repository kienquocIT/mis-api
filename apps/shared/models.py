from uuid import uuid4

from django.apps import apps
from django.db import models
from django.utils import timezone
from jsonfield import JSONField

from .managers import GlobalManager, PrivateManager, TeamManager, NormalManager
from .constant import DOCUMENT_MODE
from .formats import FORMATTING


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
            app_tmp, model_tmp = app_model.split("_")
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


class TenantModel(BaseModel):
    """
    Use for all app without core (don't use foreign key to tenant and company)
    Base + Tenant ID + Company ID
    """
    tenant_id = models.UUIDField(null=True)
    company_id = models.UUIDField(null=True)
    space_id = models.UUIDField(null=True)

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

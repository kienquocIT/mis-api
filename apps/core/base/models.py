from django.db import models
from jsonfield import JSONField

from apps.shared import SimpleAbstractModel

from apps.core.models import CoreAbstractModel


def clear_cache_base_group():
    # SubscriptionPlan.destroy_cache()
    # Application.destroy_cache()
    # PlanApplication.destroy_cache()
    # PermissionApplication.destroy_cache()
    return True


class SubscriptionPlan(CoreAbstractModel):
    class Meta:
        verbose_name = 'Subscription Plan'
        ordering = ('title',)
        default_permissions = ()
        permissions = ()

    def parse_obj(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'code': self.code,
            'application': [
                x.application.parse_obj()
                for x in PlanApplication.objects.select_related('application').filter(plan__id=self.id)
            ]
        }

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        clear_cache_base_group()


class Application(CoreAbstractModel):
    remarks = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Application'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def parse_obj(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'code': self.code,
            'remarks': self.remarks,
            'plan': [
                {
                    "id": str(x.plan.id),
                    "title": x.plan.title,
                    "code": x.plan.code,
                }
                for x in PlanApplication.objects.select_related('plan').filter(application__id=self.id)
            ]
        }

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        clear_cache_base_group()


class PlanApplication(SimpleAbstractModel):
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE
    )

    FIELD_SELECT_RELATED = ['plan', 'application', ]

    class Meta:
        verbose_name = 'Plan Application'
        verbose_name_plural = 'Plan Applications'
        default_permissions = ()
        permissions = ()


PROPERTIES_TYPE = (
    (1, 'Text'),
    (2, 'Date time'),
    (3, 'Choices'),
    (4, 'Checkbox'),
    (5, 'Master data'),
    (6, 'Number'),
)


class ApplicationProperty(CoreAbstractModel):
    application = models.ForeignKey(
        'base.Application',
        on_delete=models.CASCADE
    )
    remark = models.TextField(
        null=True,
        blank=True
    )
    code = models.TextField(
        null=True,
        blank=True
    )
    type = models.IntegerField(
        choices=PROPERTIES_TYPE,
        default=1
    )
    content_type = models.TextField(
        null=True,
        blank=True
    )
    properties = models.JSONField(
        default=dict,
    )
    compare_operator = models.JSONField(
        default=dict,
    )

    class Meta:
        verbose_name = 'Application property'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        clear_cache_base_group()


class PermissionApplication(SimpleAbstractModel):
    permission = models.CharField(max_length=100, unique=True)
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    extras = JSONField(default={})

    FIELD_SELECT_RELATED = ['app']

    def parse_obj(self):
        return {
            'id': str(self.id),
            'permission': self.permission,
            'app_id': str(self.app_id),
            'app': {
                'id': str(self.app_id),
                'title': self.app.title,
                'code': self.app.code,
                'remarks': self.app.remarks,
            } if self.app else {},
            'extras': self.extras
        }

    class Meta:
        verbose_name = 'Permission of Application'
        verbose_name_plural = 'Permission of Application'
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        clear_cache_base_group()

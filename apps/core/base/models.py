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
    applications = models.ManyToManyField(
        'Application',
        through='PlanApplication',
        symmetrical=False,
        blank=True,
        related_name='plan_map_application'
    )

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
    plans = models.ManyToManyField(
        'SubscriptionPlan',
        through='PlanApplication',
        symmetrical=False,
        blank=True,
        related_name='application_map_plan'
    )

    remarks = models.TextField(
        null=True,
        blank=True
    )

    app_label = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="application label ex. hr_employee"
    )

    is_workflow = models.BooleanField(
        default=True,
        verbose_name='Application apply Workflow',
    )

    class Meta:
        verbose_name = 'Application'
        ordering = ('title',)
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

    # use for Opp Stage
    opp_stage_operator = models.JSONField(
        default=list,
        help_text='comparison operator (≠ and =)'
    )
    stage_compare_data = models.JSONField(
        default=dict,
        help_text='compare data format {"=": [...], "≠": [...]}'
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


# Base Viet Nam info
class Country(SimpleAbstractModel):
    title = models.CharField(
        max_length=100,
        verbose_name='Name of Country'
    )
    code_2 = models.CharField(
        max_length=2,
        verbose_name='ISO Country Code: 2 letters'
    )
    code_3 = models.CharField(
        max_length=3,
        verbose_name='ISO Country Code: 3 letters'
    )
    language = models.CharField(
        blank=True,
        max_length=10,
        verbose_name='Official Language of Country'
    )

    class Meta:
        default_permissions = ()
        permissions = ()
        ordering = ('title',)
        unique_together = ('code_2', 'code_3',)
        verbose_name = 'Country'
        verbose_name_plural = 'Country'

    def save(self, *args, **kwargs):
        self.code_2 = self.code_2.upper()
        self.code_3 = self.code_3.upper()
        self.language = self.language.lower()
        return super().save(*args, **kwargs)


class City(SimpleAbstractModel):
    country = models.ForeignKey(
        'Country',
        on_delete=models.CASCADE,
        related_name='cities_of_country',
    )
    title = models.CharField(
        max_length=100,
        verbose_name='City of Country'
    )
    id_crawler = models.SmallIntegerField(
        verbose_name='ID of record in API Data'
    )
    zip_code = models.CharField(
        blank=True,
        verbose_name='Zip Code/Postal Code',
        max_length=15
    )

    class Meta:
        default_permissions = ()
        permissions = ()
        ordering = ('title',)
        unique_together = ('country', 'id_crawler')
        verbose_name = 'City'
        verbose_name_plural = 'City'


class District(SimpleAbstractModel):
    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        related_name='districts_of_city'
    )
    title = models.CharField(
        max_length=100,
        verbose_name='District of City'
    )
    id_crawler = models.SmallIntegerField(
        verbose_name='ID of record in API Data'
    )

    class Meta:
        default_permissions = ()
        permissions = ()
        ordering = ('title',)
        unique_together = ('city', 'id_crawler')
        verbose_name = 'District'
        verbose_name_plural = 'District'


class Ward(SimpleAbstractModel):
    district = models.ForeignKey(
        'District',
        on_delete=models.CASCADE,
        related_name='wards_of_district'
    )
    title = models.CharField(
        max_length=100,
        verbose_name='Ward of District'
    )
    id_crawler = models.SmallIntegerField(
        verbose_name='ID of record in API Data'
    )

    class Meta:
        default_permissions = ()
        permissions = ()
        ordering = ('title',)
        unique_together = ('district', 'id_crawler')
        verbose_name = 'Ward'
        verbose_name_plural = 'Ward'


# Currency
class Currency(SimpleAbstractModel):
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    symbol = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currency'
        ordering = ('code',)
        default_permissions = ()
        permissions = ()

    def before_save(self, **kwargs):
        self.code = self.code.upper()
        if not self.symbol and self.code:
            self.symbol = self.code
        return True

    def save(self, *args, **kwargs):
        self.before_save(**kwargs)
        super().save(*args, **kwargs)


class BaseItemUnit(SimpleAbstractModel):
    title = models.CharField(
        max_length=20,
    )
    measure = models.CharField(
        max_length=20,
    )

    class Meta:
        default_permissions = ()
        permissions = ()
        ordering = ('title',)
        verbose_name = 'BaseItemUnit'
        verbose_name_plural = 'BaseItemUnits'

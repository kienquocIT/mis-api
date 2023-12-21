import json

from django.db import models
from django.utils.text import slugify
from jsonfield import JSONField

from apps.shared import SimpleAbstractModel, INDICATOR_PARAM_TYPE, PERMISSION_OPTION_RANGE

from apps.core.models import CoreAbstractModel


def clear_cache_base_group():
    # SubscriptionPlan.destroy_cache()
    # Application.destroy_cache()
    # PlanApplication.destroy_cache()
    # PermissionApplication.destroy_cache()
    return True


def default_space_allow():
    return ['0']


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
    model_code = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text='Model code',
    )

    is_workflow = models.BooleanField(
        default=True,
        verbose_name='Application apply Workflow',
    )
    option_permission = models.PositiveSmallIntegerField(
        default=0,
        choices=PERMISSION_OPTION_RANGE,
        verbose_name='Allow Type Permission',
        help_text='0: Allow full control range, 1: Allow only company'
    )
    option_allowed = models.JSONField(
        default=list,
        verbose_name='Option code was allowed',
        # help_text='[1,2,3,4]'
    )
    app_depend_on = models.JSONField(
        default=list,
        help_text=json.dumps(
            [
                '{app_id}', '{app_id}', '{app_id}',
            ]
        ),
        verbose_name='App ID depend',
    )
    permit_mapping = models.JSONField(
        default=dict,
        verbose_name='Permit map Range and Depends On',
    )
    permit_mapping_sample = {
        # range:
        #   '*': match with all range the system supported
        #   or '1', '2', '3', '4', ... etc
        # app_depends_on:
        #   MAIN KEY:
        #       - '': match with any key in range
        #           - It's append, not override depends on config key
        #           - This config is force apply
        #       - '1'|'2'|'3'|...etc: [required range same this key ]
        #           - Active depends on app when range value match with key
        #   CHILD:
        #       MAIN KEY:
        #           - {app_id} : ID of depends on application
        #       CHILD:
        #           MAIN KEY:
        #               - {permit_code}: Code of permit allowed
        #           CHILD:
        #               - {code_range}: Range active when match case
        #                   - "==" : get range main fill into this.
        #                   - "1" | "2" | ...etc
        # local_depends_on:
        #   MAIN KEY: same level in "app_depends_on"
        #   CHILD:
        #       MAIN KEY:
        #           - {permit_code}: Code of permit allowed
        #       CHILD:
        #           - {code_range}: Range active when match case
        #               - "==" : get range main fill into this.
        #               - "1" | "2" | ...etc
        'view': {
            'range': ['*'],
            'app_depends_on': {
                '': {
                    '{app_id}': {
                        'view': 4,
                    },
                },
            },
            'local_depends_on': {},
        },
        'create': {
            'range': ['1'],
            'app_depends_on': {
                '': {
                    '{app_id}': {
                        'view': '4',
                    }
                },
                '1': {
                    '{app_id}': {
                        'view': '1',
                    }
                },
            },
            'local_depends_on': {
                '1': {
                    'view': '==',
                },
            },
        },
        'edit': {
            'range': ['1', '2', '3'],
            'app_depends_on': {},
            'local_depends_on': {
                '': {
                    'view': '=='
                },
            }
        },
        'delete': {
            'range': [],
            'app_depends_on': {},
            'local_depends_on': {},
        },
    }
    depend_follow_main = models.BooleanField(
        default=True,
        verbose_name='Depends Follow Main ID',
        help_text='Default it append to with Main ID Group, False: append to global (same general)'
    )
    filtering_inheritor = models.BooleanField(
        default=True,
        verbose_name='Allow Filter Inheritor',
        help_text='Apply rule filter employee_inherit_id in mask_view'
    )
    spacing_allow = models.JSONField(
        default=default_space_allow,
        verbose_name='Code Allow Space',
        help_text='0: General, 1: All space (not filter opp, prj,... isnull)',
    )

    def __repr__(self):
        return f'{self.app_label} - {self.model_code}'

    def __str__(self):
        return f'{self.app_label} - {self.model_code}'

    class Meta:
        verbose_name = 'Application'
        ordering = ('title',)
        default_permissions = ()
        permissions = ()
        unique_together = ('app_label', 'model_code')

    def get_prefix_permit(self):
        return f'{self.app_label}.{self.model_code}'.lower()

    @classmethod
    def get_range_allow(cls, opt):
        if opt == 0:
            return ["1", "2", "3", "4"]
        if opt == 1:
            return ["4"]
        return []

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
    is_sale_indicator = models.BooleanField(
        default=False,
        help_text="property which is only used for config sale indicators"
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
    short_search = models.CharField(blank=True, max_length=10)

    def resolve_short_search(self):
        if not self.short_search:
            short_txt = ''
            for item in slugify(self.title).split("-"):
                if item:
                    short_txt += item[0]
            if len(short_txt) > 10:
                short_txt = short_txt[:10]
            self.short_search = short_txt

    def save(self, *args, **kwargs):
        self.resolve_short_search()
        super().save(*args, **kwargs)

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


class IndicatorParam(SimpleAbstractModel):
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=100, unique=True)
    remark = models.CharField(
        max_length=200,
        blank=True
    )
    syntax = models.CharField(
        max_length=200,
        blank=True,
        help_text="syntax show in editor when user select this function"
    )
    syntax_show = models.CharField(
        max_length=200,
        blank=True,
        help_text="syntax show in description"
    )
    example = models.CharField(
        max_length=300,
        blank=True
    )
    param_type = models.SmallIntegerField(
        choices=INDICATOR_PARAM_TYPE,
        default=0
    )
    order = models.IntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Indicator Param'
        verbose_name_plural = 'Indicator Params'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()

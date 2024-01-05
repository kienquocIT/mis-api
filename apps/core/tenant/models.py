from copy import deepcopy

from django.contrib.auth import get_user_model
from django.db import models
from jsonfield import JSONField

from apps.core.models import CoreAbstractModel

TENANT_KIND = (
    (0, 'Cloud'),
    (1, 'Private'),
    (2, 'On-prem'),
)

# TenantPlan model choices
LICENSE_BUY_TYPE = (
    (0, "Auto Renew"),
    (1, "One Time"),
)


class Tenant(CoreAbstractModel):
    # override field from BASE MODEL
    code = models.CharField(max_length=10, unique=True)

    # category of tenant: Public, Private, On-prem
    kind = models.IntegerField(choices=TENANT_KIND, default=0)
    private_block = models.CharField(max_length=100, blank=True)

    # tenant detail
    sub_domain = models.CharField(max_length=20, unique=True)
    sub_domain_suffix = models.CharField(max_length=25, default='.quantrimis.com.vn')

    # representative
    representative_fullname = models.CharField(max_length=100)
    representative_phone_number = models.CharField(max_length=50)

    # plan info
    # {
    #       '{code_Plan}': {
    #           'license_limited': true,    # License: limit or unlimited
    #           'license_quantity': 100,     # quantity: null if unlimited, required if limit.
    #       }
    # }
    plan = JSONField(default={})

    # company of tenant
    auto_create_company = models.BooleanField(default=True)
    company_quality_max = models.IntegerField(default=5)

    # admin of tenant info
    admin_info = JSONField(
        default={
            'fullname': '',
            'phone_number': '',
            'username': '',
            'email': '',
        }
    )
    admin_created = models.BooleanField(default=False)
    admin = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True)

    user_request_created = JSONField(default={}, verbose_name='This is information of user request created.')

    company_total = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenant'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
        unique_together = ('code',)

    def parse_obj(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'code': self.code,
            'kind': self.kind,
            'private_block': self.private_block,
            'sub_domain': self.sub_domain,
            'sub_domain_suffix': self.sub_domain_suffix,
            'representative_fullname': self.sub_domain,
            'representative_phone_number': self.sub_domain,
            'plan': self.plan,
            'auto_create_company': self.auto_create_company,
            'company_quality_max': self.company_quality_max,
            'company_total': self.company_total,
        }

    def get_old_value(self, field_name_list: list):
        _original_fields_old = {field: None for field in field_name_list}
        if field_name_list and isinstance(field_name_list, list):
            try:
                self_fetch = deepcopy(self)
                self_fetch.refresh_from_db()
                _original_fields_old = {field: getattr(self_fetch, field) for field in field_name_list}
                return _original_fields_old
            except Exception as err:
                print(err)
        return _original_fields_old

    def save(self, *args, **kwargs):
        old_code = None
        if kwargs.get('force_update', False):
            # get old code and new code
            old_code = self.get_old_value(field_name_list=['code'])['code']
        self.code = self.code.lower()
        super().save(*args, **kwargs)

        # update username_auth for user when change tenant code
        if old_code is not None and old_code != self.code:
            for user in get_user_model().objects.filter(tenant_current_id=self.id):
                user.update_username_field_data()
                user.save()  # auto convert username auth when save user object.


class TenantPlan(CoreAbstractModel):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='tenant_plan_tenant',
        null=True
    )
    plan = models.ForeignKey(
        'base.SubscriptionPlan',
        on_delete=models.CASCADE,
        related_name='tenant_plan_plan',
        null=True
    )
    purchase_order = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    date_active = models.DateTimeField(null=True)
    date_end = models.DateTimeField(null=True)
    is_limited = models.BooleanField(null=True)
    license_quantity = models.IntegerField(null=True)
    license_used = models.IntegerField(null=True)
    is_expired = models.BooleanField(
        null=True,
        default=False
    )
    license_buy_type = models.SmallIntegerField(
        verbose_name="license buy type",
        choices=LICENSE_BUY_TYPE,
        help_text='Choose in (0, "Auto Renew"), (1, "One Time")',
        default=0,
    )

    def parse_obj(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'code': self.code,
            'tenant_id': str(self.tenant_id),
            'plan_id': str(self.plan_id),
            'purchase_order': self.purchase_order,
            'date_active': self.date_active,
            'date_end': self.date_end,
            'is_limited': self.date_end,
            'license_quantity': self.license_quantity,
            'license_used': self.license_used,
            'is_expired': self.is_expired,
            'license_buy_type': self.license_buy_type,
        }

    class Meta:
        verbose_name = 'Tenant Plan'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

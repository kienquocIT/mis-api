from copy import deepcopy

from django.contrib.auth import get_user_model
from django.db import models
from jsonfield import JSONField

from apps.shared import BaseModel, M2MModel

TENANT_KIND = (
    (0, 'Cloud'),
    (1, 'Private'),
    (2, 'On-prem'),
)


class Tenant(BaseModel):
    # override field from BASE MODEL
    code = models.CharField(max_length=10, unique=True)

    # category of tenant: Public, Private, On-prem
    kind = models.IntegerField(choices=TENANT_KIND, default=0)
    private_block = models.CharField(max_length=100, blank=True)

    # tenant detail
    sub_domain = models.CharField(max_length=10, unique=True)
    sub_domain_suffix = models.CharField(max_length=25, default='.quantrimis.com.vn')

    # representative
    representative_fullname = models.CharField(max_length=100)
    representative_phone_number = models.CharField(max_length=50)

    # company of tenant
    auto_create_company = models.BooleanField(default=True)
    company_quality_max = models.IntegerField(default=5)

    # admin of tenant info
    admin_info = JSONField(default={
        'fullname': '',
        'phone_number': '',
        'username': '',
        'email': '',
    })
    admin_created = models.BooleanField(default=False)
    admin = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True)

    user_request_created = JSONField(default={}, verbose_name='This is information of user request created.')

    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenant'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def get_old_value(self, field_name_list: list):
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

    def save(self, *args, **kwargs):
        # get old code and new code
        old_code = self.get_old_value(field_name_list=['code'])['code']

        super(Tenant, self).save(*args, **kwargs)

        # update username_auth for user when change tenant code
        if old_code != self.code:
            for user in get_user_model().objects.filter(tenant_current_id=self.id):
                user.update_username_field_data()
                user.save()  # auto convert username auth when save user object.


class Company(BaseModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    # license used
    # {
    #       '{code_Plan}': 99,
    # }
    license_usage = models.JSONField(default=dict)

    # User count | receive from client, increase or decrease
    user_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Company'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class Space(BaseModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    application = JSONField(default=[])
    is_system = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Space'
        verbose_name_plural = 'Space'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class CompanyLicenseTracking(M2MModel):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)

    # User
    user = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True)
    user_info = JSONField(default={})

    # code plan used
    license_plan = models.CharField(max_length=50)

    # sum license was used of company
    license_use_count = models.IntegerField()

    # some log, maybe it is user info just created
    log_msg = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Company License Tracking'
        verbose_name_plural = 'Company License Tracking'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

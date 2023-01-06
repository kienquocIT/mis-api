from django.db import models
from jsonfield import JSONField

from apps.shared import BaseModel, M2MModel


class Company(BaseModel):
    tenant = models.ForeignKey('tenant.Tenant', on_delete=models.CASCADE)

    # license used
    # {
    #       '{code_Plan}': 99,
    # }
    license_usage = models.JSONField(default=dict)

    # Total | receive from client, increase or decrease
    total_user = models.IntegerField(default=0)
    representative_fullname = models.CharField(
        verbose_name='fullname',
        max_length=100,
        blank=True,
    )
    address = models.CharField(
        verbose_name='address',
        blank=True,
        null=True,
        max_length=150
    )
    email = models.CharField(
        verbose_name='email',
        blank=True,
        null=True,
        max_length=150
    )
    phone = models.CharField(
        verbose_name='phone',
        blank=True,
        null=True,
        max_length=25
    )

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Company'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        super(Company, self).save(*args, **kwargs)
        # update total company of tenant
        if self.tenant:
            self.tenant.company_total = self.__class__.objects.filter(tenant=self.tenant).count()
            self.tenant.save()
        else:
            print(f'[Company|Save] Tenant does not exist {self.tenant}')


class CompanyLicenseTracking(M2MModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

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

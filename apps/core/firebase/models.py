from django.db import models
from apps.shared import SimpleAbstractModel


class DeviceToken(SimpleAbstractModel):
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

    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name="device_tokens")
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    device_info = models.JSONField(default=dict, help_text='Info of device use token')
    date_modified = models.DateTimeField(
        auto_now=True,
        help_text='Date modified this record in last',
    )

    def __str__(self):
        return f"{self.user.username} - {self.token}"

    class Meta:
        verbose_name = 'Device Token'
        verbose_name_plural = 'Device Token'
        ordering = ('-created_at',)
        default_permissions = ()
        permissions = ()

from django.contrib.auth.models import Permission
from django.db import models
from jsonfield import JSONField

from apps.shared import TenantCoreModel, M2MModel, GENDER_CHOICE


class Employee(TenantCoreModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    phone = models.CharField(max_length=25)

    is_delete = models.BooleanField(verbose_name='delete', default=False)
    search_content = models.CharField(verbose_name='Support Search Content', max_length=300, blank=True, null=True)
    avatar = models.TextField(null=True, verbose_name='avatar path')

    dob = models.DateField(verbose_name='birthday', null=True)
    gender = models.CharField(
        verbose_name='gender male or female',
        choices=GENDER_CHOICE, max_length=6, null=True,
    )

    user = models.ForeignKey('account.User', on_delete=models.CASCADE, null=True)

    space = models.ManyToManyField(
        'tenant.Space',
        through="SpaceEmployee",
        symmetrical=False,
        blank=True,
        related_name='employee_map_space'
    )

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employee'
        ordering = ('code',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        # setup full name for search engine
        self.full_name_search = f'{self.first_name} {self.last_name} , {self.last_name} {self.first_name} , {self.code}'
        super(Employee, self).save(*args, **kwargs)

    def get_detail(self, excludes=None):
        result = super(Employee, self)._get_detail(excludes=['tenant', 'company'])
        result['first_name'] = self.first_name
        result['last_name'] = self.last_name
        result['email'] = self.email
        result['phone'] = self.phone
        result['is_delete'] = self.is_delete
        result['avatar'] = self.avatar
        return result


class SpaceEmployee(M2MModel):
    space = models.ForeignKey('tenant.Space', on_delete=models.CASCADE)
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)
    application = JSONField(default=[])

    class Meta:
        verbose_name = 'Space of Employee'
        verbose_name_plural = 'Space of Employee'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

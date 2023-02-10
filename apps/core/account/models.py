from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.conf import settings
from django.db import models
from django.utils import timezone

from uuid import uuid4
from jsonfield import JSONField

from apps.core.account.manager import AccountManager
from apps.shared import AuthMsg, FORMATTING, DisperseModel


class AuthUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    username_validator = UnicodeUsernameValidator()
    username_auth = models.CharField(
        verbose_name='''Account Username for Authenticate, 
        format: "{username}-{TenantCode|upper}", slugify before call authenticate''',
        help_text=AuthMsg.USERNAME_REQUIRE, error_messages={'unique': AuthMsg.USERNAME_ALREADY_EXISTS},
        max_length=150 + 32, unique=True, validators=[username_validator],
    )
    username = models.CharField(verbose_name='Account Username', max_length=150)
    first_name = models.CharField(verbose_name='first name', max_length=80, blank=True)
    last_name = models.CharField(verbose_name='last name', max_length=150, blank=True)
    email = models.CharField(verbose_name='email address', max_length=150, blank=True, null=True)
    phone = models.CharField(verbose_name='phone number', max_length=50, blank=True, null=True)

    language = models.CharField(
        verbose_name='language favorite: vi, en',
        choices=settings.LANGUAGE_CHOICE, max_length=2, default='vi',
    )
    is_phone = models.BooleanField(verbose_name='phone is valid', default=False)
    is_email = models.BooleanField(verbose_name='email is valid', default=False)

    is_active = models.BooleanField(verbose_name='active', default=True)
    is_staff = models.BooleanField(verbose_name='staff status', default=False)
    is_superuser = models.BooleanField(default=False, verbose_name='superuser')

    user_created = models.UUIDField(verbose_name='User ID created record', null=True, default=None)
    date_created = models.DateTimeField(verbose_name='date created', default=timezone.now, editable=False)
    date_modified = models.DateTimeField(verbose_name='date modified', auto_now=True, editable=False)
    date_joined = models.DateTimeField(verbose_name='date joined, first login time', null=True, default=None)
    extras = JSONField(blank=True, null=True, default={})

    last_login = models.DateTimeField(verbose_name='Last Login', null=True)

    objects = AccountManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username_auth'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self, order_arrange=2):
        """
        order_arrange: The ways arrange full name from first_name and last_name
        ---
        First Name: Nguyen Van
        Last Name: A

        Two ways arrange full name:
        [1] {First Name}{Space}{Last Name} <=> Nguyen Van A
        [2] {Last Name}{Point}{Space}{First Name} <=> A. Nguyen Van
        [Another] Return default order_arrange
        """
        if self.last_name or self.first_name:
            if order_arrange == 1:
                return '{}, {}'.format(self.last_name, self.first_name)  # first ways
            return '{} {}'.format(self.last_name, self.first_name)  # second ways or another arrange
        return self.username

    class Meta:
        verbose_name = 'Account Abstract'
        verbose_name_plural = 'Account Abstract'
        abstract = True
        default_permissions = ()
        permissions = ()


class User(AuthUser):
    REQUIRED_FIELDS = ["phone", "email"]

    is_delete = models.BooleanField(verbose_name='delete', default=False)
    full_name_search = models.CharField(verbose_name='full name', max_length=200, blank=True, null=True)

    is_admin_tenant = models.BooleanField(default=False)
    tenant_current = models.ForeignKey(
        'tenant.Tenant', on_delete=models.CASCADE,
        related_name='tenant_current'
    )
    company_current = models.ForeignKey(
        'company.Company', on_delete=models.SET_NULL, null=True,
        related_name='company_current'
    )
    employee_current = models.ForeignKey(
        'hr.Employee', on_delete=models.SET_NULL, null=True,
        related_name='employee_current'
    )
    space_current = models.ForeignKey(
        'space.Space', on_delete=models.SET_NULL, null=True,
        related_name='space_current'
    )

    def update_username_field_data(self):
        setattr(self, self.USERNAME_FIELD, self.convert_username_field_data(self.username, self.tenant_current))
        return True

    @staticmethod
    def convert_username_field_data(username, tenant_obj):
        return f'{username}-{tenant_obj.code.upper()}'

    def sync_verify_contact(self):
        if settings.ENABLE_TURN_ON_IS_EMAIL:
            if (
                    self.email
                    and not self.is_email
                    and VerifyContact.objects.filter(email_or_phone=self.email).exists()
            ):
                self.is_email = True
            if (
                    self.phone
                    and not self.is_phone
                    and VerifyContact.objects.filter(email_or_phone=self.phone).exists()
            ):
                self.is_phone = True

    def sync_map(self, company_id):
        if company_id:
            company_employee_user_model = DisperseModel(app_model='company_CompanyUserEmployee').get_model()
            if company_employee_user_model:
                if hasattr(company_employee_user_model, 'create_new'):
                    company_employee_user_model.create_new(company_id, None, self.id)
                    return True
                raise NotImplementedError("Model company_CompanyUserEmployee sync is not found.")
            raise ReferenceError("Get models company_CompanyUserEmployee was returned not found.")
        raise AttributeError('[Account.User.sync_map] Company ID must be required.')

    def save(self,is_superuser=False, *args, **kwargs):
        # generate username for login
        self.username_auth = self.convert_username_field_data(self.username, self.tenant_current)

        # syn verify contact
        self.sync_verify_contact()

        # setup full name for search engine
        self.full_name_search = f'{self.first_name} {self.last_name} , {self.last_name} {self.first_name}'
        if is_superuser:
            self.is_superuser = True
        else:
            self.is_superuser = False
        super(User, self).save(*args, **kwargs)

        # update_total_user_for_company
        # self.company_current.total_user = self.__class__.objects.filter(company_current=self.company_current).count()
        # self.company_current.save()

    class Meta:
        verbose_name = 'Account User'
        verbose_name_plural = 'Account User'
        ordering = ("username",)
        default_permissions = ()
        permissions = ()

    def get_detail(self, is_full=True):
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username_auth': self.username_auth,
            'username': self.username,
            'email': self.email,
            'last_login': FORMATTING.parse_datetime(self.last_login),
            'is_admin_tenant': self.is_admin_tenant,
            'language': self.language,
        }
        if is_full:
            data.update({
                'tenant_current': self.tenant_current.get_detail() if self.tenant_current else {},
                'company_current': self.company_current.get_detail() if self.company_current else {},
                'space_current': self.space_current.get_detail() if self.space_current else {},
                'employee_current': self.employee_current.get_detail() if self.employee_current else {},
            })
        return data


class VerifyContact(models.Model):
    email_or_phone = models.CharField(max_length=150, primary_key=True, editable=False)
    is_email = models.BooleanField(default=False)
    is_phone = models.BooleanField(default=False)
    is_valid = models.BooleanField(verbose_name='Valid email or phone after login', default=True)
    counter = models.IntegerField(verbose_name='Counter user', default=0)
    date_valid = models.DateTimeField(default=timezone.now)
    extras = JSONField(blank=True, null=True, default={})

    class Meta:
        verbose_name = 'Verify Contact Account'
        verbose_name_plural = 'Verify Contact Account'
        ordering = ('-date_valid',)
        default_permissions = ()
        permissions = ()

    def __str__(self):
        return f'{self.email_or_phone} | is_email: {self.is_email} | is_phone: {self.is_phone}'

from uuid import UUID

from django.conf import settings
from django.db import models
from django.db.models import Count

from apps.core.attachments.storages.aws.storages_backend import PrivateMediaStorage
from apps.core.mailer.handle_html import HTMLController
from apps.shared import MasterDataAbstractModel, StringHandler, SimpleEncryptor

MAIL_TEMPLATE_SYSTEM_CODE = (
    (1, 'Welcome'),
    (2, 'Calendar'),
    (3, 'OTP Validation'),
)


def make_filename(filename, new_filename):
    if len(filename) > 0:
        arr_tmp = filename.split(".")
        f_ext = arr_tmp[-1]
        return f'{new_filename.lower()}.{f_ext.lower()}'
    raise ValueError('Attachment name is required')


def generate_path_config_file_ssl_key(instance, filename):
    if instance.company_id:
        company_path = str(instance.company_id).replace('-', '')
        return f"{company_path}/config/mail/{make_filename(filename, 'ssl_key')}"
    raise ValueError('Attachment require company related')


def generate_path_config_file_ssl_cert(instance, filename):
    if instance.company_id:
        company_path = str(instance.company_id).replace('-', '')
        return f"{company_path}/config/mail/{make_filename(filename, 'ssl_cert')}"
    raise ValueError('Attachment require company related')


class MailConfig(MasterDataAbstractModel):
    use_our_server = models.BooleanField(default=True, verbose_name='Use our mail server')
    host = models.TextField(blank=True, verbose_name='Mail server address')
    port = models.TextField(blank=True, verbose_name='Mail server port')
    username = models.TextField(blank=True, verbose_name='Mail server username')
    password = models.TextField(blank=True, verbose_name='Mail server password')
    use_tls = models.BooleanField(default=False, verbose_name='Mail server use TLS')
    use_ssl = models.BooleanField(default=False, verbose_name='Mail server use SSL')
    ssl_key = models.FileField(
        null=True, blank=True, storage=PrivateMediaStorage, upload_to=generate_path_config_file_ssl_key,
        verbose_name='SSL Key file'
    )
    ssl_cert = models.FileField(
        null=True, blank=True, storage=PrivateMediaStorage, upload_to=generate_path_config_file_ssl_cert,
        verbose_name='SSL Cert file'
    )
    data = models.JSONField(default=dict, verbose_name='Data response')

    def get_real_data(self):
        key_force = SimpleEncryptor.generate_key(password=settings.EMAIL_CONFIG_ENCRYPTOR_PASSWORD)
        cls = SimpleEncryptor(key=key_force)
        return {
            'host': cls.decrypt(self.host),
            'port': cls.decrypt(self.port),
            'username': cls.decrypt(self.username),
            'password': cls.decrypt(self.password),
        }

    def encrypt_and_collect(self, host, port, username, password):
        key_force = SimpleEncryptor.generate_key(password=settings.EMAIL_CONFIG_ENCRYPTOR_PASSWORD)

        if host is not None:
            self.host = SimpleEncryptor(key=key_force).encrypt(data=host, to_string=True)
            self.data['host'] = StringHandler.mask(host, percent_mask=50)

        if port is not None:
            self.port = SimpleEncryptor(key=key_force).encrypt(data=port, to_string=True)
            self.data['port'] = StringHandler.mask(port, percent_mask=30)

        if username is not None:
            self.username = SimpleEncryptor(key=key_force).encrypt(data=username, to_string=True)
            self.data['username'] = StringHandler.mask(username, percent_mask=70)

        if password is not None:
            self.password = SimpleEncryptor(key=key_force).encrypt(data=password, to_string=True)
            self.data['password'] = StringHandler.mask(password, percent_mask=100)

        if self.ssl_key:
            ssl_key_name = self.ssl_key.name.split('/')[-1]
            ssl_key_arr = ssl_key_name.split('.')
            if len(ssl_key_arr) > 1:
                f_name_mask = StringHandler.mask("".join(ssl_key_arr[:-1]), percent_mask=50)
                self.data['ssl_key'] = f'{f_name_mask}.{ssl_key_arr[-1]}'
            else:
                self.data['ssl_key'] = StringHandler.mask(ssl_key_name, percent_mask=50)
        else:
            self.data['ssl_key'] = None

        if self.ssl_cert:
            ssl_cert_name = self.ssl_cert.name.split('/')[-1]
            ssl_cert_arr = ssl_cert_name.split('.')
            if len(ssl_cert_arr) > 1:
                f_name_mask = StringHandler.mask("".join(ssl_cert_arr[:-1]), percent_mask=50)
                self.data['ssl_cert'] = f'{f_name_mask}.{ssl_cert_arr[-1]}'
            else:
                self.data['ssl_cert'] = StringHandler.mask(ssl_cert_name, percent_mask=50)
        else:
            self.data['ssl_key'] = None

        return self

    class Meta:
        verbose_name = 'Mail Config'
        verbose_name_plural = 'Mail Config'
        default_permissions = ()
        permissions = ()
        unique_together = ('tenant', 'company')


class MailTemplateSystem(MasterDataAbstractModel):
    subject = models.CharField(max_length=100, blank=True, verbose_name='Subject for Send Email')
    system_code = models.CharField(max_length=2, help_text='MAIL_TEMPLATE_SYSTEM_CODE')
    contents = models.TextField(blank=True)

    @classmethod
    def template_get_or_create(cls, tenant_id, company_id, system_code):
        obj, _created = MailTemplateSystem.objects.get_or_create(
            tenant_id=tenant_id, company_id=company_id, system_code=system_code,
            defaults={
                'is_active': False,
                'contents': '',
            }
        )
        return obj

    def save(self, *args, **kwargs):
        self.contents = HTMLController(html_str=self.contents).clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Mail Template System'
        verbose_name_plural = 'Mail Template System'
        default_permissions = ()
        permissions = ()
        ordering = ('title',)
        unique_together = ('tenant_id', 'company_id', 'system_code')


class MailTemplate(MasterDataAbstractModel):
    application = models.ForeignKey('base.Application', on_delete=models.CASCADE)
    contents = models.TextField()
    is_default = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)

    @classmethod
    def check_using_unique(cls, tenant_id: UUID, company_id: UUID) -> (bool, list[str]):
        app_not_unique = []
        kw_arg = {'tenant_id': tenant_id, 'company_id': company_id, 'is_default': True}
        for data in MailTemplate.objects.filter(**kw_arg).values('application').annotate(total=Count('id')):
            if data['total'] > 1:
                app_not_unique.append(data['application'])

        if app_not_unique:
            return False, app_not_unique
        return True, []

    def confirm_unique_using(self):
        obj_running_using = MailTemplate.objects.filter(
            tenant=self.tenant, company=self.company, application=self.application, is_default=True
        ).exclude(id=self.id)
        for obj in obj_running_using:
            obj.is_default = False
            obj.save(update_fields=['is_default'])
        return True

    def save(self, *args, **kwargs):
        if self.is_default is True:
            self.is_active = True
            self.confirm_unique_using()
        self.contents = HTMLController(html_str=self.contents).clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Mail Template'
        verbose_name_plural = 'Mail Template'
        default_permissions = ()
        permissions = ()
        ordering = ('title',)

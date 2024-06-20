from uuid import UUID

from django.conf import settings
from django.db import models
from django.db.models import Count
from django.utils import timezone

from apps.core.attachments.storages.aws.storages_backend import PrivateMediaStorage
from apps.core.mailer.handle_html import HTMLController
from apps.core.mailer.templates import (
    TEMPLATE_OTP_VALIDATE_DEFAULT, TEMPLATE_MAIL_WELCOME_DEFAULT,
    TEMPLATE_CALENDAR_DEFAULT, SUBJECT_MAIL_WELCOME_DEFAULT, SUBJECT_OTP_VALIDATE_DEFAULT, SUBJECT_CALENDAR_DEFAULT,
)
from apps.shared import MasterDataAbstractModel, StringHandler, SimpleEncryptor, SimpleAbstractModel, DisperseModel

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


class MailConfig(MasterDataAbstractModel):  # pylint: disable=R0902
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
    from_email = models.TextField(blank=True, verbose_name='From Email sent')
    reply_email = models.TextField(blank=True, verbose_name='Reply To sent')
    cc_email = models.JSONField(default=list, verbose_name='Email CC sent')
    bcc_email = models.JSONField(default=list, verbose_name='Email BCC sent')
    data = models.JSONField(default=dict, verbose_name='Data response')

    @classmethod
    def get_config(cls, tenant_id, company_id):
        obj, _created = cls.objects.get_or_create(tenant_id=tenant_id, company_id=company_id)
        return obj

    def get_ssl_key(self):
        return self.ssl_key.path if self.use_ssl and self.ssl_key else None

    def get_ssl_cert(self):
        return self.ssl_cert.path if self.use_ssl and self.ssl_cert else None

    def get_real_data(self):
        key_force = SimpleEncryptor.generate_key(password=settings.EMAIL_CONFIG_ENCRYPTOR_PASSWORD)
        cls = SimpleEncryptor(key=key_force)
        return {
            'host': cls.decrypt(self.host) if self.host else None,
            'port': cls.decrypt(self.port) if self.port else None,
            'username': cls.decrypt(self.username) if self.username else None,
            'password': cls.decrypt(self.password) if self.password else None,
            'from_email': cls.decrypt(self.from_email) if self.from_email else None,
            'reply_email': cls.decrypt(self.reply_email) if self.reply_email else None,
            'cc_email': [cls.decrypt(item) for item in self.cc_email] if isinstance(self.cc_email, list) else [],
            'bcc_email': [cls.decrypt(item) for item in self.bcc_email] if isinstance(self.bcc_email, list) else [],
        }

    def encrypt_and_collect(  # pylint: disable=R0912,R0914,R0915
            self, host, port, username, password,
            from_email, reply_email, cc_email, bcc_email,
            ssl_key_file, ssl_cert_file
    ):
        key_force = SimpleEncryptor.generate_key(password=settings.EMAIL_CONFIG_ENCRYPTOR_PASSWORD)
        cls_encrypt = SimpleEncryptor(key=key_force)

        if host is not None:
            self.host = cls_encrypt.encrypt(data=host, to_string=True)
            self.data['host'] = StringHandler.mask(host, percent_mask=50)

        if port is not None:
            self.port = cls_encrypt.encrypt(data=port, to_string=True)
            self.data['port'] = StringHandler.mask(port, percent_mask=30)

        if username is not None:
            self.username = cls_encrypt.encrypt(data=username, to_string=True)
            self.data['username'] = StringHandler.mask(username, percent_mask=70)

        if password is not None:
            self.password = cls_encrypt.encrypt(data=password, to_string=True)
            self.data['password'] = StringHandler.mask(password, percent_mask=100)

        if from_email is not None:
            self.from_email = cls_encrypt.encrypt(data=from_email, to_string=True)
            self.data['from_email'] = StringHandler.mask(from_email, percent_mask=70)

        if reply_email is not None:
            self.reply_email = cls_encrypt.encrypt(data=reply_email, to_string=True)
            self.data['reply_email'] = StringHandler.mask(reply_email, percent_mask=70)

        if cc_email is not None and isinstance(cc_email, list):
            cc_enc, cc_mask = [], []
            for item in cc_email:
                cc_enc.append(cls_encrypt.encrypt(data=item, to_string=True))
                cc_mask.append(StringHandler.mask(item, percent_mask=70))
            self.cc_email = cc_enc
            self.data['cc_mail'] = cc_mask

        if bcc_email is not None and isinstance(bcc_email, list):
            bcc_enc, bcc_mask = [], []
            for item in bcc_email:
                bcc_enc.append(cls_encrypt.encrypt(data=item, to_string=True))
                bcc_mask.append(StringHandler.mask(item, percent_mask=70))
            self.bcc_email = bcc_enc
            self.data['bcc_email'] = bcc_mask

        if ssl_key_file is True:
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
        if ssl_cert_file is True:
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
    def get_config(cls, tenant_id, company_id, system_code):
        obj, created = cls.objects.get_or_create(tenant_id=tenant_id, company_id=company_id, system_code=system_code)
        if created is True:
            tenant_cls = DisperseModel(app_model='tenant.Tenant').get_model()
            company_cls = DisperseModel(app_model='company.Company').get_model()
            try:
                tenant_obj = tenant_cls.objects.get(pk=tenant_id)
                company_obj = company_cls.objects.get(pk=company_id)
                if system_code in [1, '1']:
                    obj.subject = SUBJECT_MAIL_WELCOME_DEFAULT
                    obj.contents = TEMPLATE_MAIL_WELCOME_DEFAULT.replace(
                        '__company_title__', company_obj.title
                    ).replace('__company_sub_domain__', tenant_obj.code.lower())
                elif system_code in [2, '2']:
                    obj.subject = SUBJECT_CALENDAR_DEFAULT
                    obj.contents = TEMPLATE_CALENDAR_DEFAULT.replace('__company_title__', company_obj.title)
                elif system_code in [3, '3']:
                    obj.subject = SUBJECT_OTP_VALIDATE_DEFAULT
                    obj.contents = TEMPLATE_OTP_VALIDATE_DEFAULT.replace('__company_title__', company_obj.title)
                obj.save(update_fields=['contents', 'subject'])
            except tenant_cls.DoesNotExist:
                pass
            except company_cls.DoesNotExist:
                pass
        return obj

    def save(self, *args, **kwargs):
        if not HTMLController.detect_escape(self.contents):
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
        if not HTMLController.detect_escape(self.contents):
            self.contents = HTMLController(html_str=self.contents).clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Mail Template'
        verbose_name_plural = 'Mail Template'
        default_permissions = ()
        permissions = ()
        ordering = ('title',)


MAIL_LOG_STATUS_CODE = (
    (0, 'InProgress'),
    (1, 'Sent'),
    (2, 'Error'),
)


class MailLog(SimpleAbstractModel):
    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_belong_to_tenant',
    )
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_belong_to_company'
    )
    is_delete = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    date_modified = models.DateTimeField(auto_now_add=True)

    # relate data
    application = models.ForeignKey('base.Application', on_delete=models.CASCADE, null=True)
    system_code = models.CharField(max_length=2, help_text='MAIL_TEMPLATE_SYSTEM_CODE')
    doc_id = models.UUIDField(null=True, verbose_name='Document ID related')

    # mail data
    subject = models.TextField(blank=True, verbose_name='Subject of mail')
    address_sender = models.TextField(blank=True, verbose_name='Sender Mail')
    address_to = models.JSONField(default=list, verbose_name='Receiver Mail')
    employee_to = models.ManyToManyField(
        'hr.Employee',
        through='MailLogEmployeeTo',
        symmetrical=False,
        blank=True,
        related_name='to_of_mail',
    )
    address_cc = models.JSONField(default=list, verbose_name='CC Mail')
    employee_cc = models.ManyToManyField(
        'hr.Employee',
        through='MailLogEmployeeCC',
        symmetrical=False,
        blank=True,
        related_name='cc_of_mail'
    )
    address_bcc = models.JSONField(default=list, verbose_name='BCC Mail')
    employee_bcc = models.ManyToManyField(
        'hr.Employee',
        through='MailLogEmployeeBCC',
        symmetrical=False,
        blank=True,
        related_name='bcc_of_mail',
    )
    status_code = models.SmallIntegerField(default=0, verbose_name='Status code for filter: MAIL_LOG_STATUS_CODE')
    status_remark = models.TextField(blank=True, verbose_name='Status mail')
    errors_data = models.TextField(blank=True)

    # linked
    reply_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='reply_from_mail_log')
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='reply_to_mail_log')

    class Meta:
        verbose_name = 'Mail Log'
        verbose_name_plural = 'Mail Log'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class MailLogData(SimpleAbstractModel):
    log = models.OneToOneField(MailLog, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    date_modified = models.DateTimeField(auto_now_add=True)

    host = models.TextField(blank=True, verbose_name='Host - encrypted')
    port = models.TextField(blank=True, verbose_name='Port - encrypted')
    username = models.TextField(blank=True, verbose_name='Username - encrypted')
    password = models.TextField(blank=True, verbose_name='Password - encrypted')
    use_tls = models.BooleanField(default=False, verbose_name='Use TLS')
    use_ssl = models.BooleanField(default=False, verbose_name='Use SSL')
    ssl_key_path = models.TextField(blank=True, verbose_name='Path to SSL Key file')
    ssl_cert_path = models.TextField(blank=True, verbose_name='Path to SSL Cert file')

    ident_mail = models.TextField(blank=True, verbose_name='Ident Mail - ID')
    headers = models.JSONField(default=dict, verbose_name='Header Mail')
    body_text = models.TextField(blank=True, verbose_name='Body Mail Text Plain')
    body_html = models.TextField(blank=True, verbose_name='Body Mail HTML')
    reply_to = models.TextField(blank=True, verbose_name='Address Mail Reply')
    doc_data = models.JSONField(default=dict, verbose_name='Document Data')

    class Meta:
        verbose_name = 'Mail Log Data'
        verbose_name_plural = 'Mail Log Data'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class MailLogEmployeeTo(SimpleAbstractModel):
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE)
    mail_log = models.ForeignKey(MailLog, on_delete=models.CASCADE)
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Mail Log Receiver'
        verbose_name_plural = 'Mail Log Receiver'
        unique_together = ('mail_log', 'employee')
        default_permissions = ()
        permissions = ()


class MailLogEmployeeCC(SimpleAbstractModel):
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE)
    mail_log = models.ForeignKey(MailLog, on_delete=models.CASCADE)
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Mail Log CC'
        verbose_name_plural = 'Mail Log CC'
        unique_together = ('mail_log', 'employee')
        default_permissions = ()
        permissions = ()


class MailLogEmployeeBCC(SimpleAbstractModel):
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE)
    mail_log = models.ForeignKey(MailLog, on_delete=models.CASCADE)
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Mail Log BCC'
        verbose_name_plural = 'Mail Log BCC'
        unique_together = ('mail_log', 'employee')
        default_permissions = ()
        permissions = ()

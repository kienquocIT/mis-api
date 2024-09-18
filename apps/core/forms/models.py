import random
import string
from datetime import timedelta
from uuid import uuid4

from django.db import models
from django.utils import timezone

from apps.core.mailer.handle_html import HTMLController
from apps.shared import MasterDataAbstractModel, StringHandler
from apps.shared.html_constant import FORM_SANITIZE_TRUSTED_DOMAIN_LINK

LABEL_PLACEMENT_CHOICES = (
    ('top', 'TOP'),
    ('left', 'LEFT'),
    ('right', 'RIGHT'),
)

INSTRUCTION_PLACEMENT_CHOICES = (
    ('top', 'TOP'),
    ('bottom', 'BOTTOM'),
)


def generate_path_public_file(instance, filename):
    if instance.company_id:
        company_path = str(instance.company_id).replace('-', '')
        file_name = str(filename).replace('-', '')
        return f"{company_path}/global/form/{file_name}"
    raise ValueError('Attachment require company related')


class Form(MasterDataAbstractModel):
    AUTHENTICATED_TYPE = (
        ('system', "Company's member"),
        ('email', "Email"),
    )

    title = models.CharField(max_length=100)
    remark = models.TextField(blank=True, verbose_name='Remark of form, showing after form name')
    label_placement = models.CharField(max_length=10, choices=LABEL_PLACEMENT_CHOICES)
    instruction_placement = models.CharField(max_length=10, choices=INSTRUCTION_PLACEMENT_CHOICES)
    authentication_required = models.BooleanField(default=False)
    authentication_type = models.CharField(max_length=10, choices=AUTHENTICATED_TYPE, default='system')
    submit_only_one = models.BooleanField(default=False)
    edit_submitted = models.BooleanField(default=False)
    entries_default_show = models.JSONField(
        default=dict, help_text='The default display of Referrer Name in entries'
    )

    configs_order = models.JSONField(default=list, verbose_name='Order of idx config', help_text='[idx1, idx2]')
    configs = models.JSONField(
        default=dict, verbose_name='Config row with type (dict in list)',
        help_text='[{"type": "form-title", ...}, {...},]'
    )
    theme_selected = models.CharField(max_length=50, null=True, blank=True, help_text='Code theme apply for form')
    theme_assets = models.JSONField(
        default=dict, verbose_name='Asset include of theme', help_text='{"js": [], "css": []}'
    )

    page = models.JSONField(default=dict, verbose_name='Config of page')

    def get_input_names(self) -> list[str]:
        result = []
        if self.configs and isinstance(self.configs, dict):  # pylint: disable=R1702
            for _key, value in self.configs.items():
                if value and isinstance(value, dict) and 'inputs_data' in value:
                    inputs_data = value['inputs_data']
                    if inputs_data and isinstance(inputs_data, list):
                        for item in inputs_data:
                            if item and isinstance(item, dict) and 'name' in item:
                                name = item['name']
                                if name:
                                    result.append(name)
        return result

    def get_or_create_publish(self, **kwargs):
        base_kwargs = {
            'tenant': self.tenant,
            'company': self.company,
            'form_id': self.id,
        }
        extend_kwargs = {
            'is_active': True,
            'is_public': False,
            'is_iframe': False,
            **kwargs
        }
        obj, _created = FormPublished.objects.get_or_create(**base_kwargs, defaults=extend_kwargs)
        return obj, _created

    def save(self, *args, **kwargs):
        if self.is_delete is True:
            try:
                published = FormPublished.objects.get(form=self)
                published.is_active = False
                published.is_public = False
                published.is_iframe = False
                published.is_delete = True
                published.save(update_fields=['is_active', 'is_delete', 'is_public', 'is_iframe'])
            except FormPublished.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    class Meta:
        # support config
        verbose_name = 'Form'
        verbose_name_plural = 'Form'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


def notifications_default():
    return {
        "user_management_enable_new": False,
        "user_management_enable_change": False,
        "user_management_destination": [],
        "creator_enable_new": False,
        "creator_enable_change": False,
        "creator_receiver_from": "authenticated",
        "creator_field": ""
    }


class FormPublished(MasterDataAbstractModel):
    form = models.OneToOneField(Form, on_delete=models.CASCADE, related_name='form_published')
    date_publish_start = models.DateField(default=timezone.now, editable=True, help_text='Set activation date and time')
    date_publish_finish = models.DateField(null=True, help_text='Set deactivation date and time')
    is_active = models.BooleanField(
        default=True,
        help_text='With active, start and finish will be apply. With deactivate, the access was deny.'
        # Celery beat task auto check date_publish_finish force update is_active while 5 minutes
        # Task: apps.core.forms.task.check_and_update_active_publish_form
    )
    html_text = models.TextField(blank=True, help_text='This is HTML text that config was generated')
    code = models.CharField(max_length=32, unique=True)
    is_public = models.BooleanField(default=False)
    is_iframe = models.BooleanField(default=False)
    notifications = models.JSONField(default=notifications_default)

    def force_save_html_file(self):
        # content = ContentFile(self.html_text.encode())
        # filename = f"{self.id.hex}.html"
        # self.html_file.save(filename, content, save=False)
        pass

    def update_same_obj(self, real_obj):
        self.date_publish_start = real_obj.date_publish_start
        self.date_publish_finish = real_obj.date_publish_finish
        self.is_active = real_obj.is_active
        self.html_text = real_obj.html_text
        self.is_public = real_obj.is_public
        self.is_iframe = real_obj.is_iframe

    @staticmethod
    def generate_code():
        return StringHandler.random_str(32, upper_lower=1)

    def save(self, *args, **kwargs):
        # check and update notifications
        default_notify = notifications_default()
        notifications = {
            **default_notify,
            **self.notifications,
        }
        for key, value in notifications.items():
            if key in default_notify:
                self.notifications[key] = value

        #
        if not self.code:
            self.code = self.generate_code()
        if not HTMLController.detect_escape(self.html_text):
            self.html_text = HTMLController(html_str=self.html_text).clean(
                trusted_domain=FORM_SANITIZE_TRUSTED_DOMAIN_LINK,
                allowed_input_names=self.form.get_input_names(),
            )
        super().save(*args, **kwargs)

    class Meta:
        # support form config call publish + runtime after publish
        verbose_name = 'Published Forms'
        verbose_name_plural = 'Published Forms'
        ordering = ('-is_active', '-date_publish_finish')
        default_permissions = ()
        permissions = ()


class FormPublishedEntries(MasterDataAbstractModel):
    # override base and advance base
    employee_created = models.ForeignKey(
        'hr.Employee', null=True, on_delete=models.SET_NULL,
        help_text='Employee created this record',
        related_name='%(app_label)s_%(class)s_employee_creator',
    )
    user_created = models.ForeignKey(
        'account.User', null=True, on_delete=models.SET_NULL,
        help_text='User created this record',
        related_name='%(app_label)s_%(class)s_user_creator',
    )
    creator_email = models.CharField(max_length=255, null=True, verbose_name='Email of entry creator')

    # main field
    published = models.ForeignKey(FormPublished, on_delete=models.CASCADE, verbose_name='Record belong to Published')
    body_data = models.JSONField(default=dict, verbose_name='Data submit', help_text='Data of client was submit')
    ref_name = models.TextField(
        blank=True, null=True,
        verbose_name='Reference Name', help_text='Track referrals in parameter'
    )
    meta_data = models.JSONField(
        default=dict, verbose_name='Request Headers',
        help_text='Collect same data of request: PATH, PATH_INFO, METHOD, ENCODING, CONTENT_TYPE, CONTENT_PARAMS',
    )

    #
    unique_data = models.JSONField(
        default=dict, verbose_name='Unique Data',
        help_text='Key-value of unique field',
    )

    class Meta:
        verbose_name = 'Form Published Entries'
        verbose_name_plural = 'Form Published Entries'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class FormPublishAuthenticateEmail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.CharField(max_length=255)
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    date_modified = models.DateTimeField(auto_now=True)

    otp = models.CharField(max_length=10)
    otp_expires_seconds = models.SmallIntegerField(default=0)
    otp_expires = models.DateTimeField(null=True)

    is_valid = models.BooleanField(default=False)
    expires = models.DateTimeField(null=True)

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
    form = models.ForeignKey(
        FormPublished, null=True, on_delete=models.CASCADE,
        help_text='The form claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_form',
    )

    @classmethod
    def generate_otp(cls, length=8):
        return "".join(random.choices(string.digits, k=length))

    @classmethod
    def generate_otp_data(cls, expires_kwargs=None) -> dict:
        if not expires_kwargs:
            expires_kwargs = {
                'minutes': 2,
            }
        data_time = timedelta(**expires_kwargs)
        return {
            'otp': cls.generate_otp(length=6),
            'otp_expires': timezone.now() + data_time,
            'otp_expires_seconds': data_time.seconds,
        }

    def activate_valid(self, expire_append='1d', commit=False):
        self.is_valid = True
        num_time = int(expire_append[:-1])
        unit = expire_append[-1]
        now = timezone.now()

        if unit == 's':
            self.expires = now + timedelta(seconds=num_time)
        if unit == 'm':
            self.expires = now + timedelta(minutes=num_time)
        elif unit == 'h':
            self.expires = now + timedelta(hours=num_time)
        elif unit == 'd':
            self.expires = now + timedelta(days=num_time)
        elif unit == 'w':
            self.expires = now + timedelta(weeks=num_time)
        if commit is True:
            self.save()
        return self

    @classmethod
    def destroy_expired(cls):
        obj_expired = cls.objects.filter(expires__lt=timezone.now())
        if obj_expired:
            obj_expired.delete()

    def is_expired(self) -> bool:
        if timezone.now() > self.expires:
            return True
        return False

    class Meta:
        verbose_name = 'Form Authentication Email - Guess'
        verbose_name_plural = 'Form Authentication Email - Guess'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

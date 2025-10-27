import json
from django.db import models

from apps.core.models import TenantAbstractModel
from apps.shared import LIST_BANK

GENDER_TYPE = (
    (0, 'Man'),
    (1, 'Woman'),
    (2, 'Other'),
)
MARITAL_STT = (
    (0, 'Married'),
    (1, 'Widowed'),
    (2, 'Separated'),
    (3, 'Divorced'),
    (4, 'Single'),
    (5, 'Engaged'),
)


class EmployeeInfo(TenantAbstractModel):
    employee = models.OneToOneField(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name="employee_info",
        null=True,
        blank=True
    )
    citizen_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name='citizen identification',
    )
    date_of_issue = models.DateField(
        null=True,
        blank=True,
        verbose_name='Date of issue'
    )
    place_of_issue = models.CharField(
        verbose_name='place of issue',
        blank=True,
        max_length=150,
        null=True,
        help_text="The place of issue refers to the city where the passport processing took place",
    )
    place_of_birth = models.ForeignKey(
        'base.City',
        on_delete=models.SET_NULL,
        verbose_name="Place of birth",
        null=True,
        blank=True,
        related_name='pob_employee_info'
    )
    nationality = models.ForeignKey(
        'base.Country',
        on_delete=models.SET_NULL,
        verbose_name="Nationality",
        null=True,
        blank=True,
        related_name='nationality_employee_info_set'
    )
    place_of_origin = models.ForeignKey(
        'base.City',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ethnicity = models.CharField(
        blank=True, max_length=50, null=True, help_text='a group of people who identify with each other'
    )
    religion = models.CharField(
        blank=True, max_length=50, null=True, help_text='the belief in the existence of a god or gods'
    )
    gender = models.IntegerField(
        choices=GENDER_TYPE,
        null=True,
        blank=True
    )
    marital_status = models.IntegerField(
        choices=MARITAL_STT,
        null=True,
        blank=True
    )
    bank_acc_no = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name='Bank account number',
    )
    acc_name = models.CharField(
        blank=True, max_length=50, null=True, help_text='account name'
    )
    bank_name = models.IntegerField(
        choices=LIST_BANK,
        null=True,
        blank=True
    )
    tax_code = models.CharField(
        blank=True, max_length=50, null=True, help_text='tax identification numbers'
    )
    permanent_address = models.CharField(
        blank=True, max_length=250, null=True, help_text='frequently lived address'
    )
    current_resident = models.CharField(
        blank=True, max_length=250, null=True, help_text='Means the person who resides here currently'
    )
    attachment = models.JSONField(
        default=list,
        null=True,
        verbose_name='Attachment file',
        help_text=json.dumps(
            ["uuid4", "uuid4"]
        )
    )
    attachment_m2m = models.ManyToManyField(
        'attachments.Files',
        through='EmployeeMapSignatureAttachment',
        symmetrical=False,
        blank=True,
        related_name='signature_of_employee_info',
    )
    dependent_deduction = models.JSONField(default=list, verbose_name="employee's dependent information")

    class Meta:
        verbose_name = 'Employee Info'
        verbose_name_plural = 'Employee Info'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

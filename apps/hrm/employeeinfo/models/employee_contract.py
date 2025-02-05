import json

from django.db import models
from django.utils import timezone

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import MasterDataAbstractModel, CONTRACT_TYPE

from .employee_info import EmployeeInfo


class EmployeeContract(MasterDataAbstractModel):
    employee_info = models.ForeignKey(
        EmployeeInfo, on_delete=models.CASCADE,
        related_name='contract_map_employee_info',
        null=True
    )
    contract_type = models.SmallIntegerField(
        choices=CONTRACT_TYPE,
        default=0,
    )
    limit_time = models.BooleanField(
        verbose_name='limited time of contract',
        default=True,
    )
    effected_date = models.DateTimeField(
        verbose_name='effected date',
        default=timezone.now
    )
    expired_date = models.DateTimeField(
        verbose_name='expired date',
        null=True, blank=True
    )
    signing_date = models.DateTimeField(
        verbose_name='signing date',
        default=timezone.now
    )
    represent = models.ForeignKey(
        'hr.Employee', on_delete=models.SET_NULL,
        null=True,
        related_name='employee_represent'
    )
    file_type = models.SmallIntegerField(
        help_text='0: attach file, 1: online file',
        default=0,
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
        through='EmployeeContractMapAttachment',
        symmetrical=False,
        blank=True,
        related_name='file_of_employee_contract',
    )
    content = models.TextField(blank=True)
    sign_status = models.SmallIntegerField(
        help_text='0: unsigned, 1: signed',
        default=0,
    )

    def code_generator(self):
        emp_contract = EmployeeContract.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            contract_type=self.contract_type
        ).count()
        if not self.code:
            char = "HDTV" if self.contract_type == 0 else 'HDLD' if self.contract_type == 1 else 'PLHD'
            num_quotient, num_remainder = divmod(emp_contract, 1000)
            code = f"{char}{num_remainder + 1:03d}"
            if num_quotient > 0:
                code += f".{num_quotient}"
            self.code = code

    def before_save(self):
        self.code_generator()

    def save(self, *args, **kwargs):
        if self.sign_status == 0:
            self.before_save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Employee contract'
        verbose_name_plural = 'Employee contract'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class EmployeeContractMapAttachment(M2MFilesAbstractModel):
    employee_contract = models.ForeignKey(
        EmployeeContract,
        on_delete=models.CASCADE,
        verbose_name='Attachment file of Employee contract'
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'employee_contract'

    class Meta:
        verbose_name = 'Employee info attachments'
        verbose_name_plural = 'Employee info attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

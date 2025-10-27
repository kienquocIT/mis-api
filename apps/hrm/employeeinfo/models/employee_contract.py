import json

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.attachments.models import M2MFilesAbstractModel, update_files_is_approved
from apps.core.log.tasks import force_new_notify_many
from apps.core.mailer.tasks import send_mail_new_contract_submit
from apps.shared import MasterDataAbstractModel, CONTRACT_TYPE, call_task_background

from .employee_info import EmployeeInfo


class EmployeeContract(MasterDataAbstractModel):
    employee_info = models.ForeignKey(
        EmployeeInfo, on_delete=models.CASCADE,
        related_name='contract_map_employee_info',
        null=True
    )
    contract_type = models.SmallIntegerField(
        choices=CONTRACT_TYPE,
        null=True
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
        help_text='0: unsigned, 1: signing, 2: signed',
        default=0,
    )
    content_info = models.JSONField(
        default=dict,
        verbose_name='contract info via config',
        help_text=json.dumps(
            {
                'sign_01': ['emp_01_id', 'emp_02_id'],
                'sign_02': ['emp_01_id', 'emp_02_id'],
            }
        )
    )
    employee_salary_level = models.IntegerField(default=0)
    employee_salary = models.FloatField(default=0)
    employee_salary_insurance = models.FloatField(default=0)
    employee_salary_rate = models.FloatField(default=0)
    employee_salary_coefficient = models.FloatField(default=1)

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
        if self.sign_status == 2:
            update_files_is_approved(
                EmployeeContractMapAttachment.objects.filter(
                    employee_contract=self, attachment__is_approved=False
                ),
                self
            )
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


class EmployeeContractRuntime(MasterDataAbstractModel):
    employee_contract = models.OneToOneField(
        EmployeeContract,
        on_delete=models.CASCADE,
        related_name="runtime_of_contract"
    )
    members = models.JSONField(
        default=list,
        help_text='["employee_01_id", "employee_01_id"]',
        verbose_name='members assignee',
    )
    contract = models.TextField(blank=True)
    signatures = models.JSONField(
        default=dict,
        verbose_name='signatures parameter of contract',
        help_text=json.dumps(
            {
                'sign_01': {
                    'assignee': ['emp_01_id', 'emp_02_id'],
                    'stt': 'boolean',
                    'signed_by': 'employee_id',
                    'sign_image': 'base64 code'
                },
                'sign_02': {
                    'assignee': ['emp_01_id', 'emp_02_id'],
                    'stt': 'boolean',
                    'signed_by': 'employee_id',
                    'sign_image': 'base64 code'
                }
            }
        )
    )
    contract_status = models.SmallIntegerField(
        default=0,
        help_text='0: Signing, 1: Finished',
    )

    class Meta:
        verbose_name = 'Contract runtime'
        verbose_name_plural = 'Contract runtime'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


@receiver(post_save, sender=EmployeeContractRuntime)
def push_notify_contract_runtime(sender, instance, created, **kwargs):  # pylint: disable=W0613
    contract = instance.employee_contract
    company = contract.company
    tenant = contract.tenant
    created_email = contract.employee_created

    if created:
        # update contract status
        instance.employee_contract.sign_status = 1
        instance.employee_contract.save(update_fields=['sign_status'])

    # send user sign notify
    if instance.contract_status == 0:
        for key, employee in instance.signatures.items():
            print(key)
            if 'id' in employee['assignee'] and not employee['stt']:
                call_task_background(
                    my_task=force_new_notify_many,
                    **{
                        'data_list': [
                            {
                                'tenant_id': str(tenant.id),
                                'company_id': str(company.id),
                                'title': '',
                                'msg': _('You are required to sign a contract'),
                                'notify_type': 0,
                                'date_created': instance.date_created,
                                'doc_id': str(instance.id),
                                'doc_app': 'employeeinfo.EmployeeContractRuntime',
                                'employee_id': employee['assignee']['id'],
                                'employee_sender_id': str(created_email.id)
                            }
                        ]
                    }
                )
                break
    # send mail user sign

    employee_active = {}
    for item in instance.signatures.values():
        if not item['stt']:
            employee_active = item['assignee']
            break
    # gửi mail
    if 'id' in employee_active:
        call_task_background(
            my_task=send_mail_new_contract_submit,
            **{
                'tenant_id': str(tenant.id),
                'company_id': str(company.id),
                'assignee_id': str(employee_active['id']),
                'employee_created_id': str(created_email.id),
                'contract_id': str(contract.id),
                'signature_runtime_id': str(instance.id)
            }
        )
    print('contract signature runtime is activate')

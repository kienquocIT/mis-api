from django.db import models

from apps.core.attachments.models import M2MFilesAbstractModel
from .employee_info import EmployeeInfo


class EmployeeMapSignatureAttachment(M2MFilesAbstractModel):
    employee_info = models.ForeignKey(
        EmployeeInfo,
        on_delete=models.CASCADE,
        verbose_name='Employee info'
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'employee_info'

    class Meta:
        verbose_name = 'Employee info attachments'
        verbose_name_plural = 'Employee info attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

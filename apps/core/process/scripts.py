__all__ = [
    'create_member_first_of_process',
]

from apps.core.process.models import Process, ProcessMembers


def create_member_first_of_process():
    for process_obj in Process.objects.all():
        if process_obj.employee_created_id:
            filter_data = {
                'tenant': process_obj.tenant,
                'company': process_obj.company,
                'process': process_obj,
                'employee': process_obj.employee_created,
            }
            if not ProcessMembers.objects.filter(**filter_data).exists():
                ProcessMembers.objects.create(
                    tenant=process_obj.tenant,
                    company=process_obj.company,
                    process=process_obj,
                    employee=process_obj.employee_created,
                    employee_created=process_obj.employee_created,
                )

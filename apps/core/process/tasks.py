from celery import shared_task

from apps.core.process.models import Process, ProcessMembers


@shared_task
def sync_member_from_opp_to_process(process_id):
    try:
        process_obj = Process.objects.get(pk=process_id)
    except Process.DoesNotExist:
        pass
    else:
        if process_obj.opp:
            member_ids = list(process_obj.opp.get_members(return_obj_or_id='id'))
            for emp_id in member_ids:
                ProcessMembers.objects.get_or_create(
                    tenant=process_obj.tenant,
                    company=process_obj.company,
                    process=process_obj,
                    employee_id=emp_id,
                    is_system=True
                )
            member_was_removed = ProcessMembers.objects.filter(
                tenant=process_obj.tenant,
                company=process_obj.company,
                process=process_obj,
                is_system=True,
            ).exclude(employee_id__in=member_ids + [process_obj.employee_created_id])
            member_was_removed.delete()

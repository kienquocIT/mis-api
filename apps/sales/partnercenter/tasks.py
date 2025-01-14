from celery import shared_task

@shared_task
def update_num_of_records(list_obj, size):
    list_obj.num_of_records = size
    list_obj.save()
    return True

from celery import shared_task

from apps.core.chat3rd.models import MessengerToken
from apps.core.chat3rd.utils import GraphFbAccount


@shared_task
def messenger_scan_account_token(messenger_id):
    try:
        obj = MessengerToken.objects.get(id=messenger_id)
    except MessengerToken.DoesNotExist:
        raise ValueError('Messenger ID not found: %s' % (str(messenger_id)))

    return GraphFbAccount(token_obj=obj).sync_accounts_token()

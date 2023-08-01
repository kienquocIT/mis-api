import json
import os
import sys
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from apps.core.system.models import MailServerConfig


class Command(BaseCommand):
    help = 'Initials system data.'

    def handle(self, *args, **options):
        sys.stdout.write('[Init Mail Server] Started \n')
        obj = MailServerConfig.objects.filter(pk=settings.MAIL_CONFIG_OBJ_PK).first()
        if obj:
            sys.stdout.write('---- Skip load system mail config! \n')
        else:
            tokens_data = os.environ.get('MAIL_SERVER_TOKENS')
            creds_data = os.environ.get('MAIL_SERVER_CREDS', '{}')
            if tokens_data:
                tokens_data = json.loads(tokens_data)
                creds_data = json.loads(creds_data)
                if tokens_data:
                    dt_data = datetime.strptime(tokens_data['expiry'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    obj = MailServerConfig.objects.create(
                        id=settings.MAIL_CONFIG_OBJ_PK,
                        creds_data=creds_data,
                        token_data=tokens_data,
                        token=tokens_data['token'],
                        refresh_token=tokens_data['refresh_token'],
                        token_uri=tokens_data['token_uri'],
                        client_id=tokens_data['client_id'],
                        client_secret=tokens_data['client_secret'],
                        scopes=tokens_data['scopes'],
                        expiry=dt_data,
                    )
                    if obj:
                        sys.stdout.write('---- Init mail server config is success! \n')
                    else:
                        raise ValueError('Create object mail config is failure.')
                else:
                    raise ValueError('JSON object mail config is failure.')
            else:
                raise ValueError('Credentials and Tokens Data must be required from Environment.')

        sys.stdout.write('[Init Mail Server] Finish \n')

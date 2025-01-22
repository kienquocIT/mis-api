from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.chat3rd.models import MessengerToken, MessengerPageToken, MessengerMessage, MessengerPerson
from apps.shared import TypeCheck


class Command(BaseCommand):
    help = 'Chat3rd reset: Message, Person, Page, Token.'

    def add_arguments(self, parser):
        parser.add_argument('company_id', type=str, help='Company ID need reset')
        parser.add_argument(
            '--apps',
            type=str,
            help='List app need reset, split with comma',
            default='messenger,zalo',
            required=False,
        )

    def reset_messenger(self, company_id):
        self.stdout.write(f'▶ Start reset Messenger!')
        messages = MessengerMessage.objects.filter(company_id=company_id)
        if messages:
            self.stdout.write(f'♪ Messages: {messages.count()}')
            # messages.delete()
        persons = MessengerPerson.objects.filter(company_id=company_id)
        if persons:
            self.stdout.write(f'♪ Persons: {persons.count()}')
            # persons.delete()
        pages = MessengerPageToken.objects.filter(company_id=company_id)
        if pages:
            self.stdout.write(f'♪ Pages: {pages.count()}')
            # pages.delete()
        tokens = MessengerToken.objects.filter(company_id=company_id)
        if tokens:
            self.stdout.write(f'♪ Tokens: {tokens.count()}')
            # tokens.delete()
        self.stdout.write(f'■ Finish reset Messenger!')
        return True

    def reset_zalo(self, company_id):
        self.stdout.write(f'▶ Start reset Zalo!')
        self.stdout.write(f'■ Finish reset Zalo!')
        return True

    def handle(self, *args, **options):
        company_id = options.get('company_id', None)
        if company_id and TypeCheck.check_uuid(company_id):
            apps = options.get('apps', '')
            app_arr = [item.strip() for item in apps.split(",")]

            self.stdout.write(f'Start: company={company_id}, apps={app_arr}')

            self.stdout.write('—————————————————————')
            for idx, app_str in enumerate(app_arr):
                if app_str == 'messenger':
                    self.reset_messenger(company_id=company_id)
                elif app_str == 'zalo':
                    self.reset_zalo(company_id=company_id)
                if idx < len(app_arr) - 1:
                    self.stdout.write('∷∷∷ ∮∮∮ ∷∷∷')
            self.stdout.write('—————————————————————')

            self.stdout.write(f'Finish!')
        else:
            self.stdout.write(f'Finish with empty company!')

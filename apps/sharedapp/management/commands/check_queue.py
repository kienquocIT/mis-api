import json
import sys

from django.core.management.commands.makemessages import Command as BaseMakeMessagesCommand
from misapi.celery import app


class Command(BaseMakeMessagesCommand):
    help = 'Kiểm tra trạng thái Task trong Queue'

    SCOPE_ITEM = {
        'scheduled': 'Return list of scheduled tasks with details.',
        'reserved': 'Return list of currently reserved tasks, not including scheduled/active.',
        'active': 'Return list of tasks currently executed by workers.',
        'active_queues': 'Return information about queues from which worker consumes tasks.',
        'clock': 'Get the Clock value on workers.',
        'conf': 'Return configuration of each worker.',
        'memdump': 'Dump statistics of previous memsample requests.',
        'memsample': 'Return sample current RSS memory usage.',
        'ping': 'Ping all (or specific) workers.',
        'query_task': 'Return detail of tasks currently executed by workers.',
        'registered': 'Return all registered tasks per worker.',
        'report': 'Return human read-able report for each worker.',
        'stats': 'Return statistics of worker.',
    }
    SCOPE_KWARGS = {
        'memdump': {
            'sample': 10,
        }
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--scope', dest='scope', type=str, default='main',
            help='SCOPE: main=[scheduled, reversed, active], full=[*]'
        )
        parser.add_argument(
            '--scopeKwargs', dest='scope_kwargs', type=str, default='{}',
            help='SCOPE KWARGS: {"SCOPE_ITEM": {...config..},...}'
        )

    def handle(self, *args, **options):
        scope_item_keys = self.SCOPE_ITEM.keys()

        scope = options['scope']

        if scope == 'main':
            scope_collect = ['scheduled', 'reserved', 'active']
        elif scope == 'full':
            scope_collect = scope_item_keys
        else:
            scope_collect = [item.strip() for item in scope.split(",")]

        for tmp in scope_collect:
            if tmp not in scope_item_keys:
                raise ValueError('Scope is not found:', tmp)

        scope_kwargs = {
            **self.SCOPE_KWARGS,
            **json.loads(options['scope_kwargs']),
        }

        inspector = app.control.inspect()
        for scope_key in scope_collect:
            try:
                func = getattr(inspector, scope_key)
                if callable(func):
                    kw_args = scope_kwargs.get(scope_key, {})
                    value = func(**kw_args)
                    sys.stdout.write(f'{scope_key}: {self.SCOPE_ITEM[scope_key]} \n')
                    sys.stdout.write(f'\t {value} \n')
            except Exception as err:
                sys.stdout.write(f'{str(err)} \n')

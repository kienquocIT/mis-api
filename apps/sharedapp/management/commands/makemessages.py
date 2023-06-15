from django.core.management.commands.makemessages import Command as BaseMakeMessagesCommand


class Command(BaseMakeMessagesCommand):
    def handle(self, *args, **options):
        raise ValueError("Make messages is disable!")

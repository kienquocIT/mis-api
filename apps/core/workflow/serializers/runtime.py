from rest_framework import serializers


class RuntimeTaskSerializer(serializers.Serializer): # noqa
    action = serializers.IntegerField(
        help_text='Action from config and runtime suggest'
    )

from rest_framework import serializers

__all__ = [
    'AbstractListSerializerModel',
    'AbstractDetailSerializerModel',
    'AbstractCreateSerializerModel',
]


class AbstractListSerializerModel(serializers.ModelSerializer):
    def get_fields(self):
        return {
            'id': serializers.UUIDField(),
            **super().get_fields(),
            'system_status': serializers.IntegerField(),
        }

    class Meta:
        abstract = True


class AbstractDetailSerializerModel(serializers.ModelSerializer):
    def get_fields(self):
        return {
            'id': serializers.UUIDField(),
            **super().get_fields(),
            'workflow_runtime_id': serializers.UUIDField(),
            'system_status': serializers.IntegerField(),
        }

    class Meta:
        abstract = True


class AbstractCreateSerializerModel(serializers.ModelSerializer):
    def get_fields(self):
        return {
            **super().get_fields(),
            'system_status': serializers.ChoiceField(
                choices=[0, 1],
                help_text='0: draft, 1: created',
                default=0,
            )
        }

    class Meta:
        abstract = True

__all__ = [
    'FormItemBaseValidation',
    'BaseInputsDataItemSerializer',
]

from rest_framework import serializers

from apps.core.forms.i18n import FormMsg
from .serializers_base import ConfigBase


class BaseInputsDataItemSerializer(serializers.Serializer):  # noqa
    args = serializers.ListSerializer(child=serializers.CharField(), allow_empty=True, default=[])
    name = serializers.CharField()
    label = serializers.CharField(allow_blank=True)
    kwargs = serializers.DictField()
    display = serializers.BooleanField()


class FormItemBaseValidation(serializers.Serializer):  # noqa
    type = serializers.CharField()

    config = ConfigBase()  # need override to Class Validation of type

    inputs_data = BaseInputsDataItemSerializer(many=True, allow_null=True, default=[])
    INPUT_DATA_LENGTH_DEFAULT = 1

    def validate_inputs_data(self, attrs):
        if attrs and isinstance(attrs, list) and len(attrs) == self.INPUT_DATA_LENGTH_DEFAULT:
            return attrs
        raise serializers.ValidationError(
            {
                'inputs_data': FormMsg.INPUT_DATA_LENGTH_INCORRECT
            }
        )

    def manage_data(self, input_names: list[str], validated_data: dict[str, any], body_data: dict[str, any]):
        if isinstance(input_names, list) and len(input_names) == self.INPUT_DATA_LENGTH_DEFAULT:
            config = validated_data['config']
            input_values = [body_data.get(inp_name, None) for inp_name in input_names]

            config_cls = self.fields['config']
            config_cls.manage_reset(
                config=config,
                input_names=input_names,
                input_values=input_values,
                body_data=body_data,
            )
            config_cls.manage__valid()
            body_data.update(config_cls.manage__finish())
        else:
            raise serializers.ValidationError(
                {
                    'detail': FormMsg.FORM_CONFIG_EXCEPTION_DENY_RUNTIME_SUBMIT,
                }
            )

__all__ = [
    'FormValidation',
]

from rest_framework import serializers
from apps.core.forms.i18n import FormMsg
from .base import *
from .forms import *


class FormItemValidation:
    def init_cls(self) -> True or serializers.ValidationError:
        # match type with class serializer
        if self.type_field in MATCH_FORM:
            self.cls = MATCH_FORM[self.type_field]
            return True
        raise serializers.ValidationError(
            {
                'type': 'The type not match supported class'
            }
        )

    def init_obj(self) -> True or serializers.ValidationError:
        # init serializer with data config after init_cls
        if self.cls:
            self.obj = self.cls(
                data={
                    'type': self.type_field,
                    'config': self.config,
                    'inputs_data': self.inputs_data,
                }
            )
            return True
        raise serializers.ValidationError(
            {
                'type': 'The type not match supported class'
            }
        )

    def get_input_names(self):
        if len(self.input_names) == 0:
            if self.inputs_data and isinstance(self.inputs_data, list):
                for input_config in self.inputs_data:
                    if input_config and isinstance(input_config, dict) and 'name' in input_config:
                        name = input_config['name']
                        if name:
                            self.input_names.append(name)
                        else:
                            raise serializers.ValidationError(
                                {
                                    'detail': FormMsg.FORM_CONFIG_EXCEPTION_DENY_RUNTIME_SUBMIT
                                }
                            )
        return self.input_names

    def manage_item_data(self, validated_data, body_data):
        self.obj.manage_data(
            input_names=self.input_names,
            validated_data=validated_data,
            body_data=body_data
        )

    def __init__(self, idx: str, config_data: dict):
        self.cls: serializers.Serializer.__class__ = None
        self.obj: serializers.Serializer or None = None
        self.input_names: list[str] = []

        self.idx = idx
        self.type_field = config_data.get('type', None)
        self.config = config_data.get('config', None)
        self.inputs_data = config_data.get('inputs_data', None)

        self.init_cls()
        self.init_obj()


class FormValidation:
    def runtime__valid(self, body_data: dict[str, any]) -> dict[str, any] or serializers.ValidationError:
        body_data_resolved = {
            key: value for key, value in body_data.items() if key in self.input_names
        }

        errors = {}
        for item_cls in self.cls_list:
            try:
                item_cls.manage_item_data(
                    validated_data=self.configs_validated[item_cls.idx],
                    body_data=body_data_resolved
                )
            except serializers.ValidationError as err:
                errors.update(err.detail)

        if errors:
            raise serializers.ValidationError(errors)
        return body_data_resolved

    @classmethod
    def convert_to_dict(cls, input_ordered_dict):
        return {k: cls.convert_to_dict(v) if isinstance(v, dict) else v for k, v in input_ordered_dict.items()}

    def __init__(self, configs_order, configs, firing_errors: bool = True):
        # storage input data
        self.configs_order = configs_order
        self.configs = configs

        # private variable in class
        self.cls_list: list[FormItemValidation] = []
        if (
                self.configs_order and isinstance(self.configs_order, list)
                and self.configs and isinstance(self.configs, dict)
        ):
            for idx in self.configs_order:
                config_data = self.configs.get(idx, None)
                if config_data and isinstance(config_data, dict):
                    cls = FormItemValidation(idx=idx, config_data=config_data)
                    self.cls_list.append(cls)
        # call valid
        self.errors: dict[str, any] = {}
        self.configs_validated: dict[str, any] = {}
        self.input_names = []
        for item_cls in self.cls_list:
            # validate configs
            item_cls.obj.is_valid(raise_exception=False)
            if item_cls.obj.errors:
                self.errors[item_cls.idx] = item_cls.obj.errors
            else:
                # push mapping input name with class control
                input_names_of_cls = item_cls.get_input_names()
                if isinstance(input_names_of_cls, list):
                    self.input_names += input_names_of_cls

                self.configs_validated[item_cls.idx] = self.convert_to_dict(item_cls.obj.validated_data)
        if firing_errors and self.errors:
            raise serializers.ValidationError(self.errors)

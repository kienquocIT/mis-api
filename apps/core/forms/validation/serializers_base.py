import re

from rest_framework import serializers

from apps.core.forms.i18n import FormMsg


class ManageBase(serializers.Serializer):  # noqa # pylint: disable=R0902
    @property
    def manage_errors(self):
        return self._manage_errors

    @manage_errors.setter
    def manage_errors(self, errors: dict[str, any]):
        for key, value in errors.items():
            if key in self._manage_errors:
                self._manage_errors[key].append(value)
            else:
                self._manage_errors[key] = [value]

    @property
    def manage_inputs_data(self):
        return self._manage_inputs_data

    @manage_inputs_data.setter
    def manage_inputs_data(self, data: dict[str]):
        self._manage_inputs_data.update(data)

    @property
    def manage_input_names(self):
        return self._manage_input_names

    @property
    def manage_input_values(self):
        return self._manage_input_values

    @property
    def body_data(self):
        return self._body_data

    @body_data.setter
    def body_data(self, data: dict[str, any]):
        self._body_data.update(data)

    @property
    def mc_required(self):
        required = self.manage_configs.get('required', False)
        return required if isinstance(required, bool) else False

    @property
    def mc_visibility(self):
        return self.manage_configs.get('visibility', 'unset')

    @property
    def mc_disabled(self):
        if self.mc_visibility == 'disable':
            return True
        return False

    @property
    def mc_hidden(self):
        if self.mc_visibility == 'hide':
            return True
        return False

    def manage_reset(
            self,
            config: dict[str, any],
            input_names: list[str],
            input_values: list[str],
            body_data: dict[str, any],
    ):
        self.manage_configs = config
        self._manage_input_names = input_names
        self._manage_input_values = input_values
        self._manage_inputs_data = {
            inp_name: input_values[idx] for idx, inp_name in enumerate(input_names)
        }
        self._body_data = body_data

        self._manage_errors = {}

    def __init__(self, *args, **kwargs):
        self.manage_configs: dict[str, any] = {}
        self._manage_input_names = []
        self._manage_input_values = []
        self._manage_inputs_data: dict[str, any] = {}
        self._body_data = {}

        self._manage_errors: dict[str, list[any]] = {}
        self.manage_state_required: bool = True  # True: pass, Fail
        super().__init__(*args, **kwargs)

    def manage__valid(self, *args, **kwargs):
        raise NotImplementedError

    def manage__finish(self) -> serializers.ValidationError or dict[str, any]:
        if self.manage_errors:
            print('self.manage_errors:', self.manage_errors)
            raise serializers.ValidationError(self.manage_errors)
        return self.manage_inputs_data

    def call_m(
            self,
            func,
            *args,
            input_name,
            input_value,
            opts: dict[str, any] = None,
            opts_active: bool = True,
            **kwargs
    ):
        if not opts:
            opts = {}
        opts = {
            'skip_empty_not_required': True,
            'remove_with_disabled': True,
            'reset_value_with_hidden': True,
            **opts
        }

        if input_name in self.manage_inputs_data:
            if opts_active:
                if opts['reset_value_with_hidden'] is True and self.mc_hidden:
                    input_value = self.manage_configs.get('init_value', '')
                    if input_name in self.manage_inputs_data:
                        self.manage_inputs_data[input_name] = input_value

                if opts['remove_with_disabled'] is True and self.mc_disabled:
                    self.manage_inputs_data.pop(input_name, input_value)
                    return True

                if opts['skip_empty_not_required'] is True and not input_value and not self.mc_required:
                    return True

            if isinstance(func, str):
                if not hasattr(self, func):
                    raise ValueError(f'The "{func}" method is not implement in "{self.__class__.__name__}" class')
                func = getattr(self, func)
            if not callable(func):
                raise ValueError(f'The "{func}" method is not implement in "{self.__class__.__name__}" class')
            try:
                func(*args, input_name=input_name, input_value=input_value, **kwargs)
            except serializers.ValidationError as errs:
                self.manage_errors = {key: str(value) for key, value in errs.detail.items()}
        else:
            # if input_name not in self.manage_inputs_data
            # => Detect attacks or logical errors in the code.
            raise serializers.ValidationError(
                {
                    'detail': FormMsg.FORM_CONFIG_EXCEPTION_DENY_RUNTIME_SUBMIT,
                }
            )
        return True


class ConfigBase(ManageBase):  # noqa
    label = serializers.CharField(allow_blank=True, max_length=255)

    @classmethod
    def validate_label(cls, attrs):
        return attrs.strip()

    is_hide_label = serializers.BooleanField(default=False)
    instruction = serializers.CharField(allow_blank=True)

    @classmethod
    def validate_instruction(cls, attrs):
        return attrs.strip()

    size = serializers.ChoiceField(default='medium', choices=['extra-small', 'small', 'medium', 'large', 'extra-large'])

    place_holder = serializers.CharField(allow_blank=True)

    @classmethod
    def validate_place_holder(cls, attrs):
        return attrs.strip()


class ConfigInitValue(ManageBase):  # noqa
    init_value = serializers.CharField(required=False, allow_blank=True)

    @classmethod
    def validate_init_value(cls, attrs):
        return attrs.strip()


class ConfigMinMaxLength(ManageBase):  # noqa
    minlength = serializers.IntegerField(required=False)
    maxlength = serializers.IntegerField(required=False)

    def validate_maxlength(self, attrs):
        try:
            min_value = int(self.parent.initial_data.get('config', {}).get('minlength', 0))
        except ValueError:
            min_value = 0
        if min_value > attrs:
            raise serializers.ValidationError(
                {
                    'maxlength': 'The field value must greater than minlength value',
                }
            )
        return attrs

    def manage_minlength(self, input_name, input_value):
        if input_value != "":
            minlength = self.manage_configs.get('minlength', 0)
            if not isinstance(minlength, int):
                minlength = 0

            if len(input_value) < minlength:
                raise serializers.ValidationError(
                    {
                        input_name: FormMsg.MINLENGTH_FAIL.format(minlength)
                    }
                )

    def manage_maxlength(self, input_name, input_value):
        if input_value != "":
            maxlength = self.manage_configs.get('maxlength', 0)
            if not isinstance(maxlength, int):
                maxlength = 0

            if len(input_value) > maxlength:
                raise serializers.ValidationError(
                    {
                        input_name: FormMsg.MAXLENGTH_FAIL.format(maxlength)
                    }
                )


class ConfigMinMax(ManageBase):  # noqa
    min = serializers.IntegerField(default=0, min_value=0, required=False)
    max = serializers.IntegerField(default=255, max_value=255, required=False)

    def validate_max(self, attrs):
        try:
            min_value = int(self.parent.initial_data.get('config', {}).get('min', 0))
        except ValueError:
            min_value = 0
        if min_value > attrs:
            raise serializers.ValidationError(
                {
                    'max': 'The field value must greater than min value',
                }
            )
        return attrs

    def manage_min(self, input_name, input_value):
        if input_value != "":
            min_val = self.manage_configs.get('min', 0)
            if not isinstance(min_val, int):
                min_val = 0

            if len(input_value) < min_val:
                raise serializers.ValidationError({input_name: FormMsg.MIN_FAIL.format(min_val)})

    def manage_max(self, input_name, input_value):
        if input_value != "":
            max_val = self.manage_configs.get('max', 0)
            if not isinstance(max_val, int):
                max_val = 0

            if len(input_value) > max_val:
                raise serializers.ValidationError({input_name: FormMsg.MAX_FAIL.format(max_val)})


class ConfigRequired(ManageBase):  # noqa
    required = serializers.BooleanField(default=False)

    def manage_required(self, input_name, input_value):
        required = self.manage_configs.get('required', False)
        if not isinstance(required, bool):
            required = False

        input_value = str(input_value)
        if required is True and not input_value:
            raise serializers.ValidationError(
                {
                    input_name: FormMsg.REQUIRED_FAIL,
                }
            )


class ConfigUnique(ManageBase):  # noqa
    unique = serializers.BooleanField(default=False)


class ConfigVisibility(ManageBase):  # noqa
    visibility = serializers.ChoiceField(default='unset', choices=['unset', 'hide', 'disable'])


class ConfigInputType(ManageBase):  # noqa
    input_type = serializers.ChoiceField(
        default='any-character',
        choices=['any-character', 'letters-only', 'letters-number', 'letters-number-space', 'letters-space', 'custom']
    )

    input_type_value = serializers.CharField(allow_blank=True)

    def validate_input_type(self, attrs):
        if attrs == 'custom':
            input_type_value = self.parent.initial_data.get('config', {}).get('input_type_value', '')
            if not input_type_value:
                raise serializers.ValidationError(
                    {
                        'input_type_value': 'The input type value must be required',
                    }
                )
        return attrs

    def manage_input_type(self, input_name, input_value):
        if input_value != "":
            input_type = self.manage_configs.get('input_type', 'any-characters')
            input_type_value = self.manage_configs.get('input_type_value', '')

            if input_type != 'any-character':
                if input_type == 'letters-only':
                    regex = '[a-zA-Z]*'
                elif input_type == 'letters-number':
                    regex = '[a-zA-Z0-9]*'
                elif input_type == 'letter-number-space':
                    regex = '[a-zA-Z0-9 ]*'
                elif input_type == 'letters-space':
                    regex = '[a-zA-Z ]*'
                elif input_type == 'custom':
                    if input_type_value:
                        regex = input_type_value
                    else:
                        raise serializers.ValidationError(
                            {
                                input_name: FormMsg.INPUT_TYPE_FAIL
                            }
                        )
                else:
                    raise serializers.ValidationError({input_name: FormMsg.FORM_CONFIG_EXCEPTION_DENY_RUNTIME_SUBMIT})
                pattern = re.compile(regex)
                if not pattern.match(input_value):
                    raise serializers.ValidationError(
                        {
                            input_name: FormMsg.INPUT_TYPE_FAIL
                        }
                    )


class ConfigInputTextCase(ManageBase):  # noqa
    input_text_case = serializers.ChoiceField(default='unset', choices=['unset', 'lower', 'upper', 'capitalize'])

    def manage_input_text_case(self, input_name, input_value):
        if input_value != "":
            input_text_case = self.manage_configs.get('input_text_case', 'unset')
            if input_text_case != 'unset':
                if input_text_case == 'upper':
                    if not (input_value.isupper() or input_value.isdigit()):
                        raise serializers.ValidationError(
                            {input_name: FormMsg.INPUT_TEXT_CASE_FAIL.format(input_text_case)}
                        )
                elif input_text_case == 'lower':
                    if not (input_value.islower() or input_value.isdigit()):
                        raise serializers.ValidationError(
                            {input_name: FormMsg.INPUT_TEXT_CASE_FAIL.format(input_text_case)}
                        )
                elif input_text_case == 'capitalize':
                    if not (input_value.istitle() or input_value.isdigit()):
                        raise serializers.ValidationError(
                            {input_name: FormMsg.INPUT_TEXT_CASE_FAIL.format(input_text_case)}
                        )
                else:
                    raise serializers.ValidationError({input_name: FormMsg.FORM_CONFIG_EXCEPTION_DENY_RUNTIME_SUBMIT})

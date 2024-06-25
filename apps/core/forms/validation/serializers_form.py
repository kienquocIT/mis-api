# pylint: disable=W1401

__all__ = [
    'FormSingleLineConfigSerializer',
    'FormMultipleLineConfigSerializer',
    'FormNumberConfigSerializer',
    'FormPhoneConfigSerializer',
    'FormEmailConfigSerializer',
]

from .serializers_base import *  # pylint: disable=W0401,W0614


# re-define class with field
# def create_serializer_class(base_class, field_name, field_type):
#     return type('CustomSerializer', (base_class,), {field_name: field_type})

class FormSingleLineConfigSerializer(  # noqa
    ConfigBase, ConfigInitValue, ConfigMinMaxLength, ConfigRequired, ConfigUnique, ConfigVisibility,
    ConfigInputType, ConfigInputTextCase,
):
    def manage__valid(self, *args, **kwargs):
        ctx = {
            'input_value': self.manage_input_values[0],
            'input_name': self.manage_input_names[0],
        }
        self.call_m(func=self.manage_required, **ctx)
        self.call_m(func=self.manage_minlength, **ctx)
        self.call_m(func=self.manage_maxlength, **ctx)
        self.call_m(func=self.manage_input_type, **ctx)
        self.call_m(func=self.manage_input_text_case, **ctx)


class FormMultipleLineConfigSerializer(  # noqa
    ConfigBase, ConfigInitValue, ConfigRequired, ConfigVisibility, ConfigInputTextCase, ConfigMinMax,
):
    rows = serializers.IntegerField(default=3)
    type_count = serializers.ChoiceField(default='characters', choices=['characters', 'words'])
    max = serializers.IntegerField(default=65535, max_value=65535, required=False)

    def manage_type_count(self, input_name, input_value):
        if input_value != "":
            type_count = self.manage_configs.get('type_count', 'characters')
            min_val = self.manage_configs.get('min', 0)
            if not isinstance(min_val, int):
                min_val = 0
            max_val = self.manage_configs.get('max', 0)
            if not isinstance(max_val, int):
                max_val = 0
            if type_count == 'characters':
                if len(input_value) > max_val or len(input_value) < min_val:
                    raise serializers.ValidationError(
                        {input_name: FormMsg.CHARACTERS_LIMIT_FAIL.format(min_val, max_val)}
                    )
            elif type_count == 'words':
                words_count = input_value.split(" ")
                if len(words_count) > max_val or len(words_count) < min_val:
                    raise serializers.ValidationError(
                        {input_name: FormMsg.CHARACTERS_LIMIT_FAIL.format(min_val, max_val)}
                    )
            else:
                raise serializers.ValidationError({input_name: FormMsg.FORM_CONFIG_EXCEPTION_DENY_RUNTIME_SUBMIT})

    def manage__valid(self, *args, **kwargs):
        ctx = {
            'input_value': self.manage_input_values[0],
            'input_name': self.manage_input_names[0],
        }
        self.call_m(func=self.manage_required, **ctx)
        self.call_m(func=self.manage_input_text_case, **ctx)
        self.call_m(func=self.manage_type_count, **ctx)


class FormNumberConfigSerializer(  # noqa
    ConfigBase, ConfigInitValue, ConfigRequired, ConfigUnique, ConfigVisibility, ConfigMinMax,
):
    label_for_report = serializers.CharField(max_length=255)
    max = serializers.IntegerField(default=999999999, max_value=999999999, required=False)
    validate_value_type = serializers.ChoiceField(default='unset', choices=['unset', 'int', 'float'])

    unit_label_for_report = serializers.CharField(max_length=255)
    unit_code = serializers.CharField(allow_blank=True)
    unit_placement = serializers.ChoiceField(default='suffix', choices=['suffix', 'prefix'], required=False)
    unit_width_px = serializers.IntegerField(default=60, required=False)
    unit_text_align = serializers.ChoiceField(default='unit_text_align', choices=['center', 'left', 'right'])

    def validate_unit_code(self, attrs):
        if attrs:
            main_config = self.parent.initial_data.get('config', {})
            unit_placement = main_config.get('unit_placement', None)
            unit_width_px = main_config.get('unit_width_px', None)
            unit_text_align = main_config.get('unit_text_align', None)
            if not unit_placement or not unit_width_px or not unit_text_align:
                raise serializers.ValidationError(
                    {
                        'unit_code': 'The config unit is required when the unit code has a value',
                    }
                )
            return attrs
        return ""

    def manage_unit_code(self, input_name, input_value):
        unit_code = self.manage_configs.get('unit_code', '')
        if unit_code:
            if unit_code != input_value:
                raise serializers.ValidationError({input_name: FormMsg.UNIT_CODE_FAIL})

    def manage_validate_value_type(self, input_name, input_value):
        if input_value != "":
            validate_value_type = self.manage_configs.get('validate_value_type', 'unset')
            if validate_value_type != 'unset':
                if validate_value_type == 'int':
                    if not isinstance(input_value, int):
                        raise serializers.ValidationError({input_name: FormMsg.VALIDATE_VALUE_TYPE_FAIL_INT})
                elif validate_value_type == 'float':
                    if not isinstance(input_value, float or str):
                        raise serializers.ValidationError({input_name: FormMsg.VALIDATE_VALUE_TYPE_FAIL_FLOAT})
                else:
                    if not isinstance(input_value, int or float):
                        raise serializers.ValidationError({input_name: FormMsg.VALIDATE_VALUE_TYPE_FAIL_NUMBER})

    def manage__valid(self, *args, **kwargs):
        ctx = {
            'input_name': self.manage_input_names[0],
            'input_value': self.manage_input_values[0],
        }
        inp_value_unit = self.manage_input_values[1]

        self.call_m(func=self.manage_required, **ctx)
        self.call_m(func=self.manage_min, **ctx)
        self.call_m(func=self.manage_max, **ctx)
        self.call_m(
            func=self.manage_unit_code, input_name=ctx['input_name'], input_value=inp_value_unit, opts_active=False
        )
        self.call_m(func=self.manage_validate_value_type, **ctx)


class FormPhoneConfigSerializer(  # noqa
    ConfigBase, ConfigRequired, ConfigVisibility
):
    label_for_report = serializers.CharField(max_length=255)
    label_region_for_report = serializers.CharField(max_length=255)

    region_enable = serializers.BooleanField(default=True)
    region_visible = serializers.BooleanField(default=True)
    region_allowed_list = serializers.ListSerializer(child=serializers.CharField(), allow_empty=True)
    region_default = serializers.CharField()

    def validate_region_enable(self, attrs):
        if attrs is True:
            main_config = self.parent.initial_data.get('config', {})
            region_visible = main_config.get('region_visible', self.data['region_visible'])

            if not isinstance(region_visible, bool):
                raise serializers.ValidationError(
                    {
                        'region_visible': 'This field should be boolean type'
                    }
                )

            region_allowed_list = main_config.get('region_allowed_list', [])
            region_default = main_config.get('region_default', None)
            if not region_allowed_list or not region_default:
                raise serializers.ValidationError(
                    {
                        'region_enable': 'The config region is required when the region is enable',
                    }
                )
            if region_default not in region_allowed_list:
                raise serializers.ValidationError(
                    {
                        'region_default': 'The default value must be in the allowed list'
                    }
                )

            return attrs
        return False

    def manage_region_enable(self, input_name, **kwargs):
        region_value = self.manage_input_values[1]
        region_enable = self.manage_configs.get('region_enable', True)
        if region_enable is True:
            region_allowed_list = self.manage_configs.get('region_allowed_list', [])
            if not isinstance(region_allowed_list, list):
                region_allowed_list = []

            if region_value not in region_allowed_list:
                raise serializers.ValidationError({input_name: FormMsg.REGION_FAIL})

    def manage_phone_number_with_region(self, input_name, input_value):  # pylint: disable=R0912
        if input_value != "":
            region_value = self.manage_input_values[1]
            if region_value == '1':
                regex = '^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'
            elif region_value == '7':
                regex = '^[0-9]{10}$'
            elif region_value == '33':
                regex = '^[0-9]{9}$'
            elif region_value == '34':
                regex = '^[0-9]{9}$'
            elif region_value == '39':
                regex = '^[0-9]{6,11}$'
            elif region_value == '44':
                regex = '^[0-9]{7,10}$|^[0-9]{12}$'
            elif region_value == '49':
                regex = '^[0-9]{6,13}$'
            elif region_value == '52':
                regex = '^[0-9]{10,12}$'
            elif region_value == '54':
                regex = '^[0-9]{10}$'
            elif region_value == '55':
                regex = '^[0-9]{10,11}$'
            elif region_value == '57':
                regex = '^[0-9]{8,10}$'
            elif region_value == '61':
                regex = '^[0-9]{5,15}$'
            elif region_value == '62':
                regex = '^[0-9]{5,10}$'
            elif region_value == '64':
                regex = '^[0-9]{3,10}$'
            elif region_value == '66':
                regex = '^[0-9]{8}$|^[0-9]{9}$'
            elif region_value == '81':
                regex = '^[0-9]{5,13}$'
            elif region_value == '82':
                regex = '^[0-9]{8,11}$'
            elif region_value == '84':
                regex = '^((\+84)|0)([35789]|1[2389])([0-9]{8})$'
            elif region_value == '86':
                regex = '^[0-9]{5,12}$'
            elif region_value == '91':
                regex = '^[0-9]{7,10}$'
            else:
                raise serializers.ValidationError({input_name: FormMsg.FORM_CONFIG_EXCEPTION_DENY_RUNTIME_SUBMIT})

            pattern = re.compile(regex)
            if not pattern.match(input_value):
                raise serializers.ValidationError(
                    {
                        input_name: FormMsg.INPUT_TYPE_FAIL
                    }
                )

    def manage__valid(self, *args, **kwargs):
        ctx = {
            'input_name': self.manage_input_names[0],
            'input_value': self.manage_input_values[1],
        }
        self.call_m(func=self.manage_required, **ctx)
        self.call_m(func=self.manage_region_enable, **ctx)
        self.call_m(func=self.manage_phone_number_with_region, **ctx, opts_active=False)


class FormEmailConfigSerializer(  # noqa
    ConfigBase, ConfigInitValue, ConfigRequired, ConfigVisibility, ConfigInputTextCase, ConfigMinMax,
):
    max = serializers.IntegerField(default=255, max_value=255)
    domain_allow_validation = serializers.ChoiceField(
        default='unset',
        choices=['unset', 'allow'],
    )
    domain_allow_validation_data = serializers.CharField(allow_blank=True)

    def validate_domain_allow_validation(self, attrs):
        if attrs == 'allow':
            main_config = self.parent.initial_data.get('config', {})
            domain_allow_validation_data = main_config.get('domain_allow_validation_data', '')
            if not domain_allow_validation_data:
                raise serializers.ValidationError(
                    {
                        'domain_allow_validation_data': 'The domain allow data must be required'
                    }
                )
        return attrs

    domain_restrict_validation = serializers.ChoiceField(
        default='unset',
        choices=['unset', 'restrict'],
    )
    domain_restrict_validation_data = serializers.CharField(allow_blank=True)

    def validate_domain_restrict_validation(self, attrs):
        if attrs == 'restrict':
            main_config = self.parent.initial_data.get('config', {})
            domain_restrict_validation_data = main_config.get('domain_restrict_validation_data', '')
            if not domain_restrict_validation_data:
                raise serializers.ValidationError(
                    {
                        'domain_restrict_validation_data': 'The domain restrict must be required',
                    }
                )
        return attrs

    def manage_email(self, input_name, input_value):
        if input_value != "":
            domain_allow_validation = self.manage_configs.get('domain_allow_validation', 'unset')
            domain_allow_validation_data = [item.strip() for item in
                                            self.manage_configs.get('domain_allow_validation_data', '').split(",")]
            domain_restrict_validation = self.manage_configs.get('domain_restrict_validation', 'unset')
            domain_restrict_validation_data = [
                item.strip() for item in self.manage_configs.get('domain_restrict_validation_data', '').split(",")
            ]

            if input_value:
                arr_value = input_value.split("@")
                if '@' in input_value and len(arr_value) >= 2:
                    domain = arr_value[len(arr_value) - 1]
                    if domain_allow_validation == 'allow':
                        if domain not in domain_allow_validation_data:
                            raise serializers.ValidationError({input_name: FormMsg.EMAIL_ALLOW_FAIL})

                    if domain_restrict_validation == 'restrict':
                        if domain in domain_restrict_validation_data:
                            raise serializers.ValidationError({input_name: FormMsg.EMAIL_RESTRICT_FAIL})
                else:
                    raise serializers.ValidationError({input_name: FormMsg.EMAIL_TYPE_FAIL})

    def manage__valid(self, *args, **kwargs):
        ctx = {
            'input_name': self.manage_input_names[0],
            'input_value': self.manage_input_values[0],
        }
        self.call_m(func=self.manage_required, **ctx)
        self.call_m(func=self.manage_input_text_case, **ctx)
        self.call_m(func=self.manage_min, **ctx)
        self.call_m(func=self.manage_max, **ctx)
        self.call_m(func=self.manage_email, **ctx)

# pylint: disable=W1401
import datetime

from apps.shared.html_constant import FORM_SANITIZE_TRUSTED_DOMAIN_LINK
from apps.core.mailer.handle_html import HTMLController

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
        self.call_m(func=self.manage_phone_number_with_region, **{
            **ctx,
            'input_value': self.manage_input_values[0],
        }, opts_active=False)


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


class FormSelectOptions(serializers.Serializer):  # noqa
    title = serializers.CharField(max_length=255)
    value = serializers.CharField(max_length=255)
    is_default = serializers.BooleanField(default=False)
    is_default_multiple = serializers.BooleanField(default=False)
    col = serializers.CharField(max_length=50, allow_blank=True, required=False)
    row = serializers.CharField(max_length=50, allow_blank=True, required=False)
    group = serializers.CharField(max_length=5, allow_blank=True, required=False)


class FormSelectConfigSerializer(  # noqa
    ConfigBase, ConfigRequired, ConfigVisibility,
):
    style = serializers.ChoiceField(default='default', choices=['default', 'xbox', 'matrix'])
    matrix_cols = serializers.ListSerializer(child=serializers.CharField(max_length=50), min_length=0, max_length=20)
    matrix_rows = serializers.ListSerializer(child=serializers.CharField(max_length=50), min_length=0, max_length=20)
    matrix_group_by = serializers.ChoiceField(default='', allow_blank=True, choices=['', 'col', 'row'])

    options = FormSelectOptions(many=True, default=[])

    @classmethod
    def validate_options(cls, attrs):
        if attrs and isinstance(attrs, list) and len(attrs) > 0:
            default_value = None
            title_arr = []
            for item in attrs:
                if item and isinstance(item, dict) and 'is_default' in item:
                    if item['is_default'] is True:
                        if default_value is not None:
                            raise serializers.ValidationError(
                                {
                                    'options': FormMsg.SELECT_DEFAULT_UNIQUE
                                }
                            )
                    title_arr.append(item['title'])
                else:
                    raise serializers.ValidationError({'options': FormMsg.SELECT_OPTION_REQUIRED})

            if len(set(title_arr)) != len(title_arr):
                raise serializers.ValidationError({'options': FormMsg.SELECT_TITLE_UNIQUE})
            return attrs
        raise serializers.ValidationError({'options': FormMsg.SELECT_OPTION_REQUIRED})

    def manage_options(self, input_name, input_value):  # pylint: disable=R0912
        if self.mc_required and not input_value:
            raise serializers.ValidationError({input_name: FormMsg.REQUIRED_FAIL})

        is_multiple = self.manage_configs.get('is_multiple', False)
        options = self.manage_configs.get('options', [])
        matrix_group_by = self.manage_configs.get('matrix_group_by', None)
        if options and isinstance(options, list) and len(options) > 0 and isinstance(is_multiple, bool):
            title_arr = []
            value_arr = []
            group_by_key = {}
            groups = []
            for item in options:
                if isinstance(item, dict):
                    if 'title' in item:
                        title_arr.append(item['title'])
                    if 'value' in item:
                        value_arr.append(item['value'])
                    if 'group' in item and item['group'] != "":
                        groups.append(item['group'])
                        group_by_key[item['value']] = item['group']
                else:
                    raise serializers.ValidationError({input_name: FormMsg.OPTIONS_FAIL})
            if len(title_arr) == 0 or len(value_arr) == 0:
                raise serializers.ValidationError({input_name: FormMsg.OPTIONS_FAIL})

            if is_multiple is True and isinstance(input_value, list):
                style = self.manage_configs.get('style', None)
                if style == 'matrix':
                    groups = list(set(groups))
                    if groups and group_by_key:
                        group_in_value = {
                            key: [] for key in groups
                        }
                        for inp_value in input_value:
                            if inp_value not in value_arr or inp_value not in group_by_key:
                                raise serializers.ValidationError({input_name: FormMsg.OPTIONS_FAIL})
                            group_index = group_by_key[inp_value]
                            group_in_value[group_index].append(inp_value)

                        if len(groups) != len(group_in_value.keys()):
                            raise serializers.ValidationError({input_name: FormMsg.OPTIONS_FAIL})
                        for _key, inps_value in group_in_value.items():
                            if not (isinstance(inps_value, list) and len(inps_value) == 1):
                                if matrix_group_by == 'row':
                                    raise serializers.ValidationError({input_name: FormMsg.OPTIONS_INCORRECT_ROW})
                                if matrix_group_by == 'col':
                                    raise serializers.ValidationError({input_name: FormMsg.OPTIONS_INCORRECT_COL})
                                raise serializers.ValidationError({input_name: FormMsg.OPTIONS_FAIL})
                    else:
                        raise serializers.ValidationError({input_name: FormMsg.OPTIONS_FAIL})
                else:
                    for inp_value in input_value:
                        if inp_value not in value_arr:
                            raise serializers.ValidationError({input_name: FormMsg.OPTIONS_FAIL})
            elif is_multiple is False and isinstance(input_value, str):
                if input_value not in title_arr:
                    raise serializers.ValidationError({input_name: FormMsg.OPTIONS_FAIL})
            else:
                raise serializers.ValidationError({input_name: FormMsg.OPTIONS_FAIL})
        else:
            raise serializers.ValidationError({input_name: FormMsg.OPTIONS_FAIL})

    is_multiple = serializers.BooleanField(default=False, required=False)

    def manage__valid(self, *args, **kwargs):
        ctx = {
            'input_name': self.manage_input_names[0],
            'input_value': self.manage_input_values[0],
        }
        self.call_m(func=self.manage_required, **ctx)
        self.call_m(func=self.manage_options, **ctx)


class FormCheckboxConfigSerializer(  # noqa
    ConfigVisibility,  # ManageBase
):
    label = serializers.CharField(allow_blank=True, max_length=255)

    @classmethod
    def validate_label(cls, attrs):
        return attrs.strip()

    instruction = serializers.CharField(allow_blank=True)

    @classmethod
    def validate_instruction(cls, attrs):
        return attrs.strip()

    size = serializers.ChoiceField(default='medium', choices=['extra-small', 'small', 'medium', 'large', 'extra-large'])

    checkbox_style = serializers.ChoiceField(default='default', choices=['default', 'switch'])

    init_value = serializers.ChoiceField(default='unchecked', choices=['unchecked', 'checked'])

    def manage__valid(self, *args, **kwargs):
        pass


class CheckboxItemInList(serializers.Serializer):  # noqa
    name = serializers.CharField(max_length=255, required=True)
    label = serializers.CharField(max_length=255, required=True)
    is_default = serializers.BooleanField(default=False)


class FormManyCheckboxConfigSerializer(  # noqa
    ConfigVisibility,  # ManageBase
):
    label = serializers.CharField(allow_blank=True, max_length=255)

    @classmethod
    def validate_label(cls, attrs):
        return attrs.strip()

    instruction = serializers.CharField(allow_blank=True)

    @classmethod
    def validate_instruction(cls, attrs):
        return attrs.strip()

    size = serializers.ChoiceField(default='medium', choices=['extra-small', 'small', 'medium', 'large', 'extra-large'])

    checkbox_style = serializers.ChoiceField(default='default', choices=['default', 'switch'])

    list_checkbox = serializers.ListSerializer(
        child=CheckboxItemInList(), min_length=1, max_length=20,
    )

    def manage__valid(self, *args, **kwargs):
        pass


class FormDateConfigSerializer(  # noqa
    ConfigBase, ConfigRequired, ConfigVisibility,  # ManageBase
):
    init_value_type = serializers.ChoiceField(default='unset', choices=['unset', 'now', 'custom'])
    init_value_custom = serializers.DateField(allow_null=True)
    format = serializers.CharField(default='j F Y')
    min_value = serializers.DateField(allow_null=True)
    max_value = serializers.DateField(allow_null=True)

    @classmethod
    def check_date_string_format(cls, date_text) -> datetime.datetime or False:
        try:
            return datetime.date.fromisoformat(date_text)
        except ValueError:
            pass
        return False

    def errors_general(self):
        errors = {}
        for inp_name in self.manage_input_names:
            errors[inp_name] = FormMsg.DATE_TYPE_NOT_SUPPORT
        return errors

    def manage_date(self, *args, **kwargs):
        errors = {}
        ctx = {
            'input_name': self.manage_input_names[0],
            'input_value': self.manage_input_values[0],
        }
        if not self.check_date_string_format(ctx['input_value']):
            errors[ctx['input_name']] = FormMsg.DATE_FORMAT_INCORRECT
        if errors:
            raise serializers.ValidationError(errors)

    def manage__valid(self, *args, **kwargs):
        ctx = {
            'input_name': self.manage_input_names[0],
            'input_value': self.manage_input_values[0],
        }
        self.call_m(func=self.manage_required, **ctx)
        self.call_m(func=self.manage_date, **ctx)


class FormTimeConfigSerializer(  # noqa
    ConfigBase, ConfigRequired, ConfigVisibility,
):
    init_value_type = serializers.ChoiceField(default='unset', choices=['unset', 'now', 'custom'])
    init_value_custom = serializers.TimeField(allow_null=True)
    format = serializers.CharField(default='H:i')
    min_value = serializers.TimeField(allow_null=True)
    max_value = serializers.TimeField(allow_null=True)

    @classmethod
    def check_time_string_format(cls, date_text) -> datetime.datetime or False:
        try:
            return datetime.time.fromisoformat(date_text)
        except ValueError:
            pass
        return False

    def errors_general(self):
        errors = {}
        for inp_name in self.manage_input_names:
            errors[inp_name] = FormMsg.TIME_TYPE_NOT_SUPPORT
        return errors

    def manage_time(self, *args, **kwargs):
        errors = {}
        ctx = {
            'input_name': self.manage_input_names[0],
            'input_value': self.manage_input_values[0],
        }
        if not self.check_time_string_format(ctx['input_value']):
            errors[ctx['input_name']] = FormMsg.TIME_FORMAT_INCORRECT
        if errors:
            raise serializers.ValidationError(errors)

    def manage__valid(self, *args, **kwargs):
        ctx = {
            'input_name': self.manage_input_names[0],
            'input_value': self.manage_input_values[0],
        }
        self.call_m(func=self.manage_required, **ctx)
        self.call_m(func=self.manage_time, **ctx)


class FormDatetimeConfigSerializer(  # noqa
    ConfigBase, ConfigRequired, ConfigVisibility,  # ManageBase
):
    init_value_type = serializers.ChoiceField(default='unset', choices=['unset', 'now', 'custom'])
    init_value_custom = serializers.DateTimeField(allow_null=True)
    format = serializers.CharField(default='j F Y')
    min_value = serializers.DateTimeField(allow_null=True)
    max_value = serializers.DateTimeField(allow_null=True)

    @classmethod
    def check_datetime_string_format(cls, date_text) -> datetime.datetime or False:
        try:
            return datetime.datetime.fromisoformat(date_text)
        except ValueError:
            pass
        return False

    def errors_general(self):
        errors = {}
        for inp_name in self.manage_input_names:
            errors[inp_name] = FormMsg.DATE_TYPE_NOT_SUPPORT
        return errors

    def manage_datetime(self, *args, **kwargs):
        errors = {}

        def push_errors(key, value):
            if key not in errors:
                errors[key] = value
            elif isinstance(errors[key], list):
                errors[key].append(value)
            else:
                errors[key] = [errors[key], value]

        ctx = {
            'input_name': self.manage_input_names[0],
            'input_value': self.manage_input_values[0],
        }
        current_data = self.check_datetime_string_format(ctx['input_value'])
        if not current_data:
            push_errors(ctx['input_name'], FormMsg.DATE_FORMAT_INCORRECT)
        else:
            if self.manage_configs['min_value']:
                min_data = self.check_datetime_string_format(self.manage_configs['min_value'])
                if min_data and current_data < min_data:
                    push_errors(ctx['input_name'], FormMsg.DATE_LESS_THAN_MIN)
            if self.manage_configs['max_value']:
                max_data = self.check_datetime_string_format(self.manage_configs['max_value'])
                if max_data and current_data > max_data:
                    push_errors(ctx['input_name'], FormMsg.DATE_LARGE_THAN_MAX)
        if errors:
            raise serializers.ValidationError(errors)

    def manage__valid(self, *args, **kwargs):
        ctx = {
            'input_name': self.manage_input_names[0],
            'input_value': self.manage_input_values[0],
        }
        self.call_m(func=self.manage_required, **ctx)
        self.call_m(func=self.manage_datetime, **ctx)


class RatingItemsConfigSerializer(serializers.Serializer):  # noqa
    value = serializers.CharField(max_length=100)
    icon = serializers.CharField(max_length=50)
    color = serializers.CharField(max_length=10)
    review_require = serializers.BooleanField(default=False)
    icon_style = serializers.ChoiceField(default='solid', choices=['solid', 'regular'])


class FormRatingConfigSerializer(  # noqa
    ConfigBase, ConfigRequired, ConfigVisibility
):
    items = serializers.ListSerializer(
        child=RatingItemsConfigSerializer(),
        allow_empty=False, allow_null=False,
        min_length=1,
    )
    isolation_animate = serializers.BooleanField(default=False)

    def _mc__parse_items(self):
        result = {
            'values': [],
            'review_require': [],
        }
        items_arr = self.manage_configs.get('items', [])
        if items_arr and isinstance(items_arr, list):
            for item in items_arr:
                if item and isinstance(item, dict) and 'value' in item:
                    result['values'].append(item['value'])
                    if item.get('review_require', False) is True:
                        result['review_require'].append(item['value'])
        return result

    def manage_rate(self, *args, **kwargs):
        parse_items = self._mc__parse_items()
        if self.manage_input_values[0] not in parse_items['values']:
            raise serializers.ValidationError(
                {
                    self.manage_input_names[0]: FormMsg.RATE_VOTE_NOT_SUPPORT
                }
            )

        if self.manage_input_values[0] in parse_items['review_require']:
            if not self.manage_input_values[1]:
                raise serializers.ValidationError(
                    {
                        self.manage_input_names[1]: FormMsg.RATE_REVIEW_REQUIRE
                    }
                )

    def manage__valid(self, *args, **kwargs):
        ctx = {
            'input_name': self.manage_input_names[0],
            'input_value': self.manage_input_values[0],
        }
        self.call_m(func=self.manage_required, **ctx)
        self.call_m(func=self.manage_rate, **ctx)


class FormCardTextConfigSerializer(  # noqa
    ManageBase
):
    label = serializers.CharField(allow_blank=True, max_length=255)

    @classmethod
    def validate_label(cls, attrs):
        return attrs.strip()

    content = serializers.CharField()

    def validate_content(self, attrs):
        return HTMLController(html_str=attrs).clean(
            trusted_domain=FORM_SANITIZE_TRUSTED_DOMAIN_LINK,
        )

    def manage__valid(self, *args, **kwargs):
        ...


class FormCardHeadingConfigSerializer(  # noqa
    ManageBase,
):
    label = serializers.CharField(allow_blank=True, max_length=255)

    @classmethod
    def validate_label(cls, attrs):
        return attrs.strip()

    instruction = serializers.CharField(allow_blank=True, required=False, default='')

    @classmethod
    def validate_instruction(cls, attrs):
        return attrs.strip()

    def manage__valid(self, *args, **kwargs):
        ...


class FormSliderConfigSerializer(  # noqa
    ConfigBase
):
    init_value = serializers.IntegerField(default=0)
    min_value = serializers.IntegerField(default=0)
    max_value = serializers.IntegerField(default=1)
    unit_prefix = serializers.CharField(default='', allow_blank=True, max_length=25)
    unit_postfix = serializers.CharField(default='', allow_blank=True, max_length=25)
    step = serializers.IntegerField(default=1, min_value=1)
    skin = serializers.ChoiceField(
        default='flat', choices=[
            'flat', 'big', 'modern', 'sharp', 'round', 'square',
        ]
    )

    def manage__valid(self, *args, **kwargs):
        ...


class PageBreakHead(ManageBase):  # noqa
    label = serializers.CharField(allow_blank=True, max_length=100)

    @classmethod
    def validate_label(cls, attrs):
        return attrs.strip()

    show_head = serializers.BooleanField(default=False)


class PageBreakFoot(ManageBase):  # noqa
    is_prev = serializers.BooleanField(default=False)
    is_next = serializers.BooleanField(default=False)
    title_prev = serializers.CharField(max_length=50)
    title_next = serializers.CharField(max_length=50)
    show_page_number = serializers.BooleanField(default=False)
    page_number = serializers.IntegerField(allow_null=True, default=None)
    page_length = serializers.IntegerField(allow_null=True, default=None)


class PageBreakItem(ManageBase):  # noqa
    head = PageBreakHead()
    foot = PageBreakFoot()


class FormPageConfigSerializer(ManageBase):  # noqa
    enabled = serializers.BooleanField(default=False)
    items = serializers.ListSerializer(
        child=PageBreakItem(),
        min_length=0,
        max_length=10,
        allow_empty=True,
    )
    display_page_number = serializers.BooleanField(default=False)
    display_title = serializers.ChoiceField(default='bar', choices=['', 'bar', 'page', 'bar-and-page'])
    justify_progress_item = serializers.ChoiceField(default='around', choices=['around', 'between', 'evenly'])
    progress_style = serializers.ChoiceField(default='steps', choices=['steps', 'proportion', 'bar', 'piece'])
    show_progress_page = serializers.BooleanField(default=False)


class FormPageBreakHeadConfigSerializer(ManageBase):  # noqa
    label = serializers.CharField(allow_blank=True, max_length=100)

    @classmethod
    def validate_label(cls, attrs):
        return attrs.strip()

    head = PageBreakHead()

    foot = PageBreakFoot()

    def manage__valid(self, *args, **kwargs):
        ...


class FormPageBreakFootConfigSerializer(PageBreakFoot):  # noqa
    def manage__valid(self, *args, **kwargs):
        ...

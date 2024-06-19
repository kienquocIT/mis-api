from rest_framework import serializers

SIZE_CHOICES = (
    ('small', 'Small'),
    ('medium', 'Medium'),
    ('large', 'Large'),
)

INPUT_TYPE_CHOICES = (
    ('any-character', 'Any character'),
    ('letters-only', 'Letters only'),
    ('letters-number', 'Letters number'),
    ('letters-number-space', 'Letters number and space'),
    ('letters-space', 'Letters and space'),
    ('custom', 'Customize'),
)

INPUT_TEXT_CASE = (
    ('unset', 'Unset'),
    ('lower', 'Lower'),
    ('upper', 'Upper'),
)


class BaseItem(serializers.Serializer):  # noqa
    label = serializers.CharField(max_length=150, help_text='Label text of group field')
    is_hide_label = serializers.BooleanField(default=False, help_text='Hide/Show label text')
    instruction = serializers.CharField(max_length=250, help_text='Instruction text of input')

    class Meta:
        abstract = True


class BaseSize(serializers.Serializer):  # noqa
    size = serializers.ChoiceField(choices=SIZE_CHOICES)

    @classmethod
    def validate_size(cls, attrs):
        return attrs

    class Meta:
        abstract = True


class BasePlaceHolder(serializers.Serializer):  # noqa
    place_holder = serializers.CharField(max_length=255, allow_blank=True)

    @classmethod
    def validate_place_holder(cls, attrs):
        return attrs

    class Meta:
        abstract = True


class BaseInitValue(serializers.Serializer):  # noqa
    init_value = serializers.CharField(max_length=255, allow_blank=True)

    @classmethod
    def validate_init_value(cls, attrs):
        return attrs

    class Meta:
        abstract = True


class BaseMinMaxLength(serializers.Serializer):  # noqa
    min = serializers.IntegerField(min_value=0, max_value=255)
    max = serializers.IntegerField(min_value=0, max_value=255)

    def validate(self, attrs):
        min_val = attrs.get('min', 0)
        max_val = attrs.get('max', 0)

        if min_val > max_val:
            raise serializers.ValidationError(
                {
                    'min_max': 'The value of min must always be less than or equal to the value of max',
                }
            )
        return attrs

    class Meta:
        abstract = True


class BaseValidation(serializers.Serializer):  # noqa
    required = serializers.BooleanField(default=False)
    unique = serializers.BooleanField(default=False)

    class Meta:
        abstract = True


class BaseVisibility(serializers.Serializer):  # noqa
    hidden = serializers.BooleanField(default=False)
    disabled = serializers.BooleanField(default=False)

    class Meta:
        abstract = True


class BaseInputType(serializers.Serializer):  # noqa
    input_type = serializers.ChoiceField(choices=INPUT_TYPE_CHOICES)
    input_type_value = serializers.CharField(allow_blank=True)
    input_text_case = serializers.ChoiceField(choices=INPUT_TEXT_CASE)

    class Meta:
        abstract = True

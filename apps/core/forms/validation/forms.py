__all__ = ['MATCH_FORM']

from .base import FormItemBaseValidation
from .serializers_form import *  # pylint: disable=W0401,W0614


class FormSingleLineValidation(FormItemBaseValidation):  # noqa
    config = FormSingleLineConfigSerializer()


class FormMultipleLineValidation(FormItemBaseValidation):  # noqa
    config = FormMultipleLineConfigSerializer()


class FormNumberValidation(FormItemBaseValidation):  # noqa
    INPUT_DATA_LENGTH_DEFAULT = 2
    config = FormNumberConfigSerializer()


class FormPhoneValidation(FormItemBaseValidation):  # noqa
    INPUT_DATA_LENGTH_DEFAULT = 2
    config = FormPhoneConfigSerializer()


class FormEmailValidation(FormItemBaseValidation):  # noqa
    config = FormEmailConfigSerializer()


class FormSelectValidation(FormItemBaseValidation):  # noqa
    config = FormSelectConfigSerializer()


class FormCheckboxValidation(FormItemBaseValidation):  # noqa
    config = FormCheckboxConfigSerializer()


class FormManyCheckboxValidation(FormItemBaseValidation):  # noqa
    INPUT_DATA_LENGTH_DEFAULT = None
    config = FormManyCheckboxConfigSerializer()


class FormDateValidation(FormItemBaseValidation):  # noqa
    config = FormDateConfigSerializer()


class FormTimeValidation(FormItemBaseValidation):  # noqa
    config = FormTimeConfigSerializer()


class FormDatetimeValidation(FormItemBaseValidation):  # noqa
    config = FormDatetimeConfigSerializer()


class FormRatingValidation(FormItemBaseValidation):  # noqa
    INPUT_DATA_LENGTH_DEFAULT = 2
    config = FormRatingConfigSerializer()


class FormCardTextValidation(FormItemBaseValidation):  # noqa
    INPUT_DATA_LENGTH_DEFAULT = 0
    config = FormCardTextConfigSerializer()


class FormCardHeadingValidation(FormItemBaseValidation):  # noqa
    INPUT_DATA_LENGTH_DEFAULT = 0
    config = FormCardHeadingConfigSerializer()


class FormSliderValidation(FormItemBaseValidation):  # noqa
    INPUT_DATA_LENGTH_DEFAULT = 1
    config = FormSliderConfigSerializer()


class FormPageValidation(FormItemBaseValidation):  # noqa
    INPUT_DATA_LENGTH_DEFAULT = 0
    config = FormPageConfigSerializer()

class FormPageBreakHeadValidation(FormItemBaseValidation):  # noqa
    INPUT_DATA_LENGTH_DEFAULT = 0
    config = FormPageBreakHeadConfigSerializer()


class FormPageBreakFootValidation(FormItemBaseValidation):  # noqa
    INPUT_DATA_LENGTH_DEFAULT = 0
    config = FormPageBreakFootConfigSerializer()


MATCH_FORM = {
    'single-line': FormSingleLineValidation,
    'multiple-line': FormMultipleLineValidation,
    'number': FormNumberValidation,
    'phone': FormPhoneValidation,
    'email': FormEmailValidation,
    'select': FormSelectValidation,
    'checkbox': FormCheckboxValidation,
    'many-checkbox': FormManyCheckboxValidation,
    'date': FormDateValidation,
    'time': FormTimeValidation,
    'datetime': FormDatetimeValidation,
    'rating': FormRatingValidation,
    'card-text': FormCardTextValidation,
    'card-heading': FormCardHeadingValidation,
    'slider': FormSliderValidation,
    'page-break-head': FormPageBreakHeadValidation,
    'page-break-foot': FormPageBreakFootValidation,
}

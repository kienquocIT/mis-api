__all__ = ['MATCH_FORM']

from .base import FormItemBaseValidation
from .serializers_form import (
    FormSingleLineConfigSerializer,
    FormMultipleLineConfigSerializer,
    FormNumberConfigSerializer,
    FormPhoneConfigSerializer,
    FormEmailConfigSerializer,
)


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


MATCH_FORM = {
    'single-line': FormSingleLineValidation,
    'multiple-line': FormMultipleLineValidation,
    'number': FormNumberValidation,
    'phone': FormPhoneValidation,
    'email': FormEmailValidation,
}

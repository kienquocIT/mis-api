from .base import (
    BaseItem,
    BaseSize, BasePlaceHolder, BaseInitValue, BaseMinMaxLength, BaseValidation,
    BaseVisibility,
    BaseInputType,
)


class SingleLineSerializer(  # noqa
    BaseItem, BaseSize, BasePlaceHolder, BaseInitValue, BaseMinMaxLength, BaseValidation, BaseVisibility, BaseInputType
):
    ...


class MultipleLineSerializer(  # noqa
    BaseItem, BaseSize, BasePlaceHolder, BaseInitValue, BaseMinMaxLength, BaseValidation, BaseVisibility, BaseInputType
):
    ...

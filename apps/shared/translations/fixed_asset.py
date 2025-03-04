from django.utils.translation import gettext_lazy as _


class FixedAssetMsg:
    CODE_EXIST = _('Code already exists')
    ERROR_CREATE = _('Error create asset')
    DESCRIPTION_REQUIRED = _('Description of each source is required')
    TOTAL_VALUE_MUST_MATCH = _('Total value must be equal to the sum of source value')
    DEPRECIATION_MUST_BE_LESS_THAN_COST = _('Depreciation value must be equal or smaller than original cost')
    ASSET_LIST_REQUIRED = _('Asset list is required')
    ASSET_NOT_FOUND = _('Asset is not found')
    ASSET_ALREADY_WRITTEN_OFF = _('Asset is already written off')
    TOOL_LIST_REQUIRED = _('Tool list is required')
    TOOL_NOT_FOUND = _('Tool is not found')
    TOOL_ALREADY_WRITTEN_OFF = _('Tool is already written off')
    WRITEOFF_QUANTITY_INVALID = _('Writeoff quantity is invalid')
    VALUE_MUST_BE_POSITIVE = _('Value must be positive')

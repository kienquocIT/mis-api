from django.utils.translation import gettext_lazy as _


class FixedAssetMsg:
    CODE_EXIST = _('Code already exists')
    ERROR_CREATE = _('Error create asset')
    DESCRIPTION_REQUIRED = _('Description of each source is required')
    TOTAL_VALUE_MUST_MATCH = _('Total value must be equal to the sum of source value')
    DEPRECIATION_MUST_BE_LESS_THAN_COST = _('Depreciation value must be equal or smaller than original cost')
    ASSET_LIST_REQUIRED = _('Asset list is required')

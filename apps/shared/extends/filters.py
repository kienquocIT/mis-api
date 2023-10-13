from copy import deepcopy

import django_filters

from django_filters.rest_framework import filters

__all__ = ['BastionFieldAbstractListFilter']

from .utils import TypeCheck
from ..constant import KEY_GET_LIST_FROM_APP, SPLIT_CODE_FROM_APP, KEY_GET_LIST_FROM_OPP


class BastionFieldAbstractListFilter(django_filters.FilterSet):
    list_from_app = filters.CharFilter(method='filter_list_from_app')
    list_from_opp = filters.UUIDFilter(method='filter_list_from_opp_and_prj')
    list_from_prj = filters.UUIDFilter(method='filter_list_from_opp_and_prj')

    def __init__(self, *args, **kwargs):
        old_fields = self.Meta.fields
        if isinstance(old_fields, (list, tuple)):
            old_fields_convert = list(deepcopy(old_fields))
            if KEY_GET_LIST_FROM_APP not in old_fields_convert:
                old_fields_convert += (KEY_GET_LIST_FROM_APP, )
            if KEY_GET_LIST_FROM_OPP not in old_fields_convert:
                old_fields_convert += (KEY_GET_LIST_FROM_OPP,)
            old_fields = old_fields_convert
        elif isinstance(old_fields, dict):
            old_fields_convert = dict(deepcopy(old_fields))
            if KEY_GET_LIST_FROM_APP not in old_fields.keys():
                old_fields_convert[KEY_GET_LIST_FROM_APP] = {'list_from_app': ['exact']}
                old_fields_convert[KEY_GET_LIST_FROM_OPP] = {'list_from_opp': ['exact']}
            old_fields = old_fields_convert
        else:
            raise ValueError(f'Config fields in "{str(self.__class__.__name__)}" not support!')

        setattr(self.Meta, 'fields', old_fields)
        super().__init__(*args, **kwargs)

    class Meta:
        fields: tuple or dict = None
        abstract = True

    @classmethod
    def filter_list_from_app(cls, queryset, name, value):  # pylint: disable=W0613
        if value and isinstance(value, str) and len(value) > 3 and SPLIT_CODE_FROM_APP in value:
            arr = value.split(SPLIT_CODE_FROM_APP)
            if arr and len(arr) == 3:
                return queryset
        return queryset.none()

    @classmethod
    def filter_list_from_opp_and_prj(cls, queryset, name, value):   # pylint: disable=W0613
        if value and TypeCheck.check_uuid(value):
            return queryset
        return queryset.none()

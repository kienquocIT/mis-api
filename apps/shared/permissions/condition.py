from typing import Literal

from django.db.models import Q

OPERATOR_TYPE = Literal['and', 'or']  # pylint: disable=C0103
DATA_CHILD_TYPE = dict[str, any]  # pylint: disable=C0103

__all__ = [
    'FilterComponent',
    'FilterComponentList',
]


class FilterComponent:
    _data = None

    @property
    def data(self):
        if self._data is None:
            self._data = {
                'main_data': self.main_data,
                'logic_next': self.logic_next,
                'sub': [
                    item.data for item in self.sub
                ],
                'logic_sub': self.logic_sub
            }
        return self._data

    _django_q = None

    @property
    def django_q(self) -> Q:
        if self._django_q is None:
            sub_q = Q()
            opr_prev = 'and'
            for sub_item in self.sub:
                if opr_prev == 'and':
                    sub_q &= sub_item.django_q
                elif opr_prev == 'or':
                    sub_q |= sub_item.django_q

                opr_prev = sub_item.logic_next

            if self.logic_sub == 'and':
                self._django_q = Q(**self.main_data) & sub_q
            elif self.logic_sub == 'or':
                self._django_q = Q(**self.main_data) | sub_q
            else:
                self._django_q = Q(**self.main_data)

        return self._django_q

    def __init__(self, main_data: DATA_CHILD_TYPE, logic_next, sub=None, logic_sub: OPERATOR_TYPE = None):
        self.main_data = main_data
        self.logic_next = logic_next
        self._sub = sub if isinstance(sub, list) else []
        self.logic_sub = logic_sub

        self.sub = []
        if self.logic_sub:
            for item in self._sub:
                self.sub.append(FilterComponent(**item))


class FilterComponentList:
    _data = None

    @property
    def data(self):
        if self._data is None:
            self._data = [
                item.data for item in self.main_data
            ]
        return self._data

    _django_q = None

    @property
    def django_q(self) -> Q:
        if self._django_q is None:
            sub_q = Q()
            opr_prev = 'and'
            for sub_item in self.main_data:
                if opr_prev == 'and':
                    sub_q &= sub_item.django_q
                elif opr_prev == 'or':
                    sub_q |= sub_item.django_q

                opr_prev = sub_item.logic_next

            self._django_q = sub_q

        return self._django_q

    def __init__(self, main_data: list[FilterComponent]):
        self.main_data = main_data

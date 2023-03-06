from django_filters import rest_framework as filters

from apps.core.hr.models import Group


class GroupListFilter(filters.FilterSet):
    parent_level = filters.CharFilter(method="filter_parent_level")

    @classmethod
    def filter_parent_level(cls, queryset, key, value): # pylint: disable=W0613
        if value:
            return queryset.filter(group_level__level__lt=int(value))
        return queryset.none()

    class Meta:
        model = Group
        fields = (
            "group_level__level",
            "parent_level"
        )

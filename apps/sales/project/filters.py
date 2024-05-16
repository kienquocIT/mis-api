__all__ = ['ProjectGroupListFilter']

from django_filters.rest_framework import filters  # noqa
from rest_framework import exceptions

from django.db.models import Q

from apps.sales.project.models import ProjectGroups
from apps.shared import BastionFieldAbstractListFilter


class ProjectGroupListFilter(BastionFieldAbstractListFilter):
    project = filters.CharFilter(
        method='filter_by_project', field_name='project'
    )

    class Meta:
        model = ProjectGroups
        fields = {
            'id': ['exact', 'in']
        }

    def filter_by_project(self, queryset, name, value):
        user_obj = getattr(self.request, 'user', None)
        request_params = self.request.query_params.dict()
        if user_obj:
            filter_kwargs = Q()
            if 'project' in request_params:
                filter_kwargs &= Q(**{'project_projectmapgroup_project__id': request_params['project']})
            if filter_kwargs is not None:
                return queryset.filter(filter_kwargs)
            return queryset
        raise exceptions.AuthenticationFailed

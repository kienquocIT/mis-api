__all__ = ['ProjectGroupListFilter']

import django_filters
from django.db import models
from django.db.models import Q
from django_filters.rest_framework import filters

from rest_framework import exceptions

from apps.sales.project.models import ProjectGroups, ProjectNewsComment
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

    def filter_by_project(self, queryset):
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


class ProjectNewsCommentListFilter(django_filters.FilterSet):
    class Meta:
        model = ProjectNewsComment
        fields = {
            'news_id': ['exact', 'in'],
            'employee_inherit_id': ['exact', 'in'],
            'reply_from_id': ['exact', 'in', 'isnull'],
            'mentions': ['contains'],
        }
        filter_overrides = {
            models.JSONField: {
                'filter_class': django_filters.CharFilter,
            },
        }

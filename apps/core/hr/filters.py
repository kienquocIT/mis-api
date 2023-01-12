# from django_filters import rest_framework as filters
#
#
# class EmployeeUserByCompanyOverviewDetailFilter(filters.FilterSet):
#     # 1: all user and employee
#     # 1: employee linked user
#     option_display = filters.ChoiceFilter(choices=[1, 2], method='filter_all_user_and_employee')
#
#     @classmethod
#     def filter_all_user_and_employee(cls, queryset, name, value):
#         return queryset

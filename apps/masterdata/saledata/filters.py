__all__ = [
    'AccountListFilter', 'ProductWareHouseListFilter'
]
import django_filters
from django.db.models import Q
from django_filters.rest_framework import filters
from rest_framework import exceptions

from apps.shared import TypeCheck, EmployeeAttribute, DisperseModel
from .models import Account, ProductWareHouse



class AccountListFilter(django_filters.FilterSet):
    manager__contains = filters.CharFilter(method='filter_manager__contains', field_name='manager__contains')
    has_manager_custom = filters.CharFilter(method='filter_has_manager_custom', field_name='manager__contains')

    class Meta:
        model = Account
        fields = (
            'account_types_mapped__account_type_order',
        )

    @classmethod
    def filter_manager__contains(cls, queryset, name, value):
        if value:
            ids = value.split(',')
            if TypeCheck.check_uuid_list(ids):
                filter_kwargs = Q()
                for idx in ids:
                    filter_kwargs |= Q(**{name: {'id': idx}})
                return queryset.filter(filter_kwargs)
        return queryset

    def filter_has_manager_custom(self, queryset, name, value):
        user_obj = getattr(self.request, 'user', None)
        if user_obj:
            if value and value != 'all':
                employee_current = getattr(self.request.user, 'employee_current', None)
                if employee_current:
                    if value == 'me':
                        return queryset.filter(**{name: {'id': str(employee_current.id)}})

                    filter_q = Q()
                    if value == 'same':
                        employee_ids = EmployeeAttribute(
                            employee_obj=employee_current, is_append_me=True
                        ).employee_same_group_ids
                        for employee_id in employee_ids:
                            filter_q |= Q(**{name: {'id': employee_id}})
                    elif value == 'staff':
                        employee_ids = EmployeeAttribute(
                            employee_obj=employee_current, is_append_me=True
                        ).employee_staff_ids
                        for employee_id in employee_ids:
                            filter_q |= Q(**{name: {'id': employee_id}})

                    if filter_q:
                        return queryset.filter(filter_q)
                return queryset.none()
            return queryset
        raise exceptions.AuthenticationFailed


class ProductWareHouseListFilter(django_filters.FilterSet):
    is_asset = filters.CharFilter(
        method='filter_is_asset', field_name='is_asset'
    )

    class Meta:
        model = ProductWareHouse
        fields = {
            'product_id': ['exact'],
            'warehouse_id': ['exact']
        }

    def filter_is_asset(self, queryset, name, value):  # pylint: disable=W0613  # noqa
        user_obj = getattr(self.request, 'user', None) # noqa
        params = self.request.query_params.dict()
        if user_obj:
            filter_kwargs = Q()
            if 'product_id' in params:
                filter_kwargs &= Q(**{'product_id': params['product_id']})
            if 'is_asset' in params:
                asset_config = DisperseModel(app_model='assettools.AssetToolsConfig').get_model().objects.filter(
                    company_id=user_obj.company_current_id,
                )
                product_type = str(asset_config.first().product_type.id)
                warehouses = asset_config.first().asset_config_warehouse_map_asset_config.all()
                product_warehouse = [str(warehouse.warehouse.id) for warehouse in warehouses]
                # check admin list
                asset_admin_list = asset_config.first().asset_config_employee_map_asset_config.all()
                is_authen = False
                if user_obj.employee_current and asset_admin_list:
                    for item in asset_admin_list:
                        if item.employee == user_obj.employee_current:
                            is_authen = True
                            break
                if not is_authen:
                    raise exceptions.PermissionDenied
                filter_kwargs &= (Q(product__general_product_types_mapped__id=product_type) & Q(
                    warehouse__id__in=product_warehouse
                ))
            if filter_kwargs is not None:
                return queryset.filter(filter_kwargs)
            return queryset
        raise exceptions.AuthenticationFailed

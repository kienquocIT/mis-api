from collections import OrderedDict

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from unidecode import unidecode
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema

from apps.core.base.filters import ApplicationPropertiesListFilter
from apps.shared import ResponseController, BaseListMixin, mask_view, BaseRetrieveMixin
from apps.core.base.models import (
    SubscriptionPlan, Application, ApplicationProperty, PermissionApplication,
    Country, City, District, Ward, Currency as BaseCurrency, BaseItemUnit, IndicatorParam, PlanApplication
)

from apps.core.base.serializers import (
    PlanListSerializer, ApplicationListSerializer, ApplicationPropertyListSerializer,
    PermissionApplicationListSerializer,
    CountryListSerializer, CityListSerializer, DistrictListSerializer, WardListSerializer, BaseCurrencyListSerializer,
    BaseItemUnitListSerializer, IndicatorParamListSerializer, ApplicationPropertyForPrintListSerializer,
    ApplicationPropertyForMailListSerializer,
)


class PlanList(generics.GenericAPIView):
    queryset = SubscriptionPlan.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        "id": ["in"],
        "code": ["exact", "in"],
    }

    serializer_class = PlanListSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related('applications')

    @swagger_auto_schema(
        operation_summary="Plan list",
        operation_description="Get plan list",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter()).cache(timeout=1440)  # cache 1 days | 1440 minutes
        ser = self.serializer_class(queryset, many=True)
        return ResponseController.success_200(ser.data, key_data='result')


class TenantApplicationList(BaseListMixin):
    queryset = Application.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'code': ['exact'],
        'title': ['exact'],
        'is_workflow': ['exact'],
        'allow_import': ['exact'],
        'allow_print': ['exact'],
        'allow_mail': ['exact'],
    }
    serializer_list = ApplicationListSerializer
    list_hidden_field = []

    def get_queryset(self):
        if not isinstance(self.request.user, AnonymousUser) and getattr(self.request.user, 'tenant_current', None):
            return super().get_queryset().filter(
                id__in=PlanApplication.objects.filter(
                    plan_id__in=self.request.user.tenant_current.tenant_plan_tenant.values_list('plan__id', flat=True)
                ).values_list('application__id', flat=True)
            )
        return Application.objects.none()

    def get_serializer_list_data(self, ser_data):
        if not self.check_page_size():
            # auto apply will be to manual
            # - search : support Tone marks and Slugify
            # - order : support key exist return and reversed with "-" first character

            search_txt = self.request.query_params.get('search', None)
            if search_txt:
                search_txt = search_txt.lower()

                def filter_title_has_search(obj):
                    tmp = dict(OrderedDict(obj))
                    return (
                            search_txt in tmp['title'].lower()
                            or unidecode(search_txt) in unidecode(tmp['title'].lower())
                    )

                ser_data = list(filter(filter_title_has_search, ser_data))

            order_txt = self.request.query_params.get('ordering', 'title')
            if order_txt:
                key_order, reverse_order = order_txt, False
                if order_txt.startswith('-'):
                    key_order = key_order[1:]
                    reverse_order = True
                try:
                    ser_data = sorted(ser_data, key=lambda item: unidecode(item[key_order]), reverse=reverse_order)
                except KeyError:
                    pass

            return ser_data
        return ser_data

    def check_page_size(self):
        page_size = self.request.query_params.get('pageSize', None)
        if page_size in ('-1', -1):
            return False
        return True

    @swagger_auto_schema(
        operation_summary="Tenant Application list",
        operation_description="Get tenant application list",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        if not self.check_page_size():
            self.search_fields = []
        return self.list(request, *args, **kwargs)


class ApplicationDetail(BaseRetrieveMixin):
    queryset = Application.objects
    serializer_detail = ApplicationListSerializer

    @swagger_auto_schema(
        operation_summary="Tenant Application detail",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)


class ApplicationPropertyList(BaseListMixin):
    queryset = ApplicationProperty.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        'application': ['exact', 'in'],
        'type': ['exact'],
        'id': ['in'],
        'application__code': ['exact'],
        'is_sale_indicator': ['exact'],
        'parent_n': ['exact', 'isnull'],
        'is_print': ['exact'],
        'is_mail': ['exact'],
    }
    serializer_list = ApplicationPropertyListSerializer

    @swagger_auto_schema(operation_summary="Application Property list", operation_description="")
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ApplicationPropertyForPrintList(BaseListMixin):
    queryset = ApplicationProperty.objects
    search_fields = ['code', 'title_slug']
    filterset_class = ApplicationPropertiesListFilter
    serializer_list = ApplicationPropertyForPrintListSerializer

    def get_queryset(self):
        return super().get_queryset().filter(is_print=True)

    @swagger_auto_schema(operation_summary="Application Property list for Print", operation_description="")
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ApplicationPropertyForMailList(BaseListMixin):
    queryset = ApplicationProperty.objects
    search_fields = ['code', 'title_slug']
    filterset_class = ApplicationPropertiesListFilter
    serializer_list = ApplicationPropertyForMailListSerializer

    def get_queryset(self):
        query_params = self.request.query_params
        system_code__is_null_or_value = query_params.get('system_code__is_null_or_value', None)
        system_code__exact = query_params.get('system_code', None)
        system_code__isnull = query_params.get('system_code__isnull', None)
        if not (
                system_code__is_null_or_value is not None
                or system_code__exact is not None
                or system_code__isnull is not None
        ):
            return super().get_queryset().filter(is_mail=True, system_code__isnull=True)
        return super().get_queryset().filter(is_mail=True)

    @swagger_auto_schema(operation_summary="Application Property list for Mail", operation_description="")
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ApplicationPropertyEmployeeList(BaseListMixin):
    queryset = ApplicationProperty.objects
    serializer_list = ApplicationPropertyListSerializer
    list_hidden_field = []
    search_fields = ('title', 'code')
    filterset_fields = ('code', 'title')

    def get_queryset(self):
        return super().get_queryset().filter(
            content_type="hr_employee"
        )

    @swagger_auto_schema(
        operation_summary="Property list have employee data",
        operation_description="Property list have employee data",
    )
    @mask_view(
        login_require=True,
        auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ApplicationList(generics.GenericAPIView):
    queryset = Application.objects
    search_fields = ('title', 'code',)
    serializer_class = ApplicationListSerializer

    @swagger_auto_schema()
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter()).cache(timeout=1440)  # cache 1 days | 1440 minutes
        ser = self.serializer_class(queryset, many=True)
        return ResponseController.success_200(ser.data, key_data='result')


class PermissionApplicationList(generics.GenericAPIView):
    queryset = PermissionApplication.objects
    search_fields = ('permission', 'app__title', 'app__code',)
    filterset_fields = {
        'app_id': ['exact', 'in'],
        'app__code': ['exact', 'in'],
    }
    serializer_class = PermissionApplicationListSerializer

    def get_queryset(self):
        return super().get_queryset().select_related("app")

    @swagger_auto_schema(
        operation_summary="Plan list",
        operation_description="Get plan list",
    )
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter()).cache(timeout=1440)  # cache 1 days | 1440 minutes
        ser = self.serializer_class(queryset, many=True)
        return ResponseController.success_200(ser.data, key_data='result')


# Viet Nam data
class CountryList(BaseListMixin):
    queryset = Country.objects
    search_fields = ['title', 'code_2', 'code_3']
    use_cache_queryset = True
    serializer_list = CountryListSerializer

    @swagger_auto_schema()
    @mask_view(login_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CityList(BaseListMixin):
    queryset = City.objects
    search_fields = ('title', 'short_search', 'zip_code')
    filterset_fields = {
        "country_id": ["exact", "in"],
        "id": ["exact", "in"],
    }
    use_cache_queryset = True
    serializer_list = CityListSerializer

    @swagger_auto_schema()
    @mask_view(login_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DistrictList(BaseListMixin):
    queryset = District.objects
    search_fields = ('title',)
    filterset_fields = {
        "city_id": ["exact", "in"],
        "id": ["exact", "in"],
    }
    use_cache_queryset = True
    serializer_list = DistrictListSerializer

    @swagger_auto_schema()
    @mask_view(login_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class WardList(BaseListMixin):
    queryset = Ward.objects
    search_fields = ('title',)
    filterset_fields = {
        "district_id": ["exact", "in"],
    }
    use_cache_queryset = True
    serializer_list = WardListSerializer

    @swagger_auto_schema()
    @mask_view(login_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BaseCurrencyList(BaseListMixin):
    queryset = BaseCurrency.objects
    search_fields = ('title', 'code')
    use_cache_queryset = True
    serializer_list = BaseCurrencyListSerializer

    @swagger_auto_schema()
    @mask_view(login_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BaseItemUnitList(BaseListMixin):
    queryset = BaseItemUnit.objects
    search_fields = ('title', 'measure')
    filterset_fields = ('title', 'measure')
    use_cache_queryset = True
    serializer_list = BaseItemUnitListSerializer

    @swagger_auto_schema()
    @mask_view(login_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class IndicatorParamList(BaseListMixin):
    queryset = IndicatorParam.objects
    search_fields = ['title', 'code']
    filterset_fields = {
        "param_type": ["exact"],
    }
    use_cache_queryset = True
    serializer_list = IndicatorParamListSerializer

    @swagger_auto_schema()
    @mask_view(login_require=False)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ApplicationPropertyOpportunityList(BaseListMixin):
    queryset = ApplicationProperty.objects
    serializer_list = ApplicationPropertyListSerializer
    list_hidden_field = []

    def get_queryset(self):
        return super().get_queryset().filter(
            content_type="sales_opportunity"
        )

    @swagger_auto_schema(
        operation_summary="Property list have Opportunity config stage data",
        operation_description="Property list have Opportunity config stage data",
    )
    @mask_view(
        login_require=True,
        auth_require=False
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

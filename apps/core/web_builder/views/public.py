from rest_framework.generics import GenericAPIView

from apps.core.company.models import Company
from apps.core.web_builder.serializers.public.products import PublicProductListSerializer
from apps.masterdata.saledata.models import Product

from apps.shared import mask_view, ResponseController


class PublicProductListAPI(GenericAPIView):
    queryset = Product.objects
    serializer_class = PublicProductListSerializer
    search_fields = ('title', 'description')

    @mask_view(login_require=False, auth_require=False)
    def get(self, request, *args, company_sub_domain, **kwargs):
        try:
            company_obj = Company.objects.get(sub_domain=company_sub_domain)
        except Company.DoesNotExist:
            return ResponseController.notfound_404()

        queryset = self.filter_queryset(
            self.queryset.filter(company=company_obj, product_choice__contains=0, is_public_website=True)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True)
        return ResponseController.success_200(data=serializer.data, key_data='result')

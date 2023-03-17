from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from .response import cus_response


class CustomResultsSetPagination(PageNumberPagination):
    page_size_query_param = "pageSize"
    page_size_query_description = ("page_size_query_description (value -1 with get not page).",)

    def get_page_size(self, request):
        page_size_int = self.page_size
        page_size_str = request.query_params.get(self.page_size_query_param, str(page_size_int))
        try:
            page_size_int = int(page_size_str)
        except (KeyError, ValueError):
            pass
        if page_size_int == -1:
            return None
        return self.positive_int(page_size_str, strict=True, cutoff=self.max_page_size)

    def get_paginated_response(self, data):
        return cus_response(
            {
                "next": self.page.next_page_number() if self.page.has_next() else 0,
                "previous": self.page.previous_page_number() if self.page.has_previous() else 0,
                "count": self.page.paginator.count,
                "page_size": self.page.paginator.per_page,  # self.page_size,
                "result": data,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def positive_int(integer_string, strict=False, cutoff=None):
        """
        Cast a string to a strictly positive integer.
        """
        ret = int(integer_string)
        if ret < 0 or (ret == 0 and strict):
            raise ValueError()
        if cutoff:
            return min(ret, cutoff)
        return ret

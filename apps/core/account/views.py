from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from apps.core.account.mixins import AccountListMixin, AccountCreateMixin
from apps.core.account.models import User
from apps.core.account.serializers import UserListSerializer
from apps.shared import ResponseController


class UserList(
    AccountListMixin,
    AccountCreateMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.select_related(
        "tenant_current",
    )
    search_fields = ["full_name_search"]

    serializer_class = UserListSerializer

    @swagger_auto_schema(
        operation_summary="User list",
        operation_description="Get user list",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create user",
        operation_description="Create a new user",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
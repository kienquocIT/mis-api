from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.shared import ResponseController


class UserList(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema()
    def get(self, request, *args, **kwargs):
        # user_list = SerUser(userobjs, many=True).data
        return ResponseController.success_200(data=[], key_data='result')
    # {
    #     'result': user_list
    # }
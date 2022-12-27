from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from apps.shared.controllers import ResponseController
from apps.core.auths.serializers import AuthLoginSerializer, MyTokenObtainPairSerializer
from apps.shared.translations import AuthMsg


# LOGIN:
# - get user (filter by tenant code)
# - get tenant
# - get company current
# - get employee current
# - get space current
#
#
# GET MENU:
# - get current: tenant, company, space, employee
# - get menus: from application of Employee-Space
# -
class AuthLogin(generics.GenericAPIView):
    permission_classes = [AllowAny]

    serializer_class = AuthLoginSerializer

    @swagger_auto_schema(
        operation_summary='Authenticated with username and password',
        operation_description='',
        request_body=AuthLoginSerializer
    )
    def post(self, request, *args, **kwargs):
        # validate username and password
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        # get user object from serializer
        user_obj = ser.validated_data
        if user_obj:
            # generate token
            generate_token = MyTokenObtainPairSerializer.get_full_token(user_obj)
            token_data = {
                'access_token': generate_token['access'],
                'refresh_token': generate_token['refresh']
            }

            result = user_obj.get_detail()
            result['token'] = token_data

            # append user detail to result , then return response
            return ResponseController.success_200(result, key_data='result')
        return ResponseController.bad_request_400(AuthMsg.USERNAME_OR_PASSWORD_INCORRECT)


class AuthRefreshLogin(generics.GenericAPIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary='Refresh Token by key',
        request_body=TokenRefreshSerializer
    )
    def post(self, request, *args, **kwargs):
        ser = TokenRefreshSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        token = ser.validated_data

        if token:
            return ResponseController.success_200({'access_token': str(token['access'])}, key_data='result')
        return ResponseController.bad_request_400({'detail': 'Refresh is failure.'})


class MyProfile(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary='Get My Profile')
    def get(self, request, *args, **kwargs):
        return ResponseController.success_200(data={'data': request.user.get_detail()}, key_data='result')

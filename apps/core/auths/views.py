from datetime import timedelta, datetime
from typing import Union

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.utils import translation, timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from apps.core.account.models import User, ValidateUser
from apps.core.auths.serializers import (
    AuthLoginSerializer, MyTokenObtainPairSerializer, SwitchCompanySerializer,
    MyLanguageUpdateSerializer, ChangePasswordSerializer, ForgotPasswordGetOTPSerializer,
    ValidateUserDetailSerializer, SubmitOTPSerializer,
)
from apps.shared import (
    mask_view, ResponseController, AuthMsg, HttpMsg, DisperseModel, TypeCheck, FORMATTING, Caching,
)
from misapi.mongo_client import mongo_log_auth, MongoViewParse


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

    @classmethod
    def force_company_currently(cls, user_obj: User) -> tuple[User, Union[None, models.Model], bool, list[str]]:
        model_cls = DisperseModel(app_model='company.companyuseremployee').get_model()
        if not user_obj.company_current_id:
            company_user_emp = model_cls.objects.filter(
                **
                (
                    {
                        'user_id': user_obj.id,
                        'employee_id': user_obj.employee_current_id,
                    }
                    if user_obj.employee_current_id
                    else {
                        'user_id': user_obj.id,
                    }
                )
            )

            if company_user_emp.count() > 0:
                obj_first = company_user_emp.first()
                user_obj.company_current_id = obj_first.company_id
                return user_obj, obj_first, True, ['company_current_id']

        if user_obj.company_current_id:
            company_user_emp = model_cls.objects.filter(user_id=user_obj.id, company_id=user_obj.company_current_id)
            if company_user_emp.count() > 0:
                obj_first = company_user_emp.first()
                return user_obj, obj_first, True, ['company_current_id']
            user_obj.company_current_id = None
            user_obj.employee_current_id = None
            return user_obj, None, True, ['company_current_id', 'employee_current_id']

        user_obj.company_current_id = None
        user_obj.employee_current_id = None
        return user_obj, None, True, ['company_current_id', 'employee_current_id']

    @classmethod
    def force_employee_currently(cls, user_obj: User, company_user_emp_obj: models.Model = None) -> list[str]:
        if company_user_emp_obj:
            if hasattr(company_user_emp_obj, 'employee_id'):
                user_obj.employee_current_id = company_user_emp_obj.employee_id
                return ['employee_current_id']
            user_obj.employee_current_id = None
            return ['employee_current_id']
        emp_objs = DisperseModel(app_model='hr.employee').get_model().objects.filter(
            company_id=user_obj.company_current_id,
            user_id=user_obj.id,
        )
        if emp_objs.count() > 0:
            user_obj.employee_current_id = emp_objs.first().id
            return ['employee_current_id']
        user_obj.employee_current_id = None
        return ['employee_current_id']

    @classmethod
    def check_and_update_globe(cls, user_obj: User):
        user_obj, company_user_emp_obj, exist_company, update_fields = cls.force_company_currently(user_obj=user_obj)
        if exist_company:
            update_fields += cls.force_employee_currently(user_obj=user_obj, company_user_emp_obj=company_user_emp_obj)
        if update_fields:
            user_obj.save(update_fields=update_fields)
        return user_obj

    @swagger_auto_schema(
        operation_summary='Authenticated with username and password',
        operation_description='',
        request_body=AuthLoginSerializer
    )
    def post(self, request, *args, **kwargs):
        # active translate vietnamese default
        translation.activate('vi')

        # validate username and password
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        # get user object from serializer
        user_obj = ser.validated_data
        if user_obj:
            if user_obj.auth_locked_out is True:
                return ResponseController.bad_request_400(AuthMsg.USER_WAS_LOCKED_OUT)

            # info employee_id, space_id make sure correct
            self.check_and_update_globe(user_obj)

            user_detail = user_obj.get_detail()
            if user_obj.auth_2fa is True:
                result = {
                    'token': MyTokenObtainPairSerializer.get_pre_2fa_token(user=user_obj),
                    **user_detail,
                }
            else:
                result = {
                    'token': MyTokenObtainPairSerializer.get_full_token(user=user_obj, is_verified=False),
                    **user_detail,
                }
            mongo_log_auth.insert_one(
                metadata=mongo_log_auth.metadata(user_id=str(user_obj.id)),
                endpoint="LOGIN",
                return_type="PRE_2FA_TOKEN" if user_obj.auth_2fa is True else "FULL_TOKEN",
            )
            return ResponseController.success_200(result, key_data='result')
        return ResponseController.bad_request_400(AuthMsg.USERNAME_OR_PASSWORD_INCORRECT)


class AuthLogout(APIView):
    @swagger_auto_schema(operation_summary='User logout')
    @mask_view(login_require=True)
    def delete(self, request, *args, **kwargs):
        # records user sign-out in device
        # if integrate device accept call:
        #   -> remove device from allowed_devices
        # else: nothing was destroyed
        access_token = getattr(request, 'auth', None)
        if not isinstance(access_token, AccessToken):
            return ResponseController.unauthorized_401()
        try:
            refresh_token_str = request.headers.get(settings.SIMPLE_JWT['AUTH_HEADER_NAME_REFRESH_TOKEN'])
            refresh_token = RefreshToken(refresh_token_str)
        except Exception as errs:  # pylint: disable=W0612
            return ResponseController.bad_request_400({
                'refresh_token': AuthMsg.LOGOUT_REQUIRE_REFRESH_TOKEN
            })
        refresh_token.blacklist()
        mongo_log_auth.insert_one(
            metadata=mongo_log_auth.metadata(user_id=str(request.user.id)),
            endpoint="LOGOUT",
        )
        return ResponseController.no_content_204()


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
    @swagger_auto_schema(operation_summary='Get My Profile')
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        obj = User.objects.select_related(
            'tenant_current', 'company_current', 'space_current', 'employee_current',
        ).get(pk=request.user.id)
        return ResponseController.success_200(data={'data': obj.get_detail()}, key_data='result')


class AliveCheckView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_summary='Check session is alive')
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        user = request.user
        if not user or user.is_authenticated is False or user.is_anonymous is True:
            return ResponseController.unauthorized_401()
        return ResponseController.success_200(data={'state': 'You are still alive.'}, key_data='result')


class SwitchCompanyView(APIView):
    @swagger_auto_schema(operation_summary='Switch Currently Company', request_body=SwitchCompanySerializer)
    @mask_view(login_require=True)
    def put(self, request, *args, **kwargs):
        user_obj = request.user
        if user_obj and hasattr(user_obj, 'switch_company'):
            ser = SwitchCompanySerializer(data=request.data, context={'user_obj': request.user})
            ser.is_valid(raise_exception=True)
            user_obj.switch_company(ser.validated_data['company_user_employee'])
            return ResponseController.success_200(
                {'detail': f'{HttpMsg.SUCCESSFULLY}. {HttpMsg.GOTO_LOGIN}'},
                key_data='result'
            )
        return ResponseController.unauthorized_401()


class MyLanguageView(APIView):
    @swagger_auto_schema(operation_summary='Change my language', request_body=MyLanguageUpdateSerializer)
    @mask_view(login_require=True)
    def put(self, request, *args, **kwargs):
        user_obj = request.user
        if user_obj and hasattr(user_obj, 'id') and not isinstance(user_obj, AnonymousUser):
            language = request.data.get('language', None)
            ser = MyLanguageUpdateSerializer(
                data={
                    'language': language
                }, partial=True
            )
            ser.is_valid(raise_exception=True)

            user_obj.language = language
            user_obj.save()
            return ResponseController.success_200({'detail': HttpMsg.SUCCESSFULLY}, key_data='result')
        return ResponseController.unauthorized_401()


class ChangePasswordView(APIView):
    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    @mask_view(login_require=True)
    def put(self, request, *args, **kwargs):
        user_obj = request.user
        if user_obj and hasattr(user_obj, 'id') and not isinstance(user_obj, AnonymousUser):
            ser = ChangePasswordSerializer(instance=user_obj, data=request.data)
            ser.is_valid(raise_exception=True)
            ser.save()
            return ResponseController.success_200({'detail': HttpMsg.SUCCESSFULLY}, key_data='result')
        return ResponseController.unauthorized_401()


class ForgotPasswordView(APIView):
    @swagger_auto_schema(request_body=ForgotPasswordGetOTPSerializer)
    @mask_view(login_require=False)
    def post(self, request, *args, **kwargs):
        ser = ForgotPasswordGetOTPSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        obj.send_otp_to_telegram()
        return ResponseController.success_200(data=ValidateUserDetailSerializer(instance=obj).data)


class ForgotPasswordDetailView(APIView):
    @swagger_auto_schema(operation_summary='Call re-sent OTP')
    @mask_view(login_require=False)
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            try:
                obj = ValidateUser.objects.get(pk=pk)
            except ValidateUser.DoesNotExist:
                return ResponseController.notfound_404()

            obj.otp = ValidateUser.generate_otp()
            obj.save(update_fields=['otp'])
            obj.send_otp_to_telegram()
            return ResponseController.success_200(data={'': 'Ok'})
        return ResponseController.notfound_404()

    @swagger_auto_schema(request_body=SubmitOTPSerializer)
    @mask_view(login_require=False)
    def put(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            try:
                obj = ValidateUser.objects.get(pk=pk, is_valid=False)
            except ValidateUser.DoesNotExist:
                return ResponseController.notfound_404()

            if obj.date_expires >= timezone.now():
                ser = SubmitOTPSerializer(instance=obj, data=request.data)
                ser.is_valid(raise_exception=True)
                ser.save()
                new_password = obj.user.generate_new_password()
                return ResponseController.success_200(data={'new_password': new_password})
            raise serializers.ValidationError({'': AuthMsg.VALIDATE_OTP_EXPIRED})
        return ResponseController.notfound_404()


class AuthLogsView(APIView):
    @swagger_auto_schema(operation_summary="Get log of user's authentication")
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
            view_parse = MongoViewParse(request=request)
            page_size = view_parse.get_page_size()
            page_index = view_parse.get_page_index()
            record_skip = page_size * (page_index - 1)
            ordering = view_parse.get_ordering(
                default_data={
                    'timestamp': -1,
                }
            )
            filter_data = {
                'metadata.service_name': 'AUTH',
                'metadata.user_id': str(request.user.id),
            }
            count = mongo_log_auth.count_documents(filter_data)
            queries = mongo_log_auth.find(
                filter_data,
                sort=ordering,
                skip=record_skip,
                limit=page_size
            )
            results = [
                {
                    'timestamp': FORMATTING.parse_datetime(item['timestamp']),
                    'service_name': item.get('endpoint', ''),
                    'log_level': item.get('log_level', ''),
                    'errors': item.get('errors', ''),
                } for item in queries
            ]
            return ResponseController.success_200(
                data=MongoViewParse.parse_return(
                    results=results,
                    page_index=page_index,
                    page_size=page_size,
                    count=count,
                ),
                key_data='',
            )
        return ResponseController.success_200(data=MongoViewParse.parse_return(results=[]))


class AuthLogReport(APIView):
    @swagger_auto_schema(operation_summary='Chart report data since 7 days')
    @mask_view(login_require=True)
    def get(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
            try:
                range_selected = int(request.query_params.dict().get('range', 7))
                if range_selected in [7, 14, 30]:
                    raise ValueError()
            except ValueError:
                range_selected = 7

            key_of_cache = f'auth_log_${str(request.user.id)}_{range_selected}'
            data_cached = Caching().get(key_of_cache)
            if data_cached:
                results = data_cached
            else:
                end_time = timezone.now()
                start_time = datetime(year=end_time.year, month=end_time.month, day=end_time.day) - timedelta(
                    days=range_selected
                )
                pipeline = [
                    {
                        "$match": {
                            "timestamp": {"$gte": start_time, "$lt": end_time},
                            "metadata.service_name": "AUTH",
                            "metadata.user_id": str(request.user.id),
                        },
                    },
                    {
                        "$addFields": {"date": {"$dateTrunc": {"date": "$timestamp", "unit": "day"}}}
                    }, {
                        "$group": {
                            "_id": {
                                "date": "$date",
                                "endpoint": "$endpoint",
                                "log_level": "$log_level"
                            },
                            "count": {
                                "$sum": 1
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": "$_id.date",
                            "details": {
                                "$push": {
                                    "endpoint": "$_id.endpoint",
                                    "log_level": "$_id.log_level",
                                    "count": "$count"
                                }
                            }
                        }
                    },
                    {
                        "$sort": {"_id": 1}
                    },
                ]
                queries = mongo_log_auth.aggregate(pipeline)

                results = [
                    {
                        'date': result['_id'],
                        'details': result['details'],
                    }
                    for result in queries
                ]
                Caching().set(key_of_cache, results, timeout=60)
            return ResponseController.success_200(data=results)
        return ResponseController.success_200(data=MongoViewParse.parse_return(results=[]))

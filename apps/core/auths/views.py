from typing import Union

from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.utils import translation, timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from apps.core.account.models import User, ValidateUser
from apps.core.company.models import CompanyUserEmployee
from apps.core.auths.serializers import (
    AuthLoginSerializer, MyTokenObtainPairSerializer, SwitchCompanySerializer,
    AuthValidAccessCodeSerializer, MyLanguageUpdateSerializer, ChangePasswordSerializer, ForgotPasswordGetOTPSerializer,
    ValidateUserDetailSerializer, SubmitOTPSerializer,
)
from apps.shared import mask_view, ResponseController, AuthMsg, HttpMsg, DisperseModel, MediaForceAPI, TypeCheck


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
        if not user_obj.company_current_id:
            if user_obj.employee_current_id:
                company_user_emp = DisperseModel(app_model='company.companyuseremployee').get_model().objects.filter(
                    user_id=user_obj.id,
                    employee_id=user_obj.employee_current_id,
                )
            else:
                company_user_emp = DisperseModel(app_model='company.companyuseremployee').get_model().objects.filter(
                    user_id=user_obj.id,
                )
            if company_user_emp.count() > 0:
                obj_first = company_user_emp.first()
                user_obj.company_current_id = obj_first.company_id
                return user_obj, obj_first, True, ['company_current_id']
        if user_obj.company_current_id:
            company_user_emp = DisperseModel(app_model='company.companyuseremployee').get_model().objects.filter(
                user_id=user_obj.id,
                company_id=user_obj.company_current_id,
            )
            if company_user_emp.count() > 0:
                obj_first = company_user_emp.first()
                return user_obj, obj_first, True, ['company_current_id']
            return user_obj, None, True, ['company_current_id']
        return user_obj, None, False, ['company_current_id']

    @classmethod
    def force_employee_currently(cls, user_obj: User, company_user_emp_obj: models.Model = None) -> list[str]:
        if company_user_emp_obj:
            if hasattr(company_user_emp_obj, 'employee_id'):
                user_obj.employee_current_id = company_user_emp_obj.employee_id
                return ['employee_current_id']
        else:
            emp_objs = DisperseModel(app_model='hr.employee').get_model().objects.filter(
                company_id=user_obj.company_current_id,
                user_id=user_obj.id,
            )
            if emp_objs.count() > 0:
                user_obj.employee_current_id = emp_objs.first().id
                return ['employee_current_id']
        return []

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
            # info employee_id, space_id make sure correct
            self.check_and_update_globe(user_obj)

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


class AuthValidAccessCode(APIView):
    @swagger_auto_schema(operation_summary='Valid access code', request_body=AuthValidAccessCodeSerializer)
    @mask_view(login_require=True)
    def post(self, request, *args, **kwargs):
        company_id = request.data.get('company_id', None)
        user_agent = request.data.get('user_agent', None)
        public_ip = request.data.get('public_ip', None)
        access_id = request.data.get('access_id', None)
        if TypeCheck.check_uuid(company_id) and user_agent and public_ip and TypeCheck.check_uuid(access_id):
            obj = CompanyUserEmployee.objects.filter(user=request.user, company_id=company_id).first()
            if obj and obj.company.media_company_id and obj.employee.media_user_id:
                state, result_or_errs = MediaForceAPI.valid_access_code_login(
                    employee_media_id=obj.employee.media_user_id,
                    company_media_id=obj.company.media_company_id,
                    user_agent=user_agent,
                    public_ip=public_ip,
                    access_id=access_id,
                )
                if state:
                    return ResponseController.success_200(data=result_or_errs, key_data='result')
                return ResponseController.bad_request_400(msg=result_or_errs)
        return ResponseController.forbidden_403()


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
            ser = MyLanguageUpdateSerializer(data={
                'language': language
            }, partial=True)
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

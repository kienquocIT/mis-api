import logging

from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, exceptions
from rest_framework.views import APIView

from apps.core.forms.i18n import FormMsg
from apps.core.forms.models import FormPublished, FormPublishedEntries, FormPublishAuthenticateEmail
from apps.core.forms.serializers.serializers import (
    FormPublishedEntriesCreateSerializer,
    FormPublishedEntriesDetailSerializer, FormPublishedRuntimeDetailSerializer, FormPublishedEntriesUpdateSerializer,
)
from apps.core.tenant.models import Tenant
from apps.shared import mask_view, ResponseController, TypeCheck
from apps.shared.extends.exceptions import handle_exception_all_view
from apps.shared.extends.utils import clone_serializer_with_excludes

FORM_CODE_LENGTH = 32


def handle_form_authenticate(request, obj, tenant_code):
    request_user = None
    obj_auth = None
    auth_form = request.META.get('HTTP_AUTHENTICATIONFORM', None)
    if obj.form.authentication_required is True:
        if obj.form.authentication_type == 'system':
            if not request.user or (request.user and not request.user.is_authenticated):
                raise serializers.ValidationError({'authenticate_fail_code': 'system'})
            tenant_current = getattr(request.user, 'tenant_current', None)
            if not tenant_current or not hasattr(tenant_current, 'code'):
                raise serializers.ValidationError({'authenticate_fail_code': 'system'})
            if tenant_current.code.lower() != tenant_code:
                raise serializers.ValidationError({'authenticate_fail_code': 'system'})
            request_user = request.user
        elif obj.form.authentication_type == 'email':
            if not auth_form:
                raise serializers.ValidationError({'authenticate_fail_code': 'email'})
            try:
                obj_auth = FormPublishAuthenticateEmail.objects.get(pk=auth_form)
            except FormPublishAuthenticateEmail.DoesNotExist:
                raise serializers.ValidationError({'authenticate_fail_code': 'email'})
            if obj_auth.is_expired() is True:
                raise serializers.ValidationError({'authenticate_fail_code': 'email'})
    return {
        'authentication_required': obj.form.authentication_required,
        'request_user': request_user,
        'obj_auth': obj_auth,
    }


class RuntimeFormPublishedDetail(APIView):

    LIST_CONVERT_TO = 'LIST_STR'

    @swagger_auto_schema()
    @mask_view(login_require=False)
    def get(self, request, *args, tenant_code, form_code, use_at, **kwargs):
        if tenant_code and form_code and len(form_code) == FORM_CODE_LENGTH and use_at in ['view', 'iframe']:
            try:
                obj = FormPublished.objects.select_related('form', 'company').get(
                    is_active=True, code=form_code, tenant__code=tenant_code
                )
            except FormPublished.DoesNotExist:
                return ResponseController.notfound_404()

            if obj:
                if use_at == 'view' and obj.is_public is not True:
                    raise exceptions.PermissionDenied

                if use_at == 'iframe' and obj.is_iframe is not True:
                    raise exceptions.PermissionDenied

                handle_form_authenticate(request=request, obj=obj, tenant_code=tenant_code)
                exclude_data = []
                exclude_str = request.query_params.dict().get('excludes', '')
                if exclude_str:
                    exclude_data = [item.strip() for item in exclude_str.split(",")]
                cls_excludes = clone_serializer_with_excludes(
                    serializer_class=FormPublishedRuntimeDetailSerializer,
                    excludes=exclude_data,
                )
                try:
                    parsed_data = cls_excludes(instance=obj).data
                    return ResponseController.success_200(data=parsed_data)
                except Exception as err:
                    logging.error('RuntimeFormPublishedDetail.get raise error: %s', str(err))
        return ResponseController.notfound_404()

    @swagger_auto_schema(request_body=FormPublishedEntriesCreateSerializer)
    @mask_view(login_require=False)
    def post(self, request, *args, tenant_code, form_code, **kwargs):
        try:
            obj = FormPublished.objects.select_related('form', 'company').get(
                is_active=True, code=form_code, tenant__code=tenant_code
            )
        except FormPublished.DoesNotExist:
            return ResponseController.notfound_404()
        except Exception as err:
            handle_exception_all_view(err, self)
            return ResponseController.notfound_404()

        data = handle_form_authenticate(request=request, obj=obj, tenant_code=tenant_code)
        ser = FormPublishedEntriesCreateSerializer(
            data=request.data,
            context={
                'published_obj': obj,
                'user_obj': data['request_user'],
                'obj_auth': data['obj_auth'],
            }
        )
        ser.is_valid(raise_exception=True)
        instance = ser.save()
        return ResponseController.created_201(
            data=FormPublishedEntriesDetailSerializer(instance=instance).data
        )


class FormEntrySubmitted(APIView):
    LIST_CONVERT_TO = 'LIST_STR'

    @swagger_auto_schema()
    @mask_view(login_require=False)
    def get(self, request, *args, tenant_code, form_code, use_at, pk_submitted, **kwargs):  # pylint: disable=R0912
        if (
                tenant_code and form_code and len(form_code) == FORM_CODE_LENGTH and use_at in ['view', 'iframe']
                and TypeCheck.check_uuid(pk_submitted)
        ):
            try:
                obj = FormPublished.objects.select_related('form', 'company').get(
                    is_active=True, code=form_code, tenant__code=tenant_code
                )
            except FormPublished.DoesNotExist:
                return ResponseController.notfound_404()

            if obj:
                if use_at == 'view' and obj.is_public is not True:
                    raise exceptions.PermissionDenied

                if use_at == 'iframe' and obj.is_iframe is not True:
                    raise exceptions.PermissionDenied

                data = handle_form_authenticate(request, obj=obj, tenant_code=tenant_code)

                obj_submitted = None
                authentication_required = data['authentication_required']
                request_user = data['request_user']
                obj_auth = data['obj_auth']
                if request_user:
                    obj_submitted = FormPublishedEntries.objects.filter(
                        pk=pk_submitted,
                        company_id=obj.company_id,
                        user_created=data['request_user'],
                        creator_email__isnull=True,
                        is_active=True, is_delete=False,
                    ).first()
                elif obj_auth:
                    obj_submitted = FormPublishedEntries.objects.filter(
                        pk=pk_submitted,
                        company_id=obj.company_id,
                        user_created__isnull=True,
                        creator_email=obj_auth.email,
                        is_active=True, is_delete=False,
                    ).first()
                elif authentication_required is False:
                    obj_submitted = FormPublishedEntries.objects.filter(
                        pk=pk_submitted,
                        company_id=obj.company_id,
                        user_created__isnull=True,
                        creator_email__isnull=True,
                        is_active=True, is_delete=False,
                    ).first()

                if obj_submitted:
                    return ResponseController.success_200(
                        data=FormPublishedRuntimeDetailSerializer(
                            instance=obj,
                            context={
                                'entry_obj': obj_submitted,
                            }
                        ).data
                    )
        return ResponseController.notfound_404()

    @swagger_auto_schema()
    @mask_view(login_require=False)
    def put(self, request, *args, tenant_code, form_code, use_at, pk_submitted, **kwargs):  # pylint: disable=R0912
        if (
                tenant_code and form_code and len(form_code) == FORM_CODE_LENGTH and use_at in ['view', 'iframe']
                and TypeCheck.check_uuid(pk_submitted)
        ):
            try:
                obj = FormPublished.objects.select_related('form', 'company').get(
                    is_active=True, code=form_code, tenant__code=tenant_code
                )
            except FormPublished.DoesNotExist:
                return ResponseController.notfound_404()

            if obj:
                if use_at == 'view' and obj.is_public is not True:
                    raise exceptions.PermissionDenied

                if use_at == 'iframe' and obj.is_iframe is not True:
                    raise exceptions.PermissionDenied

                if obj.form.authentication_required is True:
                    if not request.user:
                        raise exceptions.AuthenticationFailed

                    if not request.user.is_authenticated:
                        raise exceptions.AuthenticationFailed

                    tenant_current = getattr(request.user, 'tenant_current', None)

                    if not tenant_current or not hasattr(tenant_current, 'code'):
                        raise exceptions.PermissionDenied

                    if tenant_current.code.lower() != tenant_code:
                        raise exceptions.PermissionDenied

                    if obj.form.edit_submitted is not True:
                        raise serializers.ValidationError(
                            {
                                'detail': FormMsg.FORM_ENTRY_EDIT_DENY,
                            }
                        )

                else:
                    if obj.form.submit_edit_of_anonymous is True:
                        try:
                            tenant_current = Tenant.objects.get(code=tenant_code)
                        except Tenant.DoesNotExist:
                            raise exceptions.PermissionDenied
                    else:
                        raise exceptions.PermissionDenied

                if tenant_current:
                    obj_submitted = FormPublishedEntries.objects.filter(
                        pk=pk_submitted,
                        tenant_id=tenant_current.id,
                        company_id=obj.company_id,
                        user_created=request.user,
                        is_active=True, is_delete=False,
                    ).first()
                    if obj_submitted:
                        ser = FormPublishedEntriesUpdateSerializer(
                            instance=obj_submitted,
                            data=request.data,
                            context={
                                'published_obj': obj,
                                'user_obj': request.user
                            }
                        )
                        ser.is_valid(raise_exception=True)
                        instance = ser.save()
                        return ResponseController.success_200(
                            data=FormPublishedEntriesDetailSerializer(instance=instance).data
                        )
        return ResponseController.notfound_404()


class RuntimeFormHasSubmitted(APIView):
    @swagger_auto_schema()
    @mask_view(login_require=True)
    def get(self, request, tenant_code, form_code, *args, **kwargs):
        if tenant_code and form_code and len(form_code) == FORM_CODE_LENGTH:
            try:
                obj = FormPublished.objects.select_related('form').get(
                    is_active=True, code=form_code, tenant__code=tenant_code
                )
            except FormPublished.DoesNotExist:
                return ResponseController.notfound_404()

            if obj:
                if obj.form.authentication_required is True:
                    if not request.user:
                        raise exceptions.AuthenticationFailed

                    if not request.user.is_authenticated:
                        raise exceptions.AuthenticationFailed

                    tenant_current = getattr(request.user, 'tenant_current', None)

                    if not tenant_current or not hasattr(tenant_current, 'code'):
                        raise exceptions.PermissionDenied

                    if tenant_current.code.lower() != tenant_code:
                        raise exceptions.PermissionDenied

                    entry_objs = FormPublishedEntries.objects.filter(
                        tenant_id=tenant_current.id,
                        company_id=obj.company_id,
                        user_created=request.user,
                        is_active=True, is_delete=False,
                    )
                    if entry_objs.count() > 0:
                        return ResponseController.success_200(
                            data={
                                'ids': [{
                                    'id': entry_obj.id,
                                    'date_created': entry_obj.date_created,
                                } for entry_obj in entry_objs],
                                'submit_only_one': obj.form.submit_only_one,
                                'edit_submitted': obj.form.edit_submitted,
                            }
                        )
        return ResponseController.notfound_404()


class RuntimeAuthenticate(APIView):
    @mask_view(login_require=False)
    def post(self, request, *args, tenant_code, form_code, **kwargs):
        if tenant_code and form_code:
            try:
                tenant_obj = Tenant.objects.get(code=tenant_code)
                form_obj = FormPublished.objects.get(tenant=tenant_obj, code=form_code)
            except (Tenant.DoesNotExist, FormPublished.DoesNotExist):
                return ResponseController.notfound_404()

            email = request.data.get('email', None)
            if email and TypeCheck.check_email(email):
                obj = FormPublishAuthenticateEmail.objects.create(
                    tenant=tenant_obj,
                    company=form_obj.company,
                    form=form_obj,
                    email=email,
                    **FormPublishAuthenticateEmail.generate_otp_data(),
                )
                return ResponseController.success_200(data={
                    'id': obj.id,
                    'email': obj.email,
                    'otp_expires_seconds': obj.otp_expires_seconds,
                    'otp_expires': obj.otp_expires
                })
            return ResponseController.forbidden_403()
        return ResponseController.notfound_404()


class RuntimeAuthVerifySession(APIView):
    @mask_view(login_require=False)
    def get(self, request, *args, tenant_code, form_code, pk_form_session, **kwargs):
        try:
            tenant_obj = Tenant.objects.get(code=tenant_code)
            form_obj = FormPublished.objects.get(tenant=tenant_obj, code=form_code)
            obj = FormPublishAuthenticateEmail.objects.get(id=pk_form_session, tenant=tenant_obj, form=form_obj)
        except (Tenant.DoesNotExist, FormPublished.DoesNotExist, FormPublishAuthenticateEmail.DoesNotExist):
            return ResponseController.notfound_404()

        return ResponseController.success_200(data={
            'id': str(obj.id),
            'email': str(obj.email),
            'is_valid': obj.is_valid,
            'expires': obj.expires.strftime(settings.REST_FRAMEWORK['DATETIME_FORMAT']),
        })

    @mask_view(login_require=False)
    def put(self, request, *args, tenant_code, form_code, pk_form_session, **kwargs):
        try:
            tenant_obj = Tenant.objects.get(code=tenant_code)
            form_obj = FormPublished.objects.get(tenant=tenant_obj, code=form_code)
            obj = FormPublishAuthenticateEmail.objects.get(id=pk_form_session, tenant=tenant_obj, form=form_obj)
        except (Tenant.DoesNotExist, FormPublished.DoesNotExist, FormPublishAuthenticateEmail.DoesNotExist):
            return ResponseController.forbidden_403()

        obj.activate_valid('1d', commit=True)
        return ResponseController.success_200(
            data={
                'id': str(obj.id),
                'email': str(obj.email),
                'is_valid': obj.is_valid,
                'expires': obj.expires.strftime(settings.REST_FRAMEWORK['DATETIME_FORMAT']),
            }
        )

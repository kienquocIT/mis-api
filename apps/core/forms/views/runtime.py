from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, exceptions
from rest_framework.views import APIView

from apps.core.forms.i18n import FormMsg
from apps.core.forms.models import FormPublished, FormPublishedEntries
from apps.core.forms.serializers.serializers import (
    FormPublishedEntriesCreateSerializer,
    FormPublishedEntriesDetailSerializer, FormPublishedRuntimeDetailSerializer, FormPublishedEntriesUpdateSerializer,
)
from apps.shared import mask_view, ResponseController, TypeCheck
from apps.shared.extends.exceptions import handle_exception_all_view

FORM_CODE_LENGTH = 32


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

                return ResponseController.success_200(
                    data=FormPublishedRuntimeDetailSerializer(instance=obj).data
                )

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

        request_user = request.user if request.user and request.user.is_authenticated else None

        # check rules authenticated required
        if obj.form.authentication_required is True and not request_user:
            raise serializers.ValidationError(
                {
                    'detail': FormMsg.FORM_REQUIRE_AUTHENTICATED,
                }
            )

        ser = FormPublishedEntriesCreateSerializer(
            data=request.data,
            context={
                'published_obj': obj,
                'user_obj': request_user
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
    @mask_view(login_require=True)
    def get(self, request, *args, tenant_code, form_code, use_at, pk_submitted, **kwargs):
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

                    obj_submitted = FormPublishedEntries.objects.filter(
                        pk=pk_submitted,
                        tenant_id=tenant_current.id,
                        company_id=obj.company_id,
                        user_created=request.user,
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
    @mask_view(login_require=True)
    def put(self, request, *args, tenant_code, form_code, use_at, pk_submitted, **kwargs):
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

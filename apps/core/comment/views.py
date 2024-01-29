from drf_yasg.utils import swagger_auto_schema

from apps.core.comment.serializers import CommentListSerializer, CommentCreateSerializer
from apps.shared import (
    BaseListMixin, BaseCreateMixin,
    mask_view, TypeCheck, ResponseController,
)
from apps.core.comment.authenticated import VerifyPermit

from apps.core.comment.models import Comments


class CommentList(BaseListMixin, BaseCreateMixin):
    queryset = Comments.objects
    serializer_list = CommentListSerializer
    serializer_detail = CommentListSerializer
    serializer_create = CommentCreateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']
    filterset_fields = {
        'parent_n': ['exact', 'isnull'],
    }

    @classmethod
    def valid_pk(cls, pk_doc, pk_app):
        return pk_doc and pk_app and TypeCheck.check_uuid(pk_doc) and TypeCheck.check_uuid(pk_app)

    @swagger_auto_schema(operation_summary="Comment list")
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, pk_doc, pk_app, **kwargs):
        if self.valid_pk(pk_doc=pk_doc, pk_app=pk_app):
            del self.kwargs['pk_doc']
            del self.kwargs['pk_app']

            if request.user.employee_current_id:
                state = VerifyPermit(application_id=pk_app).verify(idx=pk_doc, view_self=self)
                if not state:
                    self.kwargs['mentions__contains'] = str(request.user.employee_current_id)
                self.kwargs.update({'doc_id': pk_doc, 'application_id': pk_app})
                return self.list(request, *args, **kwargs)
        return ResponseController.forbidden_403()

    @swagger_auto_schema(operation_summary="Comment create", request_body=CommentCreateSerializer)
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def post(self, request, *args, pk_doc, pk_app, **kwargs):
        if self.valid_pk(pk_doc=pk_doc, pk_app=pk_app):
            state = VerifyPermit(application_id=pk_app).verify(idx=pk_doc, view_self=self)
            if state:
                field_hidden = self.cls_check.attr.setup_hidden(from_view='create')
                serializer = self.get_serializer_create(data=request.data)
                serializer.is_valid(raise_exception=True)
                obj = self.perform_create(
                    serializer, extras={
                        **field_hidden,
                        'doc_id': pk_doc,
                        'application_id': pk_app,
                    }
                )
                return ResponseController.created_201(data=self.get_serializer_detail_return(obj))
        return ResponseController.forbidden_403()


class CommentRepliesList(BaseListMixin, BaseCreateMixin):
    queryset = Comments.objects
    serializer_list = CommentListSerializer
    serializer_detail = CommentListSerializer
    serializer_create = CommentCreateSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    create_hidden_field = ['tenant_id', 'company_id', 'employee_created_id']

    @classmethod
    def sequence_parent_null(cls, obj):
        if obj:
            if obj.parent_n:
                return cls.sequence_parent_null(obj)
            return obj
        return None

    @classmethod
    def get_object_comment(cls, idx):
        try:
            obj = Comments.objects.get_current(pk=idx, fill__tenant=True, fill__company=True)
            return cls.sequence_parent_null(obj)
        except Comments.DoesNotExist:
            pass
        return None

    @swagger_auto_schema(operation_summary="Comment replies list")
    @mask_view(login_require=True, auth_require=False)
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            del self.kwargs['pk']
            self.kwargs.update({'parent_n_id': pk})

            obj = self.get_object_comment(idx=pk)
            if obj:
                state = str(request.user.employee_current_id) in obj.mentions
                if not state:
                    state = VerifyPermit(application_id=obj.application_id).verify(idx=obj.doc_id, view_self=self)

                if state is True:
                    return self.list(request, *args, **kwargs)
        return ResponseController.forbidden_403()

    @swagger_auto_schema(operation_summary="Comment replies create", request_body=CommentCreateSerializer)
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def post(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            obj = self.get_object_comment(idx=pk)
            if obj:
                state = str(request.user.employee_current_id) in obj.mentions
                if not state:
                    state = VerifyPermit(application_id=obj.application_id).verify(idx=obj.doc_id, view_self=self)

                if state is True:
                    field_hidden = self.cls_check.attr.setup_hidden(from_view='create')
                    serializer = self.get_serializer_create(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    instance = self.perform_create(
                        serializer, extras={
                            **field_hidden,
                            'doc_id': obj.doc_id,
                            'application_id': obj.application_id,
                            'parent_n': obj,
                        }
                    )
                    return ResponseController.created_201(data=self.get_serializer_detail_return(instance))
        return ResponseController.forbidden_403()


class RoomRepliesList(BaseListMixin):
    queryset = Comments.objects
    serializer_list = CommentListSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    def get_object(self) -> Comments or None:
        try:
            return Comments.objects.get_current(pk=self.kwargs['pk'], fill__tenant=True, fill__company=True)
        except Comments.DoesNotExist:
            pass
        return None

    def get_room_comment(self, obj):
        siblings_count = Comments.objects.filter(doc_id=obj.doc_id, parent_n__isnull=True).count()
        if obj.parent_n:
            parent_obj = obj.parent_n
            child_obj = obj
            children_count = Comments.objects.filter(parent_n=obj.parent_n).count()
        else:
            parent_obj = obj
            child_obj = None
            children_count = 0

        return {
            'siblings_count': siblings_count,
            'children_count': children_count,
            'parent': self.get_serializer_list(instance=parent_obj).data if parent_obj else {},
            'child': self.get_serializer_list(instance=child_obj).data if child_obj else {},
        }

    @swagger_auto_schema(operation_summary="Comment room replies list")
    @mask_view(login_require=True, auth_require=False, employee_require=True)
    def get(self, request, *args, pk, **kwargs):
        if pk and TypeCheck.check_uuid(pk):
            obj = self.get_object()
            if obj and request.user.employee_current_id:
                state = str(request.user.employee_current_id) in obj.mentions
                if not state:
                    state = VerifyPermit(application_id=obj.application_id).verify(idx=obj.doc_id, view_self=self)

                if state is True:
                    return ResponseController.success_200(data=self.get_room_comment(obj), key_data='result')
        return ResponseController.forbidden_403()

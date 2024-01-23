from drf_yasg.utils import swagger_auto_schema

from apps.core.comment.serializers import CommentListSerializer, CommentCreateSerializer
from apps.shared import (
    BaseListMixin, BaseCreateMixin,
    mask_view, TypeCheck, ResponseController,
)

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
            self.kwargs.update({'doc_id': pk_doc, 'application_id': pk_app})
            return self.list(request, *args, **kwargs)
        return self.list_empty()

    @swagger_auto_schema(operation_summary="Comment create", request_body=CommentCreateSerializer)
    @mask_view(login_require=True, auth_require=False)
    def post(self, request, *args, pk_doc, pk_app, **kwargs):
        if self.valid_pk(pk_doc=pk_doc, pk_app=pk_app):
            field_hidden = self.cls_check.attr.setup_hidden(from_view='create')
            serializer = self.get_serializer_create(data=request.data)
            serializer.is_valid(raise_exception=True)
            obj = self.perform_create(serializer, extras={
                **field_hidden,
                'doc_id': pk_doc,
                'application_id': pk_app,
            })
            return ResponseController.created_201(data=self.get_serializer_detail_return(obj))
        return ResponseController.forbidden_403()

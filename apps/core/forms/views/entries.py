from drf_yasg.utils import swagger_auto_schema

from apps.core.forms.models import Form, FormPublishedEntries, FormPublished
from apps.core.forms.serializers.serializers import FormDetailForEntriesSerializer, FormEntriesListSerializer
from apps.shared import BaseRetrieveMixin, mask_view, BaseListMixin, ResponseController


class FormDetailForEntries(BaseRetrieveMixin):
    queryset = Form.objects
    serializer_detail = FormDetailForEntriesSerializer
    retrieve_hidden_field = ['tenant_id', 'company_id']

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def get(self, request, *args, pk, **kwargs):
        return self.retrieve(request, *args, pk, **kwargs)


class FormEntriesList(BaseListMixin):
    queryset = FormPublishedEntries.objects
    serializer_list = FormEntriesListSerializer
    list_hidden_field = ['tenant_id', 'company_id']
    filterset_fields = ['ref_name', 'user_created_id']

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def get(self, request, *args, pk, **kwargs):
        del self.kwargs['pk']

        try:
            form_obj = Form.objects.get_current(fill__company=True, pk=pk)
            published_obj = FormPublished.objects.get_current(form=form_obj)
            self.kwargs['published'] = published_obj
        except Form.DoesNotExist:
            return ResponseController.notfound_404()
        except FormPublished.DoesNotExist:
            return ResponseController.notfound_404()

        return self.list(request, *args, pk, **kwargs)


class FormEntriesRefNameList(BaseListMixin):
    queryset = FormPublishedEntries.objects
    serializer_list = FormEntriesListSerializer
    list_hidden_field = ['tenant_id', 'company_id']

    def get_ref_name_list(self):
        ref_name_list = self.queryset.filter(published=self.kwargs['published'], ref_name__isnull=False).values_list(
            'ref_name', flat=True
        )
        return list(set(ref_name_list))

    @swagger_auto_schema()
    @mask_view(login_require=True, allow_admin_company=True)
    def get(self, request, *args, pk, **kwargs):
        del self.kwargs['pk']
        try:
            form_obj = Form.objects.get_current(fill__company=True, pk=pk)
            published_obj = FormPublished.objects.get_current(form=form_obj)
            self.kwargs['published'] = published_obj
        except Form.DoesNotExist:
            return ResponseController.notfound_404()
        except FormPublished.DoesNotExist:
            return ResponseController.notfound_404()

        ref_name_list = self.get_ref_name_list()
        return ResponseController.success_200(
            data={
                'ref_name_list': sorted(ref_name_list),
            }
        )

from drf_yasg.utils import swagger_auto_schema

from apps.masterdata.saledata.models import Contact
from apps.masterdata.saledata.serializers import ContactCreateSerializer
from apps.shared import BaseListMixin, mask_view, BaseRetrieveMixin, BaseUpdateMixin, BaseCreateMixin
from apps.sales.lead.models import Lead, LeadStage
from apps.sales.lead.serializers import (
    LeadListSerializer, LeadCreateSerializer, LeadDetailSerializer, LeadUpdateSerializer,
    LeadStageListSerializer
)

__all__ = [
    'LeadList',
    'LeadDetail',
    'LeadStageList'
]


class LeadList(BaseListMixin, BaseCreateMixin):
    queryset = Lead.objects
    search_fields = ['title']
    serializer_list = LeadListSerializer
    serializer_create = LeadCreateSerializer
    serializer_detail = LeadDetailSerializer
    list_hidden_field = BaseListMixin.LIST_HIDDEN_FIELD_DEFAULT
    create_hidden_field = BaseCreateMixin.CREATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(
        operation_summary="Lead list",
        operation_description="Lead list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Lead",
        operation_description="Create new Lead",
        request_body=LeadCreateSerializer,
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class LeadDetail(BaseRetrieveMixin, BaseUpdateMixin):
    queryset = Lead.objects  # noqa
    serializer_list = LeadListSerializer
    serializer_create = LeadCreateSerializer
    serializer_detail = LeadDetailSerializer
    serializer_update = LeadUpdateSerializer
    retrieve_hidden_field = BaseRetrieveMixin.RETRIEVE_HIDDEN_FIELD_DEFAULT
    update_hidden_field = BaseUpdateMixin.UPDATE_HIDDEN_FIELD_DEFAULT

    def get_queryset(self):
        return super().get_queryset().prefetch_related().select_related()

    @swagger_auto_schema(operation_summary='Detail Lead')
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        if 'convert_contact' in self.request.query_params:
            # convert to a new contact
            lead = Lead.objects.get(pk=self.kwargs['pk'])
            lead_configs = lead.lead_configs.first()
            if lead_configs:
                ContactCreateSerializer.validate_email(lead.email)
                ContactCreateSerializer.validate_mobile(lead.mobile)
                ContactCreateSerializer.validate_owner(self.request.user.employee_current)
                number = Contact.objects.filter(
                    tenant_id=self.request.user.tenant_current_id,
                    company_id=self.request.user.company_current_id
                ).count() + 1
                contact_mapped = Contact.objects.create(
                    code=f"C00{number}",
                    email=lead.email,
                    mobile=lead.mobile,
                    fullname=lead.contact_name,
                    job_title=lead.job_title,
                    owner=self.request.user.employee_current,
                    tenant_id=self.request.user.tenant_current_id,
                    company_id=self.request.user.company_current_id
                )
                current_stage = LeadStage.objects.filter(
                    tenant_id=self.request.user.tenant_current_id,
                    company_id=self.request.user.company_current_id,
                    level=2
                ).first()
                lead.current_lead_stage = current_stage
                lead.save(update_fields=['current_lead_stage'])
                lead_configs.contact_mapped = contact_mapped
                lead_configs.create_contact = True
                lead_configs.save(update_fields=['contact_mapped', 'create_contact'])
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update ARInvoice", request_body=LeadUpdateSerializer)
    @mask_view(
        login_require=True, auth_require=False,
    )
    def put(self, request, *args, **kwargs):
        self.serializer_class = LeadUpdateSerializer
        return self.update(request, *args, **kwargs)


class LeadStageList(BaseListMixin):
    queryset = LeadStage.objects
    serializer_list = LeadStageListSerializer

    @swagger_auto_schema(
        operation_summary="Lead stage list",
        operation_description="Lead stage list",
    )
    @mask_view(
        login_require=True, auth_require=False,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

import datetime
from django.utils import timezone
from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, DocumentType
from apps.sales.bidding.models import Bidding, BiddingAttachment, BiddingDocument, BiddingPartnerAccount
from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, AbstractListSerializerModel, HRMsg
from apps.shared.translations.base import AttachmentMsg

class BiddingListSerializer(AbstractListSerializerModel):
    customer = serializers.SerializerMethodField()
    sale_person = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    venture_partner = serializers.SerializerMethodField()
    class Meta:
        model = Bidding
        fields = (
            'id',
            'title',
            'code',
            'customer',
            'sale_person',
            'date_created',
            'status'
        )

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': obj.customer_id,
            'title': obj.customer.name,
            'code': obj.customer.code,
        } if obj.customer else {}

    @classmethod
    def get_sale_person(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'first_name': obj.employee_inherit.first_name,
            'last_name': obj.employee_inherit.last_name,
            'email': obj.employee_inherit.email,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
            'is_active': obj.employee_inherit.is_active,
        } if obj.employee_inherit else {}

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
            'is_deal_close': obj.opportunity.is_deal_close,
        } if obj.opportunity else {}

    @classmethod
    def get_partner_account(cls, obj):
        if obj.partner_account:
            all_partner_account = [partner_account_item.get('name', None) for partner_account_item in obj.partner_account]
            return all_partner_account
        return []

class AccountForBiddingListSerializer(AbstractListSerializerModel):
    contact_mapped = serializers.SerializerMethodField()
    account_type = serializers.SerializerMethodField()
    manager = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    bank_accounts_mapped = serializers.SerializerMethodField()
    revenue_information = serializers.SerializerMethodField()
    billing_address = serializers.SerializerMethodField()
    industry = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            "id",
            'code',
            "name",
            "website",
            "code",
            "tax_code",
            "account_type",
            "manager",
            "owner",
            "phone",
            'annual_revenue',
            'contact_mapped',
            'bank_accounts_mapped',
            'revenue_information',
            'billing_address',
            'industry'
        )

    @classmethod
    def get_account_type(cls, obj):
        if obj.account_type:
            all_account_types = [account_type.get('title', None) for account_type in obj.account_type]
            return all_account_types
        return []

    @classmethod
    def get_manager(cls, obj):
        if obj.manager:
            return obj.manager
        return []

    @classmethod
    def get_owner(cls, obj):
        if obj.owner:
            return {'id': obj.owner_id, 'fullname': obj.owner.fullname}
        return {}

    @classmethod
    def get_contact_mapped(cls, obj):
        contact_mapped = obj.contact_account_name.all()
        if contact_mapped.count() > 0:
            list_contact_mapped = []
            for item in contact_mapped:
                list_contact_mapped.append(str(item.id))
            return list_contact_mapped
        return []

    @classmethod
    def get_bank_accounts_mapped(cls, obj):
        bank_accounts_mapped_list = []
        for item in obj.account_banks_mapped.all():
            bank_accounts_mapped_list.append(
                {
                    'bank_country_id': item.country_id,
                    'bank_name': item.bank_name,
                    'bank_code': item.bank_code,
                    'bank_account_name': item.bank_account_name,
                    'bank_account_number': item.bank_account_number,
                    'bic_swift_code': item.bic_swift_code,
                    'is_default': item.is_default
                }
            )
        return bank_accounts_mapped_list

    @classmethod
    def get_revenue_information(cls, obj):
        current_date = timezone.now()
        revenue_ytd = 0
        order_number = 0
        for period in obj.company.saledata_periods_belong_to_company.all():
            if period.fiscal_year == current_date.year:
                start_date_str = str(period.start_date) + ' 00:00:00'
                start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
                for customer_revenue in obj.report_customer_customer.filter(
                        group_inherit__is_delete=False, sale_order__system_status=3
                ):
                    if customer_revenue.date_approved:
                        if start_date <= customer_revenue.date_approved <= current_date:
                            revenue_ytd += customer_revenue.revenue
                            order_number += 1
        return {
            'revenue_ytd': revenue_ytd,
            'order_number': order_number,
            'revenue_average': round(revenue_ytd / order_number) if order_number > 0 else 0,
        }

    @classmethod
    def get_billing_address(cls, obj):
        billing_address_list = []
        for item in obj.account_mapped_billing_address.all():
            billing_address_list.append({
                'id': item.id,
                'account_name': item.account_name,
                'email': item.email,
                'tax_code': item.tax_code,
                'account_address': item.account_address,
                'full_address': item.full_address,
                'is_default': item.is_default
            })
        return billing_address_list

    @classmethod
    def get_industry(cls, obj):
        if obj.industry:
            return {
                'id': obj.industry_id,
                'code': obj.industry.code,
                'title': obj.industry.title,
            }
        return {}

class DocumentMasterDataBiddingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentType
        fields = (
            "id",
            'code',
            "title",
        )
import datetime
from django.utils import timezone
from rest_framework import serializers
from apps.core.hr.models import Employee
from apps.masterdata.saledata.models import Account, DocumentType
from apps.sales.bidding.models import Bidding, BiddingAttachment, BiddingDocument, BiddingPartnerAccount
from apps.sales.bidding.models.bidding_sub import BiddingCommonCreate
from apps.sales.opportunity.models import Opportunity
from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, AbstractListSerializerModel, HRMsg
from apps.shared.translations.base import AttachmentMsg

class DocumentCreateSerializer(serializers.ModelSerializer):
    document_type = serializers.UUIDField(required=False, allow_null=True)
    id = serializers.UUIDField(required=False, allow_null=True)
    class Meta:
        model = BiddingDocument
        fields = (
            'id',
            'title',
            'remark',
            'document_type',
            'attachment_data',
            'order',
        )

    @classmethod
    def validate_document_type(cls, value):
        if value:
            try:
                document_type = DocumentType.objects.get(id=value)
                return document_type
            except DocumentType.DoesNotExist:
                raise serializers.ValidationError({'document_type': 'Document type does not exist'})
        return None
    @classmethod
    def validate_id(cls, value):
        if value:
            return str(value)
        return None


class VenturePartnerCreateSerializer(serializers.ModelSerializer):
    partner_account = serializers.UUIDField()
    id = serializers.UUIDField(required=False, allow_null=True)
    class Meta:
        model = BiddingPartnerAccount
        fields = (
            'id',
            'is_leader',
            'partner_account'
        )

    @classmethod
    def validate_partner_account(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'partner_account': 'partner_account does not exist'})

    @classmethod
    def validate_id(cls, value):
        if value:
            return str(value)
        return None


class BiddingListSerializer(AbstractListSerializerModel):
    customer = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    class Meta:
        model = Bidding
        fields = (
            'id',
            'title',
            'code',
            'customer',
            'bid_date',
            'date_created',
            'employee_inherit',
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
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
        } if obj.employee_inherit else {}


class BiddingDetailSerializer(AbstractDetailSerializerModel):
    venture_partner = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    attachment_m2m = serializers.SerializerMethodField()
    class Meta:
        model = Bidding
        fields = (
            'title',
            'opportunity',
            'venture_partner',
            'customer',
            'bid_value',
            'bid_date',
            'employee_inherit',
            'tinymce_content',
            'attachment_m2m'
        )

    @classmethod
    def get_customer(cls, obj):
        return {
            'id': obj.customer_id,
            'name': obj.customer.name,
            'code': obj.customer.code,
        } if obj.customer else {}

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
        } if obj.employee_inherit else {}

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title,
            'code': obj.opportunity.code,
        } if obj.opportunity else {}

    @classmethod
    def get_venture_partner(cls, obj):
        data = []
        for item in obj.bidding_partner_account_bidding.all():
            data.append({
                "id": item.id,
                "title": item.partner_account.name,
                "code": item.partner_account.code,
                "is_leader": item.is_leader,
                'partner_account': item.partner_account.id,
            })
        return data

    @classmethod
    def get_attachment_m2m(cls, obj):
        data = []
        for item in obj.bidding_document_bidding.all():
            data.append({
                "id": item.id,
                "title": item.title,
                "document_type": item.document_type.id if item.document_type else None,
                "is_manual": not item.document_type,
                "remark": item.remark,
                "attachment_data": item.attachment_data,
                "order": item.order
            })
        return data


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


class BiddingCreateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)
    document_data = DocumentCreateSerializer(many=True, required=False)
    opportunity_id = serializers.UUIDField(
        required=True
    )
    bid_value = serializers.FloatField(required=False)
    venture_partner = VenturePartnerCreateSerializer(many=True, required=False)
    customer = serializers.UUIDField()
    employee_inherit_id = serializers.UUIDField()

    class Meta:
        model = Bidding
        fields = (
            'title',
            'attachment',
            'opportunity_id',
            'document_data',
            'venture_partner' ,
            'customer',
            'bid_value' ,
            'bid_date',
            'employee_inherit_id',
            'tinymce_content'
        )

    @classmethod
    def validate_customer(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'customer': 'Customer does not exist'})

    @classmethod
    def validate_opportunity_id(cls, value):
        try:
            if value is None:
                return value
            return Opportunity.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
        except Opportunity.DoesNotExist:
            raise serializers.ValidationError({'opportunity': 'opp not exist'})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            return Employee.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit': 'not exist'})

    @classmethod
    def validate_bid_date(cls, value):
        if not value:
            return None
        return value

    @classmethod
    def validate_bid_value(cls, value):
        if not value:
            return None
        return value

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = BiddingAttachment.valid_change(
                current_ids=value, employee_id=user.employee_current_id, doc_id=None
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    # @decorator_run_workflow
    def create(self, validated_data):
        attachment = validated_data.pop('attachment', [])
        venture_partner = validated_data.pop('venture_partner', [])
        document_data = validated_data.pop('document_data', [])
        create_data = {'attachment': attachment, 'venture_partner': venture_partner, 'document_data': document_data}
        bidding = Bidding.objects.create(**validated_data)
        BiddingCommonCreate.create_sub_models( instance=bidding, create_data= create_data)
        return bidding


class BiddingUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)
    document_data = DocumentCreateSerializer(many=True, required=False)
    opportunity_id = serializers.UUIDField(
        required=True
    )
    bid_value = serializers.FloatField(required=False)
    venture_partner = VenturePartnerCreateSerializer(many=True, required=False)
    customer = serializers.UUIDField()
    employee_inherit_id = serializers.UUIDField()

    class Meta:
        model = Bidding
        fields = (
            'title',
            'attachment',
            'opportunity_id',
            'document_data',
            'venture_partner' ,
            'customer',
            'bid_value' ,
            'bid_date',
            'employee_inherit_id',
            'tinymce_content'
        )

    @classmethod
    def validate_customer(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'customer': 'Customer does not exist'})

    @classmethod
    def validate_opportunity_id(cls, value):
        try:
            if value is None:
                return value
            return Opportunity.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
        except Opportunity.DoesNotExist:
            raise serializers.ValidationError({'opportunity': 'opp not exist'})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            return Employee.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit': 'not exist'})

    @classmethod
    def validate_bid_date(cls, value):
        if not value:
            return None
        return value

    @classmethod
    def validate_bid_value(cls, value):
        if not value:
            return 0
        return value

    def validate_attachment(self, value):
        user = self.context.get('user', None)
        if user and hasattr(user, 'employee_current_id'):
            state, result = BiddingAttachment.valid_change(
                current_ids=value, employee_id=user.employee_current_id, doc_id=self.instance.id
            )
            if state is True:
                return result
            raise serializers.ValidationError({'attachment': AttachmentMsg.SOME_FILES_NOT_CORRECT})
        raise serializers.ValidationError({'employee_id': HRMsg.EMPLOYEE_NOT_EXIST})

    # @decorator_run_workflow
    def update(self, instance, validated_data):
        attachment = validated_data.pop('attachment', [])
        venture_partner = validated_data.pop('venture_partner', [])
        document_data = validated_data.pop('document_data', [])
        update_data = {'attachment': attachment, 'venture_partner': venture_partner, 'document_data': document_data}
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        BiddingCommonCreate.create_sub_models( instance=instance, create_data=update_data)
        return instance

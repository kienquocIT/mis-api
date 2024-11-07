from rest_framework import serializers
from apps.core.hr.models import Employee
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, DocumentType
from apps.sales.bidding.models import Bidding, BiddingAttachment, BiddingDocument, BiddingPartnerAccount, \
    BiddingBidderAccount
from apps.sales.bidding.serializers.bidding_sub import BiddingCommonCreate
from apps.sales.opportunity.models import Opportunity
from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, AbstractListSerializerModel, HRMsg
from apps.shared.translations.base import AttachmentMsg


class DocumentCreateSerializer(serializers.ModelSerializer):
    document_type = serializers.UUIDField(required=False, allow_null=True)
    class Meta:
        model = BiddingDocument
        fields = (
            'title',
            'remark',
            'document_type',
            'attachment_data',
            'order',
            'is_invite_doc'
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

    def validate(self, validate_data):
        attachment_data = validate_data.get('attachment_data')
        if not attachment_data:
            raise serializers.ValidationError({'document_type': 'Bidding Document must have data'})
        return validate_data

class VenturePartnerCreateSerializer(serializers.ModelSerializer):
    partner_account = serializers.UUIDField()
    class Meta:
        model = BiddingPartnerAccount
        fields = (
            'is_leader',
            'partner_account'
        )

    @classmethod
    def validate_partner_account(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'partner_account': 'partner_account does not exist'})




class OtherBidderCreateSerializer(serializers.ModelSerializer):
    bidder_account = serializers.UUIDField()

    class Meta:
        model = BiddingBidderAccount
        fields = (
            'is_won',
            'bidder_account'
        )

    @classmethod
    def validate_bidder_account(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'bidder_account': 'bidder_account does not exist'})

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
            'bid_status'
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
    other_bidder = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    attachment_m2m = serializers.SerializerMethodField()

    class Meta:
        model = Bidding
        fields = (
            'title',
            'opportunity',
            'customer',
            'venture_partner',
            'other_bidder',
            'bid_value',
            'bid_bond_value',
            'bid_status',
            'cause_of_lost',
            'other_cause',
            'security_type',
            'bid_date',
            'employee_inherit',
            'employee_created_id',
            'tinymce_content',
            'attachment_m2m'
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
            if item.partner_account:
                data.append({
                    "id": item.id,
                    "title": item.partner_account.name,
                    "code": item.partner_account.code,
                    "is_leader": item.is_leader,
                    'partner_account': item.partner_account.id,
                })
        return data

    @classmethod
    def get_other_bidder(cls, obj):
        data = []
        for item in obj.bidding_bidder_account_bidding.all():
            if item.bidder_account:
                data.append({
                    "id": item.id,
                    "title": item.bidder_account.name,
                    "code": item.bidder_account.code,
                    "is_won": item.is_won,
                    'bidder_account': item.bidder_account.id,
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
                "order": item.order,
                "is_invite_doc": item.is_invite_doc,
            })
        return data


class AccountForBiddingListSerializer(AbstractListSerializerModel):
    class Meta:
        model = Account
        fields = (
            "id",
            'code',
            "name"
        )


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
    opportunity = serializers.UUIDField(
        required=True
    )
    bid_value = serializers.FloatField()
    bid_date = serializers.DateField()
    bid_bond_value = serializers.FloatField(required=False)
    venture_partner = VenturePartnerCreateSerializer(many=True, required=False)
    other_bidder = OtherBidderCreateSerializer(many=True, required=False)
    employee_inherit_id = serializers.UUIDField()
    security_type= serializers.IntegerField(required=False)
    bid_status= serializers.IntegerField(required=False)
    other_cause= serializers.CharField(required=False,allow_blank=True)
    cause_of_lost = serializers.ListSerializer(child=serializers.IntegerField(), required=False)

    class Meta:
        model = Bidding
        fields = (
            'title',
            'attachment',
            'opportunity',
            'document_data',
            'venture_partner' ,
            'other_bidder',
            'bid_value' ,
            'bid_bond_value',
            'security_type',
            'bid_date',
            'employee_inherit_id',
            'bid_status',
            'cause_of_lost',
            'other_cause',
            'tinymce_content'
        )

    @classmethod
    def validate_opportunity(cls, value):
        if value:
            try:
                return Opportunity.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            except Opportunity.DoesNotExist:
                raise serializers.ValidationError({'opportunity': 'Opportunity not exist'})
        raise serializers.ValidationError({'opportunity': 'Opportunity is required'})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            return Employee.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit': 'not exist'})

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

    def validate(self, validate_data):
        if validate_data.get('opportunity'):
            validate_data['customer'] = validate_data.get('opportunity').customer
        cause_of_lost = validate_data.get('cause_of_lost', [])
        other_cause = validate_data.get('other_cause', '')
        bid_bond_value = validate_data.get('bid_bond_value', None)
        security_type = validate_data.get('security_type', 0)
        if validate_data.get('bid_status') == 2: #bid lost
            if len(cause_of_lost) == 0: #no cause of lost chosen
                raise serializers.ValidationError(
                    {'cause_of_lost': 'If bid is lost, must choose at least one cause of lost'})
        if '4' in cause_of_lost: #other reason
            if not other_cause:
                raise serializers.ValidationError(
                    {'other_cause': 'If cause of lost is "other reason", must specify the reason'})

        if bid_bond_value:
            if security_type == 0:
                raise serializers.ValidationError(
                    {'bid_bond_value': 'If there is a bond value, must choose a security type'})
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        attachment = validated_data.pop('attachment', [])
        venture_partner = validated_data.pop('venture_partner', [])
        other_bidder = validated_data.pop('other_bidder', [])
        document_data = validated_data.pop('document_data', [])
        create_data = {
            'attachment': attachment,
            'venture_partner': venture_partner,
            'document_data': document_data,
            'other_bidder': other_bidder
        }
        bidding = Bidding.objects.create(**validated_data)
        BiddingCommonCreate.create_sub_models( instance=bidding, create_data= create_data)
        return bidding


class BiddingUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)
    document_data = DocumentCreateSerializer(many=True, required=False)
    opportunity = serializers.UUIDField(
        required=True
    )
    bid_value = serializers.FloatField()
    bid_date = serializers.DateField()
    bid_bond_value = serializers.FloatField(required=False)
    venture_partner = VenturePartnerCreateSerializer(many=True, required=False)
    other_bidder = OtherBidderCreateSerializer(many=True, required=False)
    employee_inherit_id = serializers.UUIDField()
    security_type = serializers.IntegerField(required=False)
    bid_status = serializers.IntegerField(required=False)
    other_cause = serializers.CharField(required=False, allow_blank=True)
    cause_of_lost = serializers.ListSerializer(child=serializers.IntegerField(), required=False)

    class Meta:
        model = Bidding
        fields = (
            'title',
            'attachment',
            'opportunity',
            'document_data',
            'venture_partner',
            'other_bidder',
            'bid_value',
            'bid_bond_value',
            'security_type',
            'bid_date',
            'employee_inherit_id',
            'bid_status',
            'cause_of_lost',
            'other_cause',
            'tinymce_content'
        )

    @classmethod
    def validate_opportunity(cls, value):
        if value:
            try:
                return Opportunity.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            except Opportunity.DoesNotExist:
                raise serializers.ValidationError({'opportunity': 'Opportunity not exist'})
        raise serializers.ValidationError({'opportunity': 'Opportunity is required'})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            return Employee.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit': 'not exist'})

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

    def validate(self, validate_data):
        if validate_data.get('opportunity'):
            validate_data['customer'] = validate_data.get('opportunity').customer
        cause_of_lost = validate_data.get('cause_of_lost', [])
        other_cause = validate_data.get('other_cause', '')
        bid_bond_value = validate_data.get('bid_bond_value', None)
        security_type = validate_data.get('security_type', 0)
        if validate_data.get('bid_status') == 2:  # bid lost
            if len(cause_of_lost) == 0:  # no cause of lost chosen
                raise serializers.ValidationError(
                    {'cause_of_lost': 'If bid is lost, must choose at least one cause of lost'})
        if '4' in cause_of_lost:  # other reason
            if not other_cause:
                raise serializers.ValidationError(
                    {'other_cause': 'If cause of lost is "other reason", must specify the reason'})

        if bid_bond_value:
            if security_type == 0:
                raise serializers.ValidationError(
                    {'bid_bond_value': 'If there is a bond value, must choose a security type'})
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        attachment = validated_data.pop('attachment', [])
        venture_partner = validated_data.pop('venture_partner', [])
        other_bidder = validated_data.pop('other_bidder', [])
        document_data = validated_data.pop('document_data', [])
        update_data = {
            'attachment': attachment,
            'venture_partner': venture_partner,
            'document_data': document_data,
            'other_bidder': other_bidder
        }
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        BiddingCommonCreate.create_sub_models( instance=instance, create_data=update_data)
        return instance


class BiddingUpdateResultSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    other_bidder = OtherBidderCreateSerializer(many=True, required=False)
    bid_status = serializers.IntegerField(required=False)
    other_cause = serializers.CharField(required=False, allow_blank=True)
    cause_of_lost = serializers.ListSerializer(child=serializers.IntegerField(), required=False)

    class Meta:
        model = Bidding
        fields = (
            'id',
            'other_bidder',
            'bid_status',
            'cause_of_lost',
            'other_cause',
        )

    @classmethod
    def validate_id(cls, value):
        if value:
            try:
                return Bidding.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
            except Bidding.DoesNotExist:
                raise serializers.ValidationError({'bidding': 'Bidding not exist'})
        raise serializers.ValidationError({'bidding': 'Bidding is required'})

    def validate(self, validate_data):
        cause_of_lost = validate_data.get('cause_of_lost', [])
        other_cause = validate_data.get('other_cause', '')
        if validate_data.get('bid_status') == 2:  # bid lost
            if len(cause_of_lost) == 0:  # no cause of lost chosen
                raise serializers.ValidationError(
                    {'cause_of_lost': 'If bid is lost, must choose at least one cause of lost'})
        if '4' in cause_of_lost:  # other reason
            if not other_cause:
                raise serializers.ValidationError(
                    {'other_cause': 'If cause of lost is "other reason", must specify the reason'})
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        other_bidder = validated_data.pop('other_bidder', [])
        bidding = Bidding.objects.filter(id=validated_data.get('id', None)).first()
        BiddingCommonCreate.create_other_bidder(other_bidder=other_bidder, instance=bidding)
        bidding.bid_status = validated_data.get('bid_status', 0)
        bidding.cause_of_lost = validated_data.get('cause_of_lost', [])
        bidding.other_cause = validated_data.get('other_cause', '')
        bidding.save(update_fields=['bid_status', 'cause_of_lost', 'other_cause'])
        return bidding

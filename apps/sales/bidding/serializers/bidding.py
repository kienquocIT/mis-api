from rest_framework import serializers
from apps.core.hr.models import Employee
from apps.core.workflow.tasks import decorator_run_workflow
from apps.masterdata.saledata.models import Account, DocumentType
from apps.sales.bidding.models import Bidding, BiddingAttachment, BiddingDocument, BiddingPartnerAccount, \
    BiddingBidderAccount, BiddingResultConfigEmployee, BiddingResultConfig
from apps.sales.bidding.serializers.bidding_sub import BiddingCommonCreate
from apps.sales.opportunity.models import Opportunity
from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, AbstractListSerializerModel, \
    HRMsg, BaseMsg
from apps.shared.translations.base import AttachmentMsg
from apps.shared.translations.bidding import BiddingMsg
from apps.core.process.utils import ProcessRuntimeControl

class BiddingResultConfigListSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()

    class Meta:
        model = BiddingResultConfig
        fields = ('id', 'employee')

    @classmethod
    def get_employee(cls, obj):
        return [{
            'id': item.employee.id,
            'full_name': item.employee.get_full_name(),
        } for item in obj.bidding_result_config_employee_bid_config.all()]


class BiddingResultConfigCreateSerializer(serializers.ModelSerializer):
    employee = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = BiddingResultConfig
        fields = (
            'employee',
        )

    @classmethod
    def validate_employee(cls, value):
        for item in value:
            try:
                Employee.objects.get(id=item)
            except Employee.DoesNotExist:
                raise serializers.ValidationError({"employee": "Employee does not exist"})
        return value

    def create(self, validated_data):
        config = BiddingResultConfig.objects.create(**validated_data)
        bulk_info = []
        for employee in validated_data.get('employee', []):
            bulk_info.append(BiddingResultConfigEmployee(bidding_result_config=config, employee_id=employee))
        BiddingResultConfig.objects.filter(company_id=config.company_id).exclude(id=config.id).delete()
        BiddingResultConfigEmployee.objects.bulk_create(bulk_info)
        return config


class BiddingResultConfigDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiddingResultConfig
        fields = ('id',)


class BiddingDocumentCreateSerializer(serializers.ModelSerializer):
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
                raise serializers.ValidationError({'document_type': BaseMsg.NOT_EXIST})
        return None

    def validate(self, validate_data):
        attachment_data = validate_data.get('attachment_data')
        if not attachment_data:
            raise serializers.ValidationError({'attachment_data': BiddingMsg.ATTACHMENT_REQUIRED})
        return validate_data


class VenturePartnerCreateSerializer(serializers.ModelSerializer):
    partner_account = serializers.UUIDField()
    class Meta:
        model = BiddingPartnerAccount
        fields = (
            'order',
            'is_leader',
            'partner_account'
        )

    @classmethod
    def validate_partner_account(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'partner_account': BaseMsg.NOT_EXIST})


class OtherBidderCreateSerializer(serializers.ModelSerializer):
    bidder_account = serializers.UUIDField()

    class Meta:
        model = BiddingBidderAccount
        fields = (
            'order',
            'is_won',
            'bidder_account'
        )

    @classmethod
    def validate_bidder_account(cls, value):
        try:
            return Account.objects.get(id=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError({'bidder_account': BaseMsg.NOT_EXIST})


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
    process = serializers.SerializerMethodField()
    process_stage_app = serializers.SerializerMethodField()

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
            'attachment_m2m',
            'process',
            'process_stage_app',
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
                "isManual": not item.document_type,
                "remark": item.remark,
                "attachment_data": item.attachment_data,
                "order": item.order,
                "is_invite_doc": item.is_invite_doc,
            })
        return data

    @classmethod
    def get_process(cls, obj):
        if obj.process:
            return {
                'id': obj.process.id,
                'title': obj.process.title,
                'remark': obj.process.remark,
            }
        return {}

    @classmethod
    def get_process_stage_app(cls, obj):
        if obj.process_stage_app:
            return {
                'id': obj.process_stage_app.id,
                'title': obj.process_stage_app.title,
                'remark': obj.process_stage_app.remark,
            }
        return {}


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
    document_data = BiddingDocumentCreateSerializer(many=True, required=False)
    opportunity = serializers.UUIDField(
        required=True
    )
    bid_value = serializers.FloatField()
    bid_date = serializers.DateField()
    bid_bond_value = serializers.FloatField(required=False)
    venture_partner = VenturePartnerCreateSerializer(many=True, required=False)
    employee_inherit_id = serializers.UUIDField()
    security_type= serializers.IntegerField(required=False)
    process = serializers.UUIDField(allow_null=True, default=None, required=False)
    process_stage_app = serializers.UUIDField(allow_null=True, default=None, required=False)

    class Meta:
        model = Bidding
        fields = (
            'title',
            'attachment',
            'opportunity',
            'document_data',
            'venture_partner' ,
            'bid_value' ,
            'bid_bond_value',
            'security_type',
            'bid_date',
            'employee_inherit_id',
            'tinymce_content',
            'process',
            'process_stage_app',
        )

    @classmethod
    def validate_bid_value(cls, value):
        if value:
            if value < 0:
                raise serializers.ValidationError({'bid_value': BiddingMsg.BID_VALUE_NOT_NEGATIVE})
        return value

    @classmethod
    def validate_bid_bond_value(cls, value):
        if value:
            if value < 0:
                raise serializers.ValidationError({'bid_bond_value': BiddingMsg.BID_VALUE_NOT_NEGATIVE})
        return value

    @classmethod
    def validate_opportunity(cls, value):
        if value:
            try:
                return Opportunity.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            except Opportunity.DoesNotExist:
                raise serializers.ValidationError({'opportunity': BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({'opportunity': BaseMsg.REQUIRED})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            return Employee.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit': BaseMsg.NOT_EXIST})

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

    @classmethod
    def validate_process(cls, attrs):
        return ProcessRuntimeControl.get_process_obj(process_id=attrs) if attrs else None

    @classmethod
    def validate_process_stage_app(cls, attrs):
        return ProcessRuntimeControl.get_process_stage_app(
            stage_app_id=attrs, app_id=Bidding.get_app_id()
        ) if attrs else None


    def validate(self, validate_data):
        # Xử lý lấy nhân viên đang tạo để kiểm tra quyền trên Process
        employee_obj = validate_data.get('employee_inherit', None)
        if not employee_obj:
            raise serializers.ValidationError({
                'detail': 'Need employee information to check permission to create progress ticket'
            })

        if validate_data.get('opportunity'):
            validate_data['customer'] = validate_data.get('opportunity').customer
        bid_bond_value = validate_data.get('bid_bond_value', None)
        security_type = validate_data.get('security_type', 0)

        if bid_bond_value:
            if security_type == 0:
                raise serializers.ValidationError(
                    {'bid_bond_value': BiddingMsg.BID_SECURITY_TYPE_REQUIRED})

        process_obj = validate_data.get('process', None)
        process_stage_app_obj = validate_data.get('process_stage_app', None)
        opportunity_id = validate_data.get('opportunity_id', None)
        if process_obj:
            ProcessRuntimeControl(process_obj=process_obj).validate_process(
                process_stage_app_obj=process_stage_app_obj,
                employee_id=employee_obj.id,
                opp_id=opportunity_id,
            )
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        attachment = validated_data.pop('attachment', [])
        venture_partner = validated_data.pop('venture_partner', [])
        document_data = validated_data.pop('document_data', [])
        create_data = {
            'attachment': attachment,
            'venture_partner': venture_partner,
            'document_data': document_data,
        }
        bidding = Bidding.objects.create(**validated_data)
        BiddingCommonCreate.create_sub_models( instance=bidding, create_data= create_data)
        if bidding.process:
            ProcessRuntimeControl(process_obj=bidding.process).register_doc(
                process_stage_app_obj=bidding.process_stage_app,
                app_id=bidding.get_app_id(),
                doc_id=bidding.id,
                doc_title=bidding.title,
                employee_created_id=bidding.employee_created_id,
                date_created=bidding.date_created,
            )

        return bidding


class BiddingUpdateSerializer(AbstractCreateSerializerModel):
    title = serializers.CharField(max_length=100)
    attachment = serializers.ListSerializer(child=serializers.CharField(), required=False)
    document_data = BiddingDocumentCreateSerializer(many=True, required=False)
    opportunity = serializers.UUIDField(
        required=True
    )
    bid_value = serializers.FloatField()
    bid_date = serializers.DateField()
    bid_bond_value = serializers.FloatField(required=False)
    venture_partner = VenturePartnerCreateSerializer(many=True, required=False)
    employee_inherit_id = serializers.UUIDField()
    security_type = serializers.IntegerField(required=False)

    class Meta:
        model = Bidding
        fields = (
            'title',
            'attachment',
            'opportunity',
            'document_data',
            'venture_partner',
            'bid_value',
            'bid_bond_value',
            'security_type',
            'bid_date',
            'employee_inherit_id',
            'tinymce_content'
        )

    @classmethod
    def validate_bid_value(cls, value):
        if value:
            if value < 0:
                raise serializers.ValidationError({'bid_value': BiddingMsg.BID_VALUE_NOT_NEGATIVE})
        return value

    @classmethod
    def validate_bid_bond_value(cls, value):
        if value:
            if value < 0:
                raise serializers.ValidationError({'bid_bond_value': BiddingMsg.BID_VALUE_NOT_NEGATIVE})
        return value

    @classmethod
    def validate_opportunity(cls, value):
        if value:
            try:
                return Opportunity.objects.get_current(fill__tenant=True, fill__company=True, id=value)
            except Opportunity.DoesNotExist:
                raise serializers.ValidationError({'opportunity': BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({'opportunity': BaseMsg.REQUIRED})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            return Employee.objects.get_current(fill__tenant=True, fill__company=True, id=value).id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit': BaseMsg.NOT_EXIST})

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
        bid_bond_value = validate_data.get('bid_bond_value', None)
        security_type = validate_data.get('security_type', 0)
        if bid_bond_value:
            if security_type == 0:
                raise serializers.ValidationError(
                    {'bid_bond_value': BiddingMsg.BID_SECURITY_TYPE_REQUIRED})
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        attachment = validated_data.pop('attachment', [])
        venture_partner = validated_data.pop('venture_partner', [])
        document_data = validated_data.pop('document_data', [])
        update_data = {
            'attachment': attachment,
            'venture_partner': venture_partner,
            'document_data': document_data,
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
                raise serializers.ValidationError({'bidding': BaseMsg.NOT_EXIST})
        raise serializers.ValidationError({'bidding': BaseMsg.REQUIRED})

    def validate(self, validate_data):
        cause_of_lost = validate_data.get('cause_of_lost', [])
        other_cause = validate_data.get('other_cause', '')
        if validate_data.get('bid_status') == 2:  # bid lost
            if len(cause_of_lost) == 0:  # no cause of lost chosen
                raise serializers.ValidationError(
                    {'cause_of_lost': BiddingMsg.CAUSE_OF_LOST_REQUIRED})
        if '4' in cause_of_lost:  # other reason
            if not other_cause:
                raise serializers.ValidationError(
                    {'other_cause': BiddingMsg.OTHER_REASON_REQUIRED})
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        user = self.context.get('user', None)
        bid_result_config = BiddingResultConfig.objects.filter_current(fill__tenant=True, fill__company=True).first()
        bid_result_employee_list = bid_result_config.employee
        if str(user.employee_current_id) not in bid_result_employee_list:
            raise serializers.ValidationError({"bid_status": "User is not allowed to modify bid result"})
        other_bidder = validated_data.pop('other_bidder', [])
        bidding = Bidding.objects.filter(id=validated_data.get('id', None)).first()
        BiddingCommonCreate.create_other_bidder(other_bidder=other_bidder, instance=bidding)
        bidding.bid_status = validated_data.get('bid_status', 0)
        bidding.cause_of_lost = validated_data.get('cause_of_lost', [])
        bidding.other_cause = validated_data.get('other_cause', '')
        bidding.save(update_fields=['bid_status', 'cause_of_lost', 'other_cause'])
        return bidding

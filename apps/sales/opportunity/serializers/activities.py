# pylint: disable=C0302
import logging
from rest_framework import serializers
from django.core.mail import get_connection, EmailMultiAlternatives
from apps.core.attachments.models import Files
from apps.core.base.models import Application
from apps.core.hr.models import Employee
from apps.core.process.utils import ProcessRuntimeControl
from apps.masterdata.saledata.models import Contact
from apps.masterdata.saledata.models.accounts import AccountActivity
from apps.sales.opportunity.models import (
    OpportunityCallLog, OpportunityEmail, OpportunityMeeting,
    OpportunityMeetingEmployeeAttended, OpportunityMeetingCustomerMember, OpportunitySubDocument,
    OpportunityDocumentPersonInCharge, OpportunityDocument, OpportunityActivityLogTask,
    OpportunityActivityLogs, OpportunitySaleTeamMember, Opportunity
)
from apps.sales.opportunity.msg import OpportunityOnlyMsg
from apps.shared import BaseMsg, SaleMsg, HrMsg, SimpleEncryptor
from misapi import settings

logger = logging.getLogger(__name__)


# Activity: Call log
class OpportunityCallLogListSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    process_stage_app = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityCallLog
        fields = (
            'id',
            'subject',
            'opportunity',
            'employee_inherit',
            'contact',
            'call_date',
            'input_result',
            'repeat',
            'is_cancelled',
            'process',
            'process_stage_app'
        )

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
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'first_name': obj.employee_inherit.first_name,
            'last_name': obj.employee_inherit.last_name,
            'email': obj.employee_inherit.email,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
            'is_active': obj.employee_inherit.is_active,
            'group': {
                'id': obj.employee_inherit.group_id,
                'title': obj.employee_inherit.group.title,
                'code': obj.employee_inherit.group.code
            } if obj.employee_inherit.group else {}
        } if obj.employee_inherit else {}

    @classmethod
    def get_contact(cls, obj):
        return {
            'id': obj.contact_id,
            'fullname': obj.contact.fullname
        } if obj.contact else {}

    @classmethod
    def get_process_stage_app(cls, obj):
        if obj.process_stage_app:
            return {
                'id': obj.process_stage_app.id,
                'title': obj.process_stage_app.title,
                'remark': obj.process_stage_app.remark,
            }
        return {}

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'code': obj.opportunity.code,
            'title': obj.opportunity.title,
            'customer': {
                'id': obj.opportunity.customer_id,
                'code': obj.opportunity.customer.code,
                'title': obj.opportunity.customer.name
            } if obj.opportunity.customer else {}
        } if obj.opportunity else {}


class OpportunityCallLogCreateSerializer(serializers.ModelSerializer):
    opportunity_id = serializers.UUIDField()
    employee_inherit_id = serializers.UUIDField(required=False, allow_null=True)
    input_result = serializers.CharField(required=True)
    process = serializers.UUIDField(required=False, allow_null=True, default=None)
    process_stage_app = serializers.UUIDField(allow_null=True, default=None, required=False)

    @classmethod
    def validate_process(cls, attrs):
        return ProcessRuntimeControl.get_process_obj(process_id=attrs) if attrs else None

    @classmethod
    def validate_process_stage_app(cls, attrs):
        return ProcessRuntimeControl.get_process_stage_app(
            stage_app_id=attrs, app_id=OpportunityCallLog.get_app_id()
        ) if attrs else None

    class Meta:
        model = OpportunityCallLog
        fields = (
            'subject',
            'opportunity_id',
            'employee_inherit_id',
            'contact',
            'call_date',
            'input_result',
            'repeat',
            'process',
            'process_stage_app',
        )

    @classmethod
    def validate_opportunity_id(cls, value):
        try:
            opportunity_obj = Opportunity.objects.get(id=value)
            if opportunity_obj.is_close_lost or opportunity_obj.is_deal_close:
                raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
            return opportunity_obj.id
        except Opportunity.DoesNotExist:
            raise serializers.ValidationError({'opportunity_id': OpportunityOnlyMsg.OPP_NOT_EXIST})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            employee_inherit = Employee.objects.get(id=value)
            return employee_inherit.id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit_id': OpportunityOnlyMsg.EMP_NOT_EXIST})

    @classmethod
    def validate_input_result(cls, value):
        if value:
            return value
        raise serializers.ValidationError({'detail': OpportunityOnlyMsg.RESULT_NOT_NULL})

    def validate(self, validate_data):
        process_obj = validate_data.get('process', None)
        process_stage_app_obj = validate_data.get('process_stage_app', None)
        if process_obj:
            process_cls = ProcessRuntimeControl(process_obj=process_obj)
            process_cls.validate_process(
                process_stage_app_obj=process_stage_app_obj,
                opp_id=validate_data['opportunity_id']
            )
        validate_data['title'] = f"Call log: {validate_data.get('subject', '')}"
        return validate_data

    def create(self, validated_data):
        call_log_obj = OpportunityCallLog.objects.create(**validated_data)
        OpportunityActivityLogs.objects.create(
            tenant=call_log_obj.tenant,
            company=call_log_obj.company,
            call=call_log_obj,
            opportunity_id=validated_data['opportunity_id'],
            date_created=validated_data['call_date'],
            log_type=2,
        )
        if call_log_obj.process:
            ProcessRuntimeControl(process_obj=call_log_obj.process).register_doc(
                process_stage_app_obj=call_log_obj.process_stage_app,
                app_id=OpportunityCallLog.get_app_id(),
                doc_id=call_log_obj.id,
                doc_title=call_log_obj.title,
                employee_created_id=call_log_obj.employee_created_id,
                date_created=call_log_obj.date_created,
            )
        return call_log_obj


class OpportunityCallLogDetailSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField() # noqa
    contact = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    process_stage_app = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityCallLog
        fields = (
            'id',
            'subject',
            'opportunity',
            'contact',
            'call_date',
            'input_result',
            'repeat',
            'is_cancelled',
            # process
            'process',
            'process_stage_app',
        )

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

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'code': obj.opportunity.code,
            'title': obj.opportunity.title,
            'customer': {
                'id': obj.opportunity.customer_id,
                'code': obj.opportunity.customer.code,
                'title': obj.opportunity.customer.name
            } if obj.opportunity.customer else {}
        } if obj.opportunity else {}

    @classmethod
    def get_contact(cls, obj):
        return {
            'id': obj.contact_id,
            'fullname': obj.contact.fullname
        } if obj.contact else {}


class OpportunityCallLogUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityCallLog
        fields = ('is_cancelled',)

    def validate(self, validate_data):
        if self.instance.is_cancelled is True:
            raise serializers.ValidationError({'Cancelled': SaleMsg.CAN_NOT_REACTIVE})
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        OpportunityActivityLogs.objects.filter(call=instance).update(is_cancelled=instance.is_cancelled)
        return instance


# Activity: Email
class OpportunityEmailListSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()

    @classmethod
    def get_process(cls, obj):
        if obj.process:
            return {
                'id': obj.process.id,
                'title': obj.process.title,
                'remark': obj.process.remark,
            }
        return {}

    class Meta:
        model = OpportunityEmail
        fields = (
            'id',
            'subject',
            'email_to_list',
            'email_cc_list',
            'content',
            'date_created',
            'opportunity',
            'process',
        )

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'code': obj.opportunity.code,
            'title': obj.opportunity.title
        } if obj.opportunity else {}


class OpportunityEmailCreateSerializer(serializers.ModelSerializer):
    opportunity_id = serializers.UUIDField()
    employee_inherit_id = serializers.UUIDField()
    content = serializers.CharField(required=True)
    process = serializers.UUIDField(allow_null=True, default=None, required=False)
    process_stage_app = serializers.UUIDField(allow_null=True, default=None, required=False)

    @classmethod
    def validate_process(cls, attrs):
        return ProcessRuntimeControl.get_process_obj(process_id=attrs) if attrs else None

    @classmethod
    def validate_process_stage_app(cls, attrs):
        return ProcessRuntimeControl.get_process_stage_app(
            stage_app_id=attrs, app_id=OpportunityEmail.get_app_id()
        ) if attrs else None

    class Meta:
        model = OpportunityEmail
        fields = (
            'subject',
            'email_to_list',
            'email_cc_list',
            'content',
            'opportunity_id',
            'employee_inherit_id',
            'process',
            'process_stage_app',
        )

    @classmethod
    def validate_opportunity_id(cls, value):
        try:
            opportunity_obj = Opportunity.objects.get(id=value)
            if opportunity_obj.is_close_lost or opportunity_obj.is_deal_close:
                raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
            return opportunity_obj.id
        except Opportunity.DoesNotExist:
            raise serializers.ValidationError({'opportunity_id': OpportunityOnlyMsg.OPP_NOT_EXIST})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            employee_inherit = Employee.objects.get(id=value)
            return employee_inherit.id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit_id': OpportunityOnlyMsg.EMP_NOT_EXIST})

    @classmethod
    def validate_content(cls, value):
        if value:
            return value
        raise serializers.ValidationError({'detail': OpportunityOnlyMsg.CONTENT_NOT_NULL})

    @classmethod
    def validate_email_to_list(cls, value):
        if value:
            return value
        raise serializers.ValidationError({'Email to list': 'Missing to list'})

    @classmethod
    def validate_email_cc_list(cls, value):
        return value

    def validate(self, validate_data):
        process_obj = validate_data.get('process', None)
        process_stage_app_obj = validate_data.get('process_stage_app', None)
        if process_obj:
            process_cls = ProcessRuntimeControl(process_obj=process_obj)
            process_cls.validate_process(
                process_stage_app_obj=process_stage_app_obj,
                opp_id=validate_data['opportunity_id']
            )
        validate_data['title'] = f"Email: {validate_data.get('subject', '')}"
        return validate_data

    def create(self, validated_data):
        email_obj = OpportunityEmail.objects.create(**validated_data)
        ActivitiesCommonFunc.send_email(email_obj, self.context.get('employee_current'))
        OpportunityActivityLogs.objects.create(
            tenant=email_obj.tenant,
            company=email_obj.company,
            email=email_obj,
            opportunity_id=validated_data['opportunity_id'],
            log_type=3,
        )
        if email_obj.process:
            ProcessRuntimeControl(process_obj=email_obj.process).register_doc(
                process_stage_app_obj=email_obj.process_stage_app,
                app_id=OpportunityEmail.get_app_id(),
                doc_id=email_obj.id,
                doc_title=email_obj.title,
                employee_created_id=email_obj.employee_created_id,
                date_created=email_obj.date_created,
            )
        return email_obj


class OpportunityEmailDetailSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    process_stage_app = serializers.SerializerMethodField()

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

    class Meta:
        model = OpportunityEmail
        fields = (
            'id',
            'subject',
            'email_to_list',
            'email_cc_list',
            'content',
            'date_created',
            'opportunity',
            'process',
            'process_stage_app',
        )

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'code': obj.opportunity.code,
            'title': obj.opportunity.title
        } if obj.opportunity else {}


class OpportunityEmailUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpportunityEmail
        fields = ()


# Activity: Meeting
class OpportunityMeetingListSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()
    employee_attended_list = serializers.SerializerMethodField()
    customer_member_list = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    process_stage_app = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityMeeting
        fields = (
            'id',
            'subject',
            'opportunity',
            'employee_inherit',
            'employee_attended_list',
            'customer_member_list',
            'meeting_date',
            'meeting_from_time',
            'meeting_to_time',
            'meeting_address',
            'room_location',
            'input_result',
            'repeat',
            'is_cancelled',
            'process',
            'process_stage_app'
        )

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'code': obj.opportunity.code,
            'title': obj.opportunity.title
        } if obj.opportunity else {}

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            'id': obj.employee_inherit_id,
            'first_name': obj.employee_inherit.first_name,
            'last_name': obj.employee_inherit.last_name,
            'email': obj.employee_inherit.email,
            'full_name': obj.employee_inherit.get_full_name(2),
            'code': obj.employee_inherit.code,
            'is_active': obj.employee_inherit.is_active,
            'group': {
                'id': obj.employee_inherit.group_id,
                'title': obj.employee_inherit.group.title,
                'code': obj.employee_inherit.group.code
            } if obj.employee_inherit.group else {}
        } if obj.employee_inherit else {}

    @classmethod
    def get_employee_attended_list(cls, obj):
        employee_attended_list = []
        for item in list(obj.employee_attended_list.all()):
            employee_attended_list.append({'id': item.id, 'code': item.code, 'fullname': item.get_full_name(2)})
        return employee_attended_list

    @classmethod
    def get_customer_member_list(cls, obj):
        customer_member_list = []
        for item in list(obj.customer_member_list.all()):
            customer_member_list.append({'id': item.id, 'fullname': item.fullname})
        return customer_member_list

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


class SubEmployeeMemberDetailSerializer(serializers.Serializer):  # noqa
    id = serializers.UUIDField()
    fullname = serializers.CharField()


class OpportunityMeetingCreateSerializer(serializers.ModelSerializer):
    opportunity_id = serializers.UUIDField()
    employee_inherit_id = serializers.UUIDField()
    input_result = serializers.CharField(required=True)
    meeting_from_time = serializers.TimeField(required=True)
    meeting_to_time = serializers.TimeField(required=True)
    employee_attended_list = serializers.ListField(
        child=SubEmployeeMemberDetailSerializer(), min_length=1,
    )
    customer_member_list = serializers.ListField(
        child=SubEmployeeMemberDetailSerializer(),
        allow_empty=True, default=[], required=False,
    )
    process = serializers.UUIDField(allow_null=True, default=None, required=False)
    process_stage_app = serializers.UUIDField(allow_null=True, default=None, required=False)

    @classmethod
    def validate_process(cls, attrs):
        return ProcessRuntimeControl.get_process_obj(process_id=attrs) if attrs else None

    @classmethod
    def validate_process_stage_app(cls, attrs):
        return ProcessRuntimeControl.get_process_stage_app(
            stage_app_id=attrs, app_id=OpportunityMeeting.get_app_id()
        ) if attrs else None

    class Meta:
        model = OpportunityMeeting
        fields = (
            'subject',
            'opportunity_id',
            'employee_inherit_id',
            'employee_attended_list',
            'customer_member_list',
            'meeting_date',
            'meeting_from_time',
            'meeting_to_time',
            'meeting_address',
            'room_location',
            'input_result',
            'repeat',
            'process',
            'process_stage_app',
        )

    @classmethod
    def validate_opportunity_id(cls, value):
        try:
            opportunity_obj = Opportunity.objects.get(id=value)
            if opportunity_obj.is_close_lost or opportunity_obj.is_deal_close:
                raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
            return opportunity_obj.id
        except Opportunity.DoesNotExist:
            raise serializers.ValidationError({'opportunity_id': OpportunityOnlyMsg.OPP_NOT_EXIST})

    @classmethod
    def validate_employee_inherit_id(cls, value):
        try:
            employee_inherit = Employee.objects.get(id=value)
            return employee_inherit.id
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'employee_inherit_id': OpportunityOnlyMsg.EMP_NOT_EXIST})

    @classmethod
    def validate_input_result(cls, value):
        if value:
            return value
        raise serializers.ValidationError({'detail': OpportunityOnlyMsg.RESULT_NOT_NULL})

    @classmethod
    def validate_employee_attended_list(cls, attrs):
        ids = [item.get('id') for item in attrs]
        amount = Employee.objects.filter_current(fill__tenant=True, fill__company=True, id__in=ids).count()
        if amount != len(attrs):
            raise serializers.ValidationError({'employee': OpportunityOnlyMsg.EMP_NOT_EXIST})
        return attrs

    @classmethod
    def validate_customer_member_list(cls, attrs):
        ids = [item.get('id') for item in attrs]
        amount = Contact.objects.filter_current(fill__tenant=True, fill__company=True, id__in=ids).count()
        if amount != len(attrs):
            raise serializers.ValidationError({'employee': OpportunityOnlyMsg.EMP_NOT_EXIST})
        return attrs

    def validate(self, validate_data):
        if validate_data.get('meeting_from_time') and validate_data.get('meeting_to_time'):
            if validate_data['meeting_from_time'] >= validate_data['meeting_to_time']:
                raise serializers.ValidationError({'detail': SaleMsg.WRONG_TIME})

        process_obj = validate_data.get('process', None)
        process_stage_app_obj = validate_data.get('process_stage_app', None)
        if process_obj:
            process_cls = ProcessRuntimeControl(process_obj=process_obj)
            process_cls.validate_process(
                process_stage_app_obj=process_stage_app_obj,
                opp_id=validate_data['opportunity_id']
            )
        validate_data['title'] = f"Meeting: {validate_data.get('subject', '')}"
        return validate_data

    def create(self, validated_data):
        employee_attended_list = validated_data.pop('employee_attended_list')
        customer_member_list = validated_data.pop('customer_member_list')
        meeting_obj = OpportunityMeeting.objects.create(**validated_data)
        ActivitiesCommonFunc.create_employee_attended_map_meeting(meeting_obj, employee_attended_list)
        ActivitiesCommonFunc.create_customer_member_map_meeting(meeting_obj, customer_member_list)
        OpportunityActivityLogs.objects.create(
            tenant=meeting_obj.tenant,
            company=meeting_obj.company,
            meeting=meeting_obj,
            opportunity_id=validated_data['opportunity_id'],
            date_created=validated_data['meeting_date'],
            log_type=4,
        )
        # push to customer activity
        if meeting_obj.opportunity:
            if meeting_obj.opportunity.customer:
                AccountActivity.push_activity(
                    tenant_id=meeting_obj.opportunity.tenant_id,
                    company_id=meeting_obj.opportunity.company_id,
                    account_id=meeting_obj.opportunity.customer_id,
                    app_code=meeting_obj._meta.label_lower,
                    document_id=meeting_obj.id,
                    title=meeting_obj.subject,
                    code='',
                    date_activity=meeting_obj.meeting_date,
                    revenue=None,
                )

        if meeting_obj.process:
            ProcessRuntimeControl(process_obj=meeting_obj.process).register_doc(
                process_stage_app_obj=meeting_obj.process_stage_app,
                app_id=OpportunityMeeting.get_app_id(),
                doc_id=meeting_obj.id,
                doc_title=meeting_obj.title,
                employee_created_id=meeting_obj.employee_created_id,
                date_created=meeting_obj.date_created,
            )

        return meeting_obj


class OpportunityMeetingDetailSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    employee_attended_list = serializers.SerializerMethodField()
    customer_member_list = serializers.SerializerMethodField()
    process = serializers.SerializerMethodField()
    process_stage_app = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityMeeting
        fields = (
            'id',
            'subject',
            'opportunity',
            'employee_attended_list',
            'customer_member_list',
            'meeting_date',
            'meeting_from_time',
            'meeting_to_time',
            'meeting_address',
            'room_location',
            'input_result',
            'repeat',
            'is_cancelled',
            # process
            'process',
            'process_stage_app',
        )

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

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'code': obj.opportunity.code,
            'title': obj.opportunity.title
        } if obj.opportunity else {}

    @classmethod
    def get_employee_attended_list(cls, obj):
        if obj.employee_attended_list:
            employee_attended_list = []
            for item in list(obj.employee_attended_list.all()):
                employee_attended_list.append({'id': item.id, 'code': item.code, 'fullname': item.get_full_name(2)})
            return employee_attended_list
        return {}

    @classmethod
    def get_customer_member_list(cls, obj):
        if obj.customer_member_list:
            customer_member_list = []
            for item in list(obj.customer_member_list.all()):
                customer_member_list.append({'id': item.id, 'fullname': item.fullname})
            return customer_member_list
        return {}


class OpportunityMeetingUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpportunityMeeting
        fields = ('is_cancelled',)

    def validate(self, validate_data):
        if self.instance.is_cancelled is True:
            raise serializers.ValidationError({'Cancelled': SaleMsg.CAN_NOT_REACTIVE})
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        OpportunityActivityLogs.objects.filter(meeting=instance).update(is_cancelled=instance.is_cancelled)
        return instance


# Activity: Document
class OpportunityDocumentListSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    person_in_charge = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityDocument
        fields = (
            'id',
            'opportunity',
            'title',
            'person_in_charge',
            'request_completed_date',
        )

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity.id,
            'code': obj.opportunity.code,
            'title': obj.opportunity.title
        } if obj.opportunity else {}

    @classmethod
    def get_person_in_charge(cls, obj):
        if obj.person_in_charge:
            persons = obj.person_in_charge.all()
            list_result = []
            for person in persons:
                list_result.append({
                    'id': person.id,
                    'full_name': person.get_full_name()
                })
            return list_result
        return []


class OpportunityDocumentCreateSerializer(serializers.ModelSerializer):
    person_in_charge = serializers.ListField(child=serializers.UUIDField())

    class Meta:
        model = OpportunityDocument
        fields = (
            'title',
            'opportunity',
            'request_completed_date',
            'description',
            'data_documents',
            'person_in_charge'
        )

    @classmethod
    def validate_person_in_charge(cls, value):
        if not value:
            raise serializers.ValidationError({'person_in_charge': OpportunityOnlyMsg.PIC_NOT_NULL})
        return value

    @classmethod
    def create_sub_document(cls, user, instance, data):
        relate_app = Application.objects.get(id="319356b4-f16c-4ba4-bdcb-e1b0c2a2c124")
        instance_id = str(instance.id)
        employee_id = getattr(user, 'employee_current_id', None)
        if not employee_id:
            raise serializers.ValidationError({'User': HrMsg.EMPLOYEE_WAS_LINKED})

        bulk_data = []
        for doc in data:
            if not doc['attachment']:
                return False
            state, att_objs = Files.check_media_file(
                file_ids=doc['attachment'], employee_id=employee_id, doc_id=instance_id,
            )
            if state:
                file_objs = Files.regis_media_file(
                    relate_app=relate_app, relate_doc_id=instance_id, file_objs_or_ids=att_objs
                )
                for obj in file_objs:
                    bulk_data.append(OpportunitySubDocument(
                        document=instance,
                        attachment=obj,
                        description=doc['description']
                    ))
            else:
                raise serializers.ValidationError({'Attachment': BaseMsg.UPLOAD_FILE_ERROR})
        OpportunitySubDocument.objects.bulk_create(bulk_data)
        return True

    @classmethod
    def create_person_in_charge(cls, data, instance):
        bulk_data = [OpportunityDocumentPersonInCharge(
            person_id=person_id,
            document=instance,
        ) for person_id in data]
        OpportunityDocumentPersonInCharge.objects.bulk_create(bulk_data)
        return True

    def validate(self, validate_data):
        if validate_data.get('opportunity', None):
            if validate_data['opportunity'].is_close_lost is True or validate_data['opportunity'].is_deal_close:
                raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
            if not ActivitiesCommonFunc.check_permission_in_opp(
                    self.context.get('employee_id'), validate_data['opportunity']
            ):
                raise serializers.ValidationError({'Create failed': OpportunityOnlyMsg.DONT_HAVE_PERMISSION})
        return validate_data

    def create(self, validated_data):
        user = self.context.get('user', None)
        data_documents = validated_data.get('data_documents', [])
        data_person_in_charge = validated_data.pop('person_in_charge')
        instance = OpportunityDocument.objects.create(**validated_data)
        if instance:
            self.create_person_in_charge(data_person_in_charge, instance)
            self.create_sub_document(user, instance, data_documents)
            OpportunityActivityLogs.objects.create(
                document=instance,
                opportunity=validated_data['opportunity'],
                date_created=validated_data['request_completed_date'],
                log_type=5,
            )
        return instance


class OpportunityDocumentDetailSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()
    person_in_charge = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityDocument
        fields = (
            'title',
            'opportunity',
            'request_completed_date',
            'description',
            'data_documents',
            'person_in_charge',
            'files',
        )

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'title': obj.opportunity.title
        } if obj.opportunity else {}

    @classmethod
    def get_person_in_charge(cls, obj):
        if obj.person_in_charge:
            persons = obj.person_in_charge.all()
            list_result = []
            for person in persons:
                list_result.append({
                    'id': person.id,
                    'full_name': person.get_full_name()
                })
            return list_result
        return []

    @classmethod
    def get_files(cls, obj):
        file = OpportunitySubDocument.objects.select_related('attachment').filter(document=obj)
        if file.exists():  # noqa
            attachments = []
            for item in file:
                files = item.attachment
                attachments.append({
                    "id": str(files.id),
                    "relate_app_id": str(files.relate_app_id),
                    "relate_app_code": files.relate_app_code,
                    "relate_doc_id": str(files.relate_doc_id),
                    "media_file_id": str(files.media_file_id),
                    "file_name": files.file_name,
                    "file_size": int(files.file_size),
                    "file_type": files.file_type
                })
            return attachments
        return []


# Activity: Logging
class OpportunityActivityLogTaskListSerializer(serializers.ModelSerializer):
    task = serializers.SerializerMethodField()

    @classmethod
    def get_task(cls, obj):
        return {
            'id': obj.task.id,
            'title': obj.task.title,
            'code': obj.task.code
        } if obj.task else {}

    class Meta:
        model = OpportunityActivityLogTask
        fields = (
            'subject',
            'task',
            'activity_name',
            'activity_type',
            'date_created'
        )


class OpportunityActivityLogsListSerializer(serializers.ModelSerializer):
    task = serializers.SerializerMethodField()
    call_log = serializers.SerializerMethodField()
    meeting = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    document = serializers.SerializerMethodField()

    @classmethod
    def get_task(cls, obj):
        return {
            'subject': obj.task.subject,
            'id': str(obj.task.task_id),
            'activity_name': obj.task.activity_name,
            'activity_type': obj.task.activity_type,
        } if obj.task else {}

    @classmethod
    def get_call_log(cls, obj):
        return {
            'subject': obj.call.subject,
            'id': str(obj.call_id),
            'activity_name': 'Call to customer',
            'activity_type': 'call',
            'is_cancelled': obj.call.is_cancelled
        } if obj.call else {}

    @classmethod
    def get_meeting(cls, obj):
        return {
            'subject': obj.meeting.subject,
            'id': str(obj.meeting_id),
            'activity_name': 'Meeting with customer',
            'activity_type': 'meeting',
            'is_cancelled': obj.meeting.is_cancelled
        } if obj.meeting else {}

    @classmethod
    def get_email(cls, obj):
        return {
            'subject': obj.email.subject,
            'id': str(obj.email_id),
            'activity_name': 'Send email',
            'activity_type': 'email',
        } if obj.email else {}

    @classmethod
    def get_document(cls, obj):
        return {
            'subject': obj.document.subject,
            'id': str(obj.document_id),
            'activity_name': 'Upload document',
            'activity_type': 'document',
        } if obj.document else {}

    class Meta:
        model = OpportunityActivityLogs
        fields = (
            'call_log',
            'email',
            'meeting',
            'document',
            'task',
            'date_created',
            'app_code',
            'doc_id',
            'title',
            'log_type',
            'doc_data',
        )


class ActivitiesCommonFunc:
    @staticmethod
    def check_permission_in_opp(employee_id, opportunity_obj):
        is_team_members = OpportunitySaleTeamMember.objects.filter(
            opportunity=opportunity_obj, member_id=employee_id
        ).exists()
        is_inherit = opportunity_obj.employee_inherit_id == employee_id
        return (is_team_members + is_inherit) > 0

    @staticmethod
    def send_email(email_obj, employee_created):
        if settings.EMAIL_SERVER_DEFAULT_HOST:
            try:
                html_content = email_obj.content
                email = EmailMultiAlternatives(
                    subject=email_obj.subject,
                    body='',
                    from_email=employee_created.email,
                    to=email_obj.email_to_list,
                    cc=email_obj.email_cc_list,
                    bcc=[],
                    reply_to=[],
                )
                email.attach_alternative(html_content, "text/html")
                password = SimpleEncryptor().generate_key(password=settings.EMAIL_CONFIG_PASSWORD)
                connection = get_connection(
                    username=employee_created.email,
                    password=SimpleEncryptor(key=password).decrypt(employee_created.email_app_password),
                    fail_silently=False,
                )
                email.connection = connection
                email.send()
                return True
            except Exception as err:
                logger.error('[ActivitiesCommonFunc][send_email] Err: %s', str(err))
                employee_created.email_app_password_status = False
                employee_created.save(update_fields=['email_app_password_status'])
            raise serializers.ValidationError({
                'Send email': "Cannot send email. Try to verify your Email in Employee update page."
            })
        return False

    @staticmethod
    def create_employee_attended_map_meeting(meeting_id, employee_attended_list):
        bulk_info = []
        for employee_attended_item in employee_attended_list:
            bulk_info.append(
                OpportunityMeetingEmployeeAttended(
                    meeting_mapped=meeting_id,
                    employee_attended_mapped_id=employee_attended_item['id']
                )
            )
        OpportunityMeetingEmployeeAttended.objects.filter(meeting_mapped=meeting_id).delete()
        OpportunityMeetingEmployeeAttended.objects.bulk_create(bulk_info)
        return True

    @staticmethod
    def create_customer_member_map_meeting(meeting_id, customer_member_list):
        bulk_info = []
        for customer_member_item in customer_member_list:
            bulk_info.append(
                OpportunityMeetingCustomerMember(
                    meeting_mapped=meeting_id,
                    customer_member_mapped_id=customer_member_item['id']
                )
            )
        OpportunityMeetingCustomerMember.objects.filter(meeting_mapped=meeting_id).delete()
        OpportunityMeetingCustomerMember.objects.bulk_create(bulk_info)
        return True

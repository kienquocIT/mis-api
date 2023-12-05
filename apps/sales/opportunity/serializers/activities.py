from rest_framework import serializers

from apps.core.attachments.models import Files
from apps.core.base.models import Application
from apps.sales.opportunity.models import (
    OpportunityCallLog, OpportunityEmail, OpportunityMeeting,
    OpportunityMeetingEmployeeAttended, OpportunityMeetingCustomerMember, OpportunitySubDocument,
    OpportunityDocumentPersonInCharge, OpportunityDocument, OpportunityActivityLogTask,
    OpportunityActivityLogs
)
from apps.shared import BaseMsg, SaleMsg
from apps.shared.translations.opportunity import OpportunityMsg
from apps.shared.mail import GmailController


class OpportunityCallLogListSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityCallLog
        fields = (
            'id',
            'subject',
            'opportunity',
            'contact',
            'call_date',
            'input_result',
            'repeat'
        )

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


class OpportunityCallLogCreateSerializer(serializers.ModelSerializer):
    input_result = serializers.CharField(required=True)

    class Meta:
        model = OpportunityCallLog
        fields = (
            'subject',
            'opportunity',
            'contact',
            'call_date',
            'input_result',
            'repeat'
        )

    @classmethod
    def validate_input_result(cls, value):
        if value:
            return value
        raise serializers.ValidationError({'detail': OpportunityMsg.ACTIVITIES_CALL_LOG_RESULT_NOT_NULL})

    def validate(self, validate_data):
        if validate_data.get('opportunity', None):
            if validate_data['opportunity'].is_close_lost is True or validate_data['opportunity'].is_deal_close:
                raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
        return validate_data

    def create(self, validated_data):
        call_log_obj = OpportunityCallLog.objects.create(**validated_data)
        OpportunityActivityLogs.objects.create(
            call=call_log_obj,
            opportunity=validated_data['opportunity'],
            date_created=validated_data['call_date']
        )
        return call_log_obj


class OpportunityCallLogDetailSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField() # noqa
    contact = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityCallLog
        fields = (
            'id',
            'subject',
            'opportunity',
            'contact',
            'call_date',
            'input_result',
            'repeat'
        )

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


class OpportunityEmailListSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()

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
        )

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'code': obj.opportunity.code,
            'title': obj.opportunity.title
        } if obj.opportunity else {}


def send_email(email_obj, employee_id, tenant_id, company_id):
    try:
        template = f"<table><tr><td><h1>{email_obj.subject}</h1></td><td>{email_obj.content}</td></tr></table>"
        GmailController(
            subject=email_obj.subject,
            to=email_obj.email_to,
            cc=email_obj.email_cc_list,
            bcc=[],
            template=template,
            context=email_obj.content,
            tenant_id=tenant_id,
            company_id=company_id,
            employee_id=employee_id,
        ).send()
        return True
    except Exception as err:
        print(err)
    return False


class OpportunityEmailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityEmail
        fields = (
            'subject',
            'email_to_list',
            'email_cc_list',
            'content',
            'opportunity',
        )

    @classmethod
    def validate_email_to_list(cls, value):
        return value

    @classmethod
    def validate_email_cc_list(cls, value):
        return value

    def validate(self, validate_data):
        if validate_data.get('opportunity', None):
            if validate_data['opportunity'].is_close_lost is True or validate_data['opportunity'].is_deal_close:
                raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
        return validate_data

    def create(self, validated_data):
        email_obj = OpportunityEmail.objects.create(**validated_data)

        # employee_id = self.context.get('employee_id', None)
        # tenant_id = self.context.get('tenant_id', None)
        # company_id = self.context.get('company_id', None)
        # send_mail_state = send_email(email_obj, employee_id, tenant_id, company_id)
        # if not send_mail_state:
        #     raise serializers.ValidationError({'Email': OpportunityMsg.CAN_NOT_SEND_EMAIL})
        OpportunityActivityLogs.objects.create(
            email=email_obj,
            opportunity=validated_data['opportunity'],
        )
        return email_obj


class OpportunityEmailDetailSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()

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
        )

    @classmethod
    def get_opportunity(cls, obj):
        return {
            'id': obj.opportunity_id,
            'code': obj.opportunity.code,
            'title': obj.opportunity.title
        } if obj.opportunity else {}


class OpportunityMeetingListSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    employee_attended_list = serializers.SerializerMethodField()
    customer_member_list = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityMeeting
        fields = (
            'id',
            'subject',
            'opportunity',
            'employee_attended_list',
            'customer_member_list',
            'meeting_date',
            'meeting_address',
            'room_location',
            'input_result',
            'repeat'
        )

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


class OpportunityMeetingCreateSerializer(serializers.ModelSerializer):
    input_result = serializers.CharField(required=True)

    class Meta:
        model = OpportunityMeeting
        fields = (
            'subject',
            'opportunity',
            'employee_attended_list',
            'customer_member_list',
            'meeting_date',
            'meeting_address',
            'room_location',
            'input_result',
            'repeat'
        )

    @classmethod
    def validate_input_result(cls, value):
        if value:
            return value
        raise serializers.ValidationError({'detail': OpportunityMsg.ACTIVITIES_MEETING_RESULT_NOT_NULL})

    def validate(self, validate_data):
        if validate_data.get('opportunity', None):
            if validate_data['opportunity'].is_close_lost is True or validate_data['opportunity'].is_deal_close:
                raise serializers.ValidationError({'detail': SaleMsg.OPPORTUNITY_CLOSED})
        return validate_data

    def create(self, validated_data):
        meeting_obj = OpportunityMeeting.objects.create(**validated_data)
        create_employee_attended_map_meeting(meeting_obj, self.initial_data.get('employee_attended_list', []))
        create_customer_member_map_meeting(meeting_obj, self.initial_data.get('customer_member_list', []))
        OpportunityActivityLogs.objects.create(
            meeting=meeting_obj,
            opportunity=validated_data['opportunity'],
            date_created=validated_data['meeting_date']
        )
        return meeting_obj


class OpportunityMeetingDetailSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    employee_attended_list = serializers.SerializerMethodField()
    customer_member_list = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityMeeting
        fields = (
            'id',
            'subject',
            'opportunity',
            'employee_attended_list',
            'customer_member_list',
            'meeting_date',
            'meeting_address',
            'room_location',
            'input_result',
            'repeat'
        )

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
                list_result.append(
                    {
                        'id': person.id,
                        'full_name': person.get_full_name()
                    }
                )
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
            raise serializers.ValidationError({'person_in_charge': OpportunityMsg.NOT_BLANK})
        return value

    @classmethod
    def create_sub_document(cls, user, instance, data):
        # attachments: list -> danh s?ch id t? cloud tr? v?, t?m th?i chi c? 1 n?n l?y [0]
        relate_app = Application.objects.get(id="319356b4-f16c-4ba4-bdcb-e1b0c2a2c124")
        relate_app_code = 'documentforcustomer'
        instance_id = str(instance.id)
        if not user.employee_current:
            raise serializers.ValidationError(
                {'User': BaseMsg.USER_NOT_MAP_EMPLOYEE}
            )
        bulk_data = []
        for doc in data:
            # check file tr?n cloud
            if not doc['attachment']:
                return False
            is_check, attach_check = Files.check_media_file(
                media_file_id=doc['attachment'],
                media_user_id=str(user.employee_current.media_user_id)
            )
            if not is_check:
                raise serializers.ValidationError({'Attachment': BaseMsg.UPLOAD_FILE_ERROR})

            # step 1: t?o m?i file trong File API
            files = Files.regis_media_file(
                relate_app, instance_id, relate_app_code, user, media_result=attach_check
            )
            # step 2: t?o m?i file trong table M2M
            bulk_data.append(
                OpportunitySubDocument(
                    document=instance,
                    attachment=files,
                    media_file=doc['attachment'],
                    description=doc['description']
                )
            )
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
                date_created=validated_data['request_completed_date']
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
                attachments.append(
                    {
                        "id": str(files.id),
                        "relate_app_id": str(files.relate_app_id),
                        "relate_app_code": files.relate_app_code,
                        "relate_doc_id": str(files.relate_doc_id),
                        "media_file_id": str(files.media_file_id),
                        "file_name": files.file_name,
                        "file_size": int(files.file_size),
                        "file_type": files.file_type
                    }
                )
            return attachments
        return []


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
        } if obj.call else {}

    @classmethod
    def get_meeting(cls, obj):
        return {
            'subject': obj.meeting.subject,
            'id': str(obj.meeting_id),
            'activity_name': 'Meeting with customer',
            'activity_type': 'meeting',
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
        )

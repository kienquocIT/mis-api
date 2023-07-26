from rest_framework import serializers

from apps.core.attachments.models import Files
from apps.core.base.models import Application
from apps.sales.opportunity.models import (
    OpportunityCallLog, OpportunityEmail, OpportunityMeeting,
    OpportunityMeetingEmployeeAttended, OpportunityMeetingCustomerMember, OpportunitySubDocument,
    OpportunityDocumentPersonInCharge, OpportunityDocument
)
from apps.shared import BaseMsg
from apps.shared.translations.opportunity import OpportunityMsg
from apps.shared.mail import GmailController


class OpportunityCallLogListSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityCallLog
        fields = (
            'id',
            'subject',
            'opportunity',
            'customer',
            'contact',
            'call_date',
            'input_result',
            'repeat'
        )

    @classmethod
    def get_opportunity(cls, obj):
        if obj.opportunity:
            return {
                'id': obj.opportunity_id,
                'code': obj.opportunity.code,
                'title': obj.opportunity.title
            }
        return {}

    @classmethod
    def get_customer(cls, obj):
        if obj.opportunity.customer:
            return {
                'id': obj.opportunity.customer_id,
                'code': obj.opportunity.customer.code,
                'title': obj.opportunity.customer.name
            }
        return {}

    @classmethod
    def get_contact(cls, obj):
        if obj.contact:
            return {
                'id': obj.contact_id,
                'fullname': obj.contact.fullname
            }
        return {}


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


class OpportunityCallLogDetailSerializer(serializers.ModelSerializer):
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


class OpportunityEmailListSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    email_to_contact = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityEmail
        fields = (
            'id',
            'subject',
            'email_to',
            'email_cc_list',
            'content',
            'date_created',
            'opportunity',
            'email_to_contact'
        )

    @classmethod
    def get_opportunity(cls, obj):
        if obj.opportunity:
            return {
                'id': obj.opportunity_id,
                'code': obj.opportunity.code,
                'title': obj.opportunity.title
            }
        return {}

    @classmethod
    def get_email_to_contact(cls, obj):
        if obj.email_to_contact:
            return {
                'id': obj.email_to_contact_id,
                'fullname': obj.email_to_contact.fullname,
                'email': obj.email_to_contact.email
            }
        return {}


def send_email(email_obj):
    GmailController(
        subject=email_obj.subject,
        to=email_obj.email_to,
        cc=email_obj.email_cc_list,
        bcc=[],
        template="<table><tr><td><h1>" + email_obj.subject + "</h1></td><td>" + email_obj.content + "</td></tr></table>",
        context=email_obj.content,
    ).send()
    return True


class OpportunityEmailCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=True)

    class Meta:
        model = OpportunityEmail
        fields = (
            'subject',
            'email_to',
            'email_cc_list',
            'content',
            'opportunity',
            'email_to_contact'
        )

    @classmethod
    def validate_email_to(cls, value):
        return value

    @classmethod
    def validate_email_cc_list(cls, value):
        return value

    def create(self, validated_data):
        email_obj = OpportunityEmail.objects.create(**validated_data)
        # try:
        #     send_email(email_obj)
        # except Exception:
        #     raise serializers.ValidationError({'Email': OpportunityMsg.CAN_NOT_SEND_EMAIL})
        return email_obj


class OpportunityEmailDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityEmail
        fields = (
            'id',
            'subject',
            'email_to',
            'email_cc_list',
            'content',
            'date_created',
            'opportunity',
            'email_to_contact'
        )


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
        if obj.opportunity:
            return {
                'id': obj.opportunity_id,
                'code': obj.opportunity.code,
                'title': obj.opportunity.title
            }
        return {}

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

    def create(self, validated_data):
        meeting_obj = OpportunityMeeting.objects.create(**validated_data)
        create_employee_attended_map_meeting(meeting_obj, self.initial_data.get('employee_attended_list', []))
        create_customer_member_map_meeting(meeting_obj, self.initial_data.get('customer_member_list', []))
        return meeting_obj


class OpportunityMeetingDetailSerializer(serializers.ModelSerializer):
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


class OpportunityDocumentListSerializer(serializers.ModelSerializer):
    to_contact = serializers.SerializerMethodField()
    opportunity = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityDocument
        fields = (
            'id',
            'to_contact',
            'opportunity',
            'subject',
            'request_completed_date'
        )

    @classmethod
    def get_to_contact(cls, obj):
        return None

    @classmethod
    def get_opportunity(cls, obj):
        if obj.opportunity:
            return {
                'id': obj.opportunity.id,
                'code': obj.opportunity.code,
                'title': obj.opportunity.title
            }
        return None


class OpportunityDocumentCreateSerializer(serializers.ModelSerializer):
    person_in_charge = serializers.ListField(child=serializers.UUIDField())

    class Meta:
        model = OpportunityDocument
        fields = (
            'subject',
            'opportunity',
            'request_completed_date',
            'kind_of_product',
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
        # attachments: list -> danh s�ch id t? cloud tr? v?, t?m th?i chi c� 1 n�n l?y [0]
        relate_app = Application.objects.get(id="319356b4-f16c-4ba4-bdcb-e1b0c2a2c124")
        relate_app_code = 'documentforcustomer'
        instance_id = str(instance.id)
        if not user.employee_current:
            raise serializers.ValidationError(
                {'User': BaseMsg.USER_NOT_MAP_EMPLOYEE}
            )
        bulk_data = []
        for doc in data:
            # check file tr�n cloud
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

    def create(self, validated_data):
        user = self.context.get('user', None)
        data_documents = validated_data.get('data_documents', [])
        data_person_in_charge = validated_data.pop('person_in_charge')
        instance = OpportunityDocument.objects.create(**validated_data)
        if instance:
            self.create_person_in_charge(data_person_in_charge, instance)
            self.create_sub_document(user, instance, data_documents)
        return instance


class OpportunityDocumentDetailSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityDocument
        fields = (
            'subject',
            'opportunity',
            'request_completed_date',
            'kind_of_product',
            'data_documents',
            'person_in_charge',
            'files',
        )

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

from rest_framework import serializers
from apps.sales.opportunity.models import (
    OpportunityCallLog, OpportunityEmail, OpportunityMeeting,
    OpportunityMeetingEmployeeAttended, OpportunityMeetingCustomerMember
)
from apps.shared.translations.opportunity import OpportunityMsg


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


class OpportunityCallLogDeleteSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = OpportunityCallLog
        fields = ()

    def update(self, instance, validated_data):
        instance.delete()
        return True


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
        if len(value.split(' ')) > 1 or not value.endswith("@gmail.com"):
            raise serializers.ValidationError({'To': OpportunityMsg.EMAIL_TO_NOT_VALID})
        return value

    @classmethod
    def validate_email_cc_list(cls, value):
        for item in value:
            if len(item.split(' ')) > 1 or not item.endswith("@gmail.com"):
                raise serializers.ValidationError({'Cc': OpportunityMsg.EMAIL_CC_NOT_VALID})
        return value


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


class OpportunityEmailDeleteSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = OpportunityEmail
        fields = ()

    def update(self, instance, validated_data):
        instance.delete()
        return True


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
        create_employee_attended_map_meeting(meeting_obj, validated_data.get('employee_attended_list', []))
        create_customer_member_map_meeting(meeting_obj, validated_data.get('customer_member_list', []))
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


class OpportunityMeetingDeleteSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = OpportunityMeeting
        fields = ()

    def update(self, instance, validated_data):
        OpportunityMeetingEmployeeAttended.objects.filter(meeting_mapped=instance).delete()
        OpportunityMeetingCustomerMember.objects.filter(meeting_mapped=instance).delete()
        instance.delete()
        return True

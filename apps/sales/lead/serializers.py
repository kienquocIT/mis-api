from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.core.mailer.tasks import send_email_sale_activities_email, send_email_sale_activities_meeting
from apps.masterdata.saledata.models import Periods, Contact, Industry
from apps.sales.lead.models import (
    Lead, LeadStage, LeadConfig, LeadChartInformation, LeadHint, LeadOpportunity, LeadNote, LeadParser,
    LEAD_SOURCE, LEAD_STATUS
)
from apps.sales.opportunity.models import (
    OpportunityCallLog, OpportunityEmail, OpportunityMeeting,
    OpportunityMeetingEmployeeAttended, OpportunityMeetingCustomerMember, OpportunityActivityLogs, Opportunity
)
from apps.sales.opportunity.serializers import ActivitiesCommonFunc
from apps.shared import BaseMsg, SaleMsg, AccountsMsg


__all__ = [
    'LeadListSerializer',
    'LeadCreateSerializer',
    'LeadDetailSerializer',
    'LeadUpdateSerializer',
    'LeadStageListSerializer',
    'LeadChartListSerializer',
    'LeadListForOpportunitySerializer',
    'LeadCallCreateSerializer',
    'LeadCallDetailSerializer',
    'LeadEmailCreateSerializer',
    'LeadEmailDetailSerializer',
    'LeadMeetingCreateSerializer',
    'LeadMeetingDetailSerializer'
]

# main
class LeadListSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()
    lead_status = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = (
            'id',
            'code',
            'title',
            'source',
            'lead_status',
            'current_lead_stage_data',
            'employee_created',
            'date_created',
            'email'
        )

    @classmethod
    def get_source(cls, obj):
        return str(dict(LEAD_SOURCE).get(obj.source))

    @classmethod
    def get_lead_status(cls, obj):
        return str(dict(LEAD_STATUS).get(obj.lead_status))

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}


class LeadCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    industry = serializers.UUIDField(required=False, allow_null=True)
    assign_to_sale = serializers.UUIDField(required=False, allow_null=True)
    note_data = serializers.JSONField(required=False, default=list)

    class Meta:
        model = Lead
        fields = (
            'title',
            'contact_name',
            'job_title',
            'mobile',
            'email',
            'company_name',
            'industry',
            'total_employees',
            'revenue',
            'source',
            'lead_status',
            'assign_to_sale',
            'note_data'
        )

    @classmethod
    def validate_industry(cls, value):
        if value:
            try:
                return Industry.objects.get_on_company(id=value)
            except Industry.DoesNotExist:
                raise serializers.ValidationError({"industry": AccountsMsg.INDUSTRY_NOT_EXIST})
        return None

    @classmethod
    def validate_assign_to_sale(cls, value):
        if value:
            try:
                return Employee.objects.get_on_company(id=value)
            except Employee.DoesNotExist:
                raise serializers.ValidationError({"assign_to_sale": SaleMsg.EMPLOYEE_NOT_EXIST})
        return None

    def validate(self, validate_data, **kwargs):
        industry_obj = validate_data.get('industry')
        if industry_obj:
            validate_data['industry_data'] = LeadParser.parse_data(industry_obj, 'industry')

        assign_to_sale_obj = validate_data.get('assign_to_sale')
        if assign_to_sale_obj:
            validate_data['assign_to_sale_data'] = LeadParser.parse_data(assign_to_sale_obj, 'assign_to_sale')

        current_stage_obj = LeadStage.objects.filter_on_company(level=1).first()
        if current_stage_obj:
            validate_data['current_lead_stage'] = current_stage_obj
            validate_data['current_lead_stage_data'] = LeadParser.parse_data(current_stage_obj, 'lead_stage')
        else:
            raise serializers.ValidationError({'current_lead_stage': _("Lead stage not found")})


        if 'tenant_current_id' in kwargs and 'company_current_id' in kwargs:
            tenant_current_id = kwargs.get('tenant_current_id')
            company_current_id = kwargs.get('company_current_id')
        else:
            tenant_current_id = self.context.get('tenant_current_id')
            company_current_id = self.context.get('company_current_id')

        period_mapped = Periods.get_current_period(tenant_current_id, company_current_id)
        if period_mapped:
            validate_data['period_mapped'] = period_mapped
        else:
            raise serializers.ValidationError({'period_mapped': _("Period not found")})

        return validate_data

    def create(self, validated_data):
        note_data = validated_data.pop('note_data', [])
        lead_obj = Lead.objects.create(**validated_data, system_status=1)
        LeadCommonFunc.create_lead_note(lead_obj, note_data)
        LeadConfig.objects.create(lead=lead_obj)
        return lead_obj


class LeadDetailSerializer(serializers.ModelSerializer):
    note_data = serializers.SerializerMethodField()
    config_data = serializers.SerializerMethodField()
    related_opps = serializers.SerializerMethodField()
    related_leads = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = (
            'id',
            'code',
            'title',
            'contact_name',
            'job_title',
            'mobile',
            'email',
            'company_name',
            'industry_data',
            'total_employees',
            'revenue',
            'source',
            'lead_status',
            'assign_to_sale_data',
            'current_lead_stage_data',
            'note_data',
            'config_data',
            'related_opps',
            'related_leads'
        )

    @classmethod
    def get_note_data(cls, obj):
        return [note_content.note for note_content in obj.lead_notes.all()]

    @classmethod
    def get_config_data(cls, obj):
        config = obj.lead_configs.first()
        return {
            'create_contact': config.create_contact,
            'convert_opp': config.convert_opp,
            'convert_opp_create': config.convert_opp_create,
            'convert_opp_select': config.convert_opp_select,
            'account_mapped': config.account_mapped_data,
            'assign_to_sale_config': config.assign_to_sale_config_data,
            'contact_mapped': config.contact_mapped_data,
            'opp_mapped': config.opp_mapped_data
        } if config else {}

    @classmethod
    def get_related_opps(cls, obj):
        related_opps = []
        config = obj.lead_configs.first()
        if config:
            if config.convert_opp:
                return []
        existed = []

        all_hint = LeadHint.objects.filter(opportunity__company_id=obj.company_id)
        hints_by_phone = all_hint.filter(contact_phone=obj.mobile) if obj.mobile else []
        hints_by_mobile = all_hint.filter(contact_mobile=obj.mobile) if obj.mobile else []
        hints_by_email = all_hint.filter(contact_email=obj.email) if obj.email else []
        for hint in list(hints_by_phone) + list(hints_by_mobile) + list(hints_by_email):
            if str(hint.opportunity_id) not in existed:
                related_opps.append(hint.opportunity_data)
                existed.append(str(hint.opportunity_id))
        return related_opps

    @classmethod
    def get_related_leads(cls, obj):
        related_leads = []
        config = obj.lead_configs.first()
        if config:
            if config.convert_opp:
                return []
        all_lead = Lead.objects.filter(tenant_id=obj.tenant_id, company_id=obj.company_id).exclude(id=obj.id)
        existed = []
        for lead in all_lead:
            filter_by_contact_name = all_lead.filter(contact_name=obj.contact_name).count()
            filter_by_mobile = all_lead.filter(mobile=obj.mobile).count()
            filter_by_email = all_lead.filter(email=obj.email).count()
            filter_by_company_name = all_lead.filter(company_name=obj.company_name).count()
            if sum([filter_by_contact_name, filter_by_mobile, filter_by_email, filter_by_company_name]) > 0:
                if str(lead.id) not in existed:
                    related_leads.append(LeadParser.parse_data(lead, 'lead'))
                    existed.append(str(lead.id))
        return related_leads


class LeadUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    industry = serializers.UUIDField(required=False, allow_null=True)
    assign_to_sale = serializers.UUIDField(required=False, allow_null=True)
    note_data = serializers.JSONField(required=False, default=list)

    class Meta:
        model = Lead
        fields = (
            'title',
            'contact_name',
            'job_title',
            'mobile',
            'email',
            'company_name',
            'industry',
            'total_employees',
            'revenue',
            'source',
            'lead_status',
            'assign_to_sale',
            'note_data'
        )

    @classmethod
    def validate_industry(cls, value):
        return LeadCreateSerializer.validate_industry(value)

    @classmethod
    def validate_assign_to_sale(cls, value):
        return LeadCreateSerializer.validate_assign_to_sale(value)

    def validate(self, validate_data):
        if 'goto_stage' in self.context:
            validate_data = {}
            stage_goto = LeadStage.objects.filter_on_company(level=3).first()
            if not stage_goto:
                raise serializers.ValidationError({'stage_goto': _("Lead stage level 3 not found.")})
            if self.instance.lead_status != 2:
                raise serializers.ValidationError({'stage': _('You have to go to "Marketing Qualified Lead" first.')})
            validate_data['stage_goto'] = stage_goto
            return validate_data
        if 'convert_opp' in self.context:
            validate_data = {}
            # check config
            lead_config = self.instance.lead_configs.first()
            if not lead_config:
                raise serializers.ValidationError({'lead_config': _("Lead config not found.")})
            validate_data['lead_config'] = lead_config
            # check lead converted
            if lead_config.contact_mapped or lead_config.convert_opp:
                raise serializers.ValidationError({'lead_config': _("Contact or Opp has been created already.")})
            # valid opp
            if 'opp_mapped_id' in self.context:
                opp_mapped = Opportunity.objects.filter_on_company(id=self.context.get('opp_mapped_id')).first()
                if not opp_mapped:
                    raise serializers.ValidationError({'opp_mapped': SaleMsg.OPPORTUNITY_NOT_EXIST})
                validate_data['opp_mapped'] = opp_mapped
            return validate_data
        return LeadCreateSerializer().validate(
            validate_data,
            **{
                'tenant_current_id': self.context.get('tenant_current_id'),
                'company_current_id': self.context.get('company_current_id'),
            }
        )

    def update(self, instance, validated_data):
        if 'goto_stage' in self.context:
            LeadCommonFunc.goto_stage(instance, validated_data.get('stage_goto'))
        elif 'convert_opp' in self.context:
            LeadCommonFunc.convert_to_opp(instance, validated_data.get('lead_config'), validated_data.get('opp_mapped'))
        else:
            note_data = validated_data.pop('note_data', [])
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()
            LeadCommonFunc.create_lead_note(instance, note_data)
        return instance


class LeadCommonFunc:
    @staticmethod
    def create_lead_note(lead_obj, note_data):
        LeadNote.objects.filter(lead=lead_obj).delete()
        for order, note_content in enumerate(note_data, start=1):
            LeadNote.objects.create(lead=lead_obj, note=note_content, order=order)
        return True

    @staticmethod
    def goto_stage(lead_obj, stage_goto):
        lead_obj.current_lead_stage = stage_goto
        lead_obj.current_lead_stage_data = LeadParser.parse_data(stage_goto, 'lead_stage')
        lead_obj.lead_status = 3
        lead_obj.save(update_fields=['current_lead_stage', 'current_lead_stage_data', 'lead_status'])
        return lead_obj

    @staticmethod
    def convert_to_opp(lead_obj, lead_config, opp_mapped):
        lead_config.convert_opp = True
        lead_config.convert_opp_select = True
        lead_config.opp_mapped = opp_mapped
        lead_config.opp_mapped_data = LeadParser.parse_data(opp_mapped, 'opportunity')
        lead_config.save(
            update_fields=['convert_opp', 'convert_opp_select', 'opp_mapped', 'opp_mapped_data']
        )
        LeadOpportunity.objects.create(
            tenant=lead_obj.tenant,
            company=lead_obj.company,
            lead=lead_obj,
            lead_data=LeadParser.parse_data(lead_obj, 'lead_mapped_opp'),
            opportunity=opp_mapped,
            employee_created=lead_obj.employee_created,
            employee_inherit=lead_obj.employee_inherit
        )
        stage = LeadStage.objects.filter_on_company(level=4).first()
        if stage:
            lead_obj.current_lead_stage = stage
            lead_obj.current_lead_stage_data = LeadParser.parse_data(stage, 'lead_stage')
            lead_obj.lead_status = 4
            lead_obj.save(update_fields=['current_lead_stage', 'current_lead_stage', 'lead_status'])
        return lead_obj

# related
class LeadStageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadStage
        fields = (
            'id',
            'stage_title',
            'level'
        )


class LeadChartListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadChartInformation
        fields = (
            'id',
            'status_amount_information',
            'stage_amount_information',
            'period_mapped'
        )


class LeadListForOpportunitySerializer(serializers.ModelSerializer):
    lead = serializers.SerializerMethodField()

    class Meta:
        model = LeadOpportunity
        fields = (
            'id',
            'lead',
            'opportunity'
        )

    @classmethod
    def get_lead(cls, obj):
        return obj.lead_data


class LeadCallCreateSerializer(serializers.ModelSerializer):
    lead = serializers.UUIDField(required=True)
    contact = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = OpportunityCallLog
        fields = (
            'lead',
            'subject',
            'call_date',
            'contact',
            'input_result',
            'employee_inherit_id'
        )

    @classmethod
    def validate_subject(cls, value):
        if not value:
            raise serializers.ValidationError({'subject': BaseMsg.REQUIRED})
        return value

    @classmethod
    def validate_call_date(cls, value):
        if not value:
            raise serializers.ValidationError({'call_date': BaseMsg.REQUIRED})
        return value

    @classmethod
    def validate_input_result(cls, value):
        if not value:
            raise serializers.ValidationError({'input_result': BaseMsg.REQUIRED})
        return value

    @classmethod
    def validate_lead(cls, value):
        try:
            return Lead.objects.get(pk=value)
        except Lead.DoesNotExist:
            raise serializers.ValidationError({'lead': 'Lead does not exist.'})

    def validate(self, validated_data):
        lead = validated_data.get('lead')
        contact_id = validated_data.get('contact', None)
        for lead_config in lead.lead_configs.all():
            if lead_config.contact_mapped and contact_id is None:
                raise serializers.ValidationError({'contact': BaseMsg.REQUIRED})

        if contact_id:
            try:
                validated_data['contact'] = Contact.objects.get(pk=contact_id)
            except Contact.DoesNotExist:
                raise serializers.ValidationError({'contact': 'Contact does not exist.'})

        return validated_data

    def create(self, validated_data):
        with transaction.atomic():
            validated_data['employee_inherit_id'] = validated_data.get('employee_created_id', None)
            instance = OpportunityCallLog.objects.create(**validated_data)
            OpportunityActivityLogs.objects.create(
                tenant=instance.tenant,
                company=instance.company,
                call=instance,
                log_type=2,
                lead_id=instance.lead_id,
                doc_data = {
                    'id': str(instance.id).replace('-',''),
                    'subject': instance.subject,
                    'call_date': str(instance.call_date),
                    'employee_created': instance.employee_created.get_full_name(),
                    'contact': {
                        'id': str(instance.contact_id).replace('-',''),
                        'fullname': instance.contact.fullname
                    } if instance.contact else {},
                    'input_result': instance.input_result,
                    'lead': {
                        'id': str(instance.lead_id).replace('-',''),
                        'title': instance.lead.title,
                    },
                },
                employee_created_id=str(validated_data.get('employee_created_id', '')).replace('-',''),
            )
            return instance


class LeadCallDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityCallLog
        fields = (
            'id',
        )


class LeadEmailCreateSerializer(serializers.ModelSerializer):
    lead = serializers.UUIDField(required=True)

    class Meta:
        model = OpportunityEmail
        fields = (
            'subject',
            'lead',
            'email_to_list',
            'email_cc_list',
            'email_bcc_list',
            'content',
            'just_log'
        )

    @classmethod
    def validate_subject(cls, value):
        if not value:
            raise serializers.ValidationError({'subject': BaseMsg.REQUIRED})
        return value

    @classmethod
    def validate_lead(cls, value):
        try:
            return Lead.objects.get(pk=value)
        except Lead.DoesNotExist:
            raise serializers.ValidationError({'lead': 'Lead does not exist.'})

    def create(self, validated_data):
        with transaction.atomic():
            validated_data['employee_inherit_id'] = validated_data.get('employee_created_id', None)
            if not self.context.get('employee_current').email:
                raise serializers.ValidationError({'from_email': SaleMsg.FROM_EMAIL_NOT_EXIST})

            validated_data['from_email'] = self.context.get('employee_current').email
            instance = OpportunityEmail.objects.create(**validated_data)
            if not validated_data.get('just_log', False) and self.context.get('user_current'):
                email_sent = send_email_sale_activities_email(self.context.get('user_current').id, instance)
                instance.send_success = email_sent == 'Success'
                instance.save(update_fields=['send_success'])
            OpportunityActivityLogs.objects.create(
                tenant=instance.tenant,
                company=instance.company,
                email=instance,
                log_type=3,
                lead_id=instance.lead_id,
                employee_created_id=str(validated_data.get('employee_created_id', '')).replace('-', ''),
                doc_data={
                    'id': str(instance.id).replace('-', ''),
                    'subject': instance.subject,
                    'email_date': str(instance.date_created),
                    'employee_created': instance.employee_created.get_full_name(),
                    'email_to_list': instance.email_to_list,
                    'email_cc_list': instance.email_cc_list,
                    'email_bcc_list': instance.email_bcc_list,
                    'from_email': instance.from_email,
                    'content': instance.content,
                    'lead': {
                        'id': str(instance.lead_id).replace('-', ''),
                        'title': instance.lead.title,
                    },
                    'send_success': instance.send_success,
                    'just_log': instance.just_log,
                },
            )
            return instance


class LeadEmailDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpportunityEmail
        fields = (
            'id',
        )


class LeadMeetingEmployeeAttendedListSerializer(serializers.ModelSerializer):
    employee_attended_mapped = serializers.UUIDField()

    class Meta:
        model = OpportunityMeetingEmployeeAttended
        fields = (
            'employee_attended_mapped',
        )

    @classmethod
    def validate_employee_attended_mapped(cls, value):
        try:
            return Employee.objects.get(pk=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({'Employee Attended List': 'Employee does not exist.'})


class LeadMeetingCustomerMemberListSerializer(serializers.ModelSerializer):
    customer_member_mapped = serializers.UUIDField(allow_null=True, required=False)
    class Meta:
        model = OpportunityMeetingCustomerMember
        fields = (
            'customer_member_mapped',
        )

    @classmethod
    def validate_customer_member_mapped(cls, value):
        if value:
            try:
                return Contact.objects.get(pk=value)
            except Contact.DoesNotExist:
                raise serializers.ValidationError({'Customer Member Mapped': 'Customer does not exist.'})
        return value


class LeadMeetingCreateSerializer(serializers.ModelSerializer):
    lead = serializers.UUIDField(required=True)
    employee_attended_list = LeadMeetingEmployeeAttendedListSerializer(many=True)
    customer_member_list = LeadMeetingCustomerMemberListSerializer(many=True)

    class Meta:
        model = OpportunityMeeting
        fields = (
            'lead',
            'subject',
            'employee_attended_list',
            'customer_member_list',
            'meeting_date',
            'meeting_from_time',
            'meeting_to_time',
            'meeting_address',
            'input_result',
            'room_location',
            'email_notify'
        )

    @classmethod
    def validate_lead(cls, value):
        try:
            return Lead.objects.get(pk=value)
        except Lead.DoesNotExist:
            raise serializers.ValidationError({'lead': 'Lead does not exist.'})

    def validate(self, validate_data):
        meeting_from_time = validate_data.get('meeting_from_time')
        meeting_to_time = validate_data.get('meeting_to_time')

        if meeting_from_time > meeting_to_time:
            raise serializers.ValidationError({'Meeting Time: ': 'Starting time must be before ending time.'})

        return validate_data

    def create(self, validated_data):
        with transaction.atomic():
            validated_data['employee_inherit_id'] = validated_data.get('employee_created_id', None)
            employee_attended_list_data = validated_data.pop('employee_attended_list')
            customer_member_list_data = validated_data.pop('customer_member_list')

            employee_attended_list = [
                {'id': item['employee_attended_mapped'].id } for item in employee_attended_list_data
            ]
            customer_member_list = [
                {'id': item['customer_member_mapped'].id } if item['customer_member_mapped'] else {}
                for item in customer_member_list_data
            ]
            instance = OpportunityMeeting.objects.create(**validated_data)

            ActivitiesCommonFunc.create_employee_attended_map_meeting(instance, employee_attended_list)
            ActivitiesCommonFunc.create_customer_member_map_meeting(instance, customer_member_list)

            if validated_data.get('email_notify', False) and self.context.get('user_current'):
                # email_sent = ActivitiesCommonFunc.send_email(instance, self.context.get('employee_current'))
                email_sent = send_email_sale_activities_meeting( self.context.get('user_current').id, instance)
                instance.send_success = email_sent == 'Success'
                instance.save(update_fields=['send_success'])
            OpportunityActivityLogs.objects.create(
                tenant=instance.tenant,
                company=instance.company,
                meeting=instance,
                log_type=4,
                lead_id=instance.lead_id,
                employee_created_id=str(validated_data.get('employee_created_id', '')).replace('-', ''),
                doc_data={
                    'id': str(instance.id).replace('-', ''),
                    'subject': instance.subject,
                    'meeting_date': str(instance.meeting_date),
                    'employee_created': instance.employee_created.get_full_name(),
                    'employee_attended_list': [
                        {
                            'id': str(item.id).replace('-', ''),
                            'group': {
                                'id': str(item.group_id).replace('-', ''),
                                'title': item.group.title,
                                'code': item.group.code
                            } if item.group else {},
                            'fullname': item.get_full_name(),
                        } for item in instance.employee_attended_list.all()
                    ],
                    'customer_member_list': [
                        {
                            'id': str(item.id).replace('-', ''),
                            'code': item.code,
                            'fullname': item.fullname,
                            'job_title': item.job_title,
                        } for item in instance.customer_member_list.all()
                    ],
                    'meeting_from_time': str(instance.meeting_from_time),
                    'meeting_to_time': str(instance.meeting_to_time),
                    'input_result': instance.input_result,
                    'room_location': instance.room_location,
                    'meeting_address': instance.meeting_address,
                    'lead': {
                        'id': str(instance.lead_id).replace('-', ''),
                        'title': instance.lead.title,
                    },
                    'send_success': instance.send_success
                }
            )
            return instance


class LeadMeetingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityMeeting
        fields = (
            'id',
        )

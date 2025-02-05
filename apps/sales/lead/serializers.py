from django.db import transaction
from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.core.mailer.tasks import send_email_sale_activities_email, send_email_sale_activities_meeting
from apps.masterdata.saledata.models import Periods, Contact
from apps.sales.lead.models import (
    Lead, LeadNote, LeadStage, LeadConfig, LEAD_SOURCE, LEAD_STATUS,
    LeadChartInformation, LeadHint, LeadOpportunity
)

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

from apps.sales.opportunity.models import OpportunityCallLog, OpportunityEmail, OpportunityMeeting, \
    OpportunityMeetingEmployeeAttended, OpportunityMeetingCustomerMember, OpportunityActivityLogs

from apps.sales.opportunity.serializers import ActivitiesCommonFunc

from apps.shared import BaseMsg, SaleMsg


class LeadListSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()
    lead_status = serializers.SerializerMethodField()
    current_lead_stage = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = (
            'id',
            'code',
            'title',
            'contact_name',
            'source',
            'lead_status',
            'current_lead_stage',
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
    def get_current_lead_stage(cls, obj):
        return {
            'title': obj.current_lead_stage.stage_title,
            'level': obj.current_lead_stage.level,
        }


class LeadCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)

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
        )

    def validate(self, validate_data):
        return validate_data

    def create(self, validated_data):
        current_stage = LeadStage.objects.filter(
            tenant_id=validated_data['tenant_id'], company_id=validated_data['company_id'], level=1
        ).first()
        this_period = Periods.get_current_period(validated_data['tenant_id'], validated_data['company_id'])
        if current_stage and this_period:
            lead = Lead.objects.create(
                **validated_data, current_lead_stage=current_stage, system_status=1,
                period_mapped=this_period
            )

            # create notes
            for note_content in self.initial_data.get('note_data', []):
                LeadNote.objects.create(lead=lead, note=note_content)

            # create config
            if 'assign_to_sale' in validated_data:
                LeadConfig.objects.create(lead=lead, assign_to_sale_config=validated_data['assign_to_sale'])

            return lead
        raise serializers.ValidationError({'Lead stage': "Lead stage not found"})


class LeadDetailSerializer(serializers.ModelSerializer):
    industry = serializers.SerializerMethodField()
    assign_to_sale = serializers.SerializerMethodField()
    note_data = serializers.SerializerMethodField()
    config_data = serializers.SerializerMethodField()
    current_lead_stage = serializers.SerializerMethodField()
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
            'industry',
            'total_employees',
            'revenue',
            'source',
            'lead_status',
            'assign_to_sale',
            'current_lead_stage',
            'note_data',
            'config_data',
            'related_opps',
            'related_leads'
        )

    @classmethod
    def get_industry(cls, obj):
        return {
            'id': obj.industry_id,
            'code': obj.industry.code,
            'title': obj.industry.title
        } if obj.industry else {}

    @classmethod
    def get_assign_to_sale(cls, obj):
        return {
            'id': obj.assign_to_sale_id,
            'code': obj.assign_to_sale.code,
            'full_name': obj.assign_to_sale.get_full_name(2)
        } if obj.assign_to_sale else {}

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
            'account_mapped': {
                'id': config.account_mapped_id,
                'code': config.account_mapped.code,
                'name': config.account_mapped.name,
            } if config.account_mapped else None,
            'assign_to_sale_config': {
                'id': config.assign_to_sale_config_id,
                'code': config.assign_to_sale_config.code,
                'full_name': config.assign_to_sale_config.get_full_name(2),
            } if config.assign_to_sale_config else {},
            'contact_mapped': {
                'id': config.contact_mapped_id,
                'code': config.contact_mapped.code,
                'fullname': config.contact_mapped.fullname,
                'email': config.contact_mapped.email,
            } if config.contact_mapped else {},
            'opp_mapped': {
                'id': config.opp_mapped_id,
                'code': config.opp_mapped.code,
                'title': config.opp_mapped.title,
            } if config.opp_mapped else {}
        } if config else {}

    @classmethod
    def get_current_lead_stage(cls, obj):
        return {
            'title': obj.current_lead_stage.stage_title,
            'level': obj.current_lead_stage.level,
        }

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
                related_opps.append({
                    'id': str(hint.opportunity_id),
                    'code': hint.opportunity.code,
                    'title': hint.opportunity.title,
                    'customer': {
                        'id': hint.opportunity.customer_id,
                        'title': hint.opportunity.customer.name,
                        'code': hint.opportunity.customer.code,
                    } if hint.opportunity.customer else {},
                    'sale_person': {
                        'id': hint.opportunity.employee_inherit_id,
                        'code': hint.opportunity.employee_inherit.code,
                        'full_name': hint.opportunity.employee_inherit.get_full_name(2)
                    } if hint.opportunity.employee_inherit else {}
                })
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
                    related_leads.append({'id': lead.id, 'code': lead.code, 'title': lead.title})
                    existed.append(str(lead.id))
        return related_leads


class LeadUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)

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
        )

    def validate(self, validate_data):
        return validate_data

    @classmethod
    def goto_stage(cls, instance):
        stage_goto = LeadStage.objects.filter(
            company=instance.company, tenant=instance.tenant, level=3
        ).first()
        if instance.lead_status == 2 and stage_goto:
            instance.current_lead_stage = stage_goto
            instance.lead_status = 3
        else:
            raise serializers.ValidationError({
                'error': 'Can not go to this Stage. You have to go to "Marketing Qualified Lead" first.'
            })
        instance.save()
        return instance

    @classmethod
    def convert_opp(cls, instance, config, opp_mapped_id):
        if config:
            config.convert_opp = True
            config.convert_opp_create = False
            config.convert_opp_select = True
            config.opp_mapped_id = opp_mapped_id
            config.save(update_fields=[
                'convert_opp', 'convert_opp_create', 'convert_opp_select', 'opp_mapped_id'
            ])
            LeadOpportunity.objects.create(
                company=instance.company, tenant=instance.tenant,
                lead=instance, opportunity_id=opp_mapped_id,
                employee_created=instance.employee_created,
                employee_inherit=instance.employee_inherit
            )
            stage = LeadStage.objects.filter(
                company=instance.company, tenant=instance.tenant, level=4
            ).first()
            if stage:
                instance.current_lead_stage = stage
                instance.lead_status = 4
        instance.save()
        return instance

    def update(self, instance, validated_data):
        # this_period = Periods.get_current_period(instance.tenant_id, instance.company_id)
        config = instance.lead_configs.first()
        # if str(this_period.id) == str(instance.period_mapped_id):
        if 'goto_stage' in self.context:
            self.goto_stage(instance)
        elif 'convert_opp' in self.context:
            self.convert_opp(instance, config, self.context.get('opp_mapped_id'))
        else:
            if config.contact_mapped or config.convert_opp:
                raise serializers.ValidationError(
                    {'Finished': "Can not update this Lead. Contact or Opp has been created already."}
                )
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            # update notes
            LeadNote.objects.filter(lead=instance).delete()
            for note_content in self.initial_data.get('note_data', []):
                LeadNote.objects.create(lead=instance, note=note_content)

        return instance
        # raise serializers.ValidationError({'Lead period': "Can not update lead of other period."})


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
        return {
            'id': obj.lead_id,
            'code': obj.lead.code,
            'title': obj.lead.title,
            'contact_name': obj.lead.contact_name,
            'source': str(dict(LEAD_SOURCE).get(obj.lead.source)),
            'lead_status': str(dict(LEAD_STATUS).get(obj.lead.lead_status)),
            'date_created': obj.lead.date_created
        }


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
                doc_id = str(instance.lead_id).replace('-',''),
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
                doc_id=str(instance.lead_id).replace('-', ''),
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
                doc_id=str(instance.lead_id).replace('-', ''),
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

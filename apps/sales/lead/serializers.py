from django.db import transaction
from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.masterdata.saledata.models import Periods, Contact
from apps.sales.lead.models import (
    Lead, LeadNote, LeadStage, LeadConfig, LEAD_SOURCE, LEAD_STATUS,
    LeadChartInformation, LeadHint, LeadOpportunity, LeadCall, LeadEmail, LeadMeeting
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
    'LeadActivityListSerializer',
    'LeadEmailCreateSerializer',
    'LeadEmailDetailSerializer',
    'LeadMeetingCreateSerializer',
    'LeadMeetingDetailSerializer'
]

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
        model = LeadCall
        fields = (
            'lead',
            'title',
            'call_date',
            'contact',
            'detail'
        )

    @classmethod
    def validate_title(cls, value):
        if not value:
            raise serializers.ValidationError({'title': BaseMsg.REQUIRED})
        return value

    @classmethod
    def validate_call_date(cls, value):
        if not value:
            raise serializers.ValidationError({'call_date': BaseMsg.REQUIRED})
        return value

    @classmethod
    def validate_detail(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': BaseMsg.REQUIRED})
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
        if lead.contact_name and contact_id is None:
            raise serializers.ValidationError({'contact': BaseMsg.REQUIRED})

        if contact_id:
            try:
                validated_data['contact'] = Contact.objects.get(pk=contact_id)
            except Contact.DoesNotExist:
                raise serializers.ValidationError({'contact': 'Contact does not exist.'})

        return validated_data

    def create(self, validated_data):
        instance = LeadCall.objects.create(**validated_data)
        return instance


class LeadCallDetailSerializer(serializers.ModelSerializer):
    lead = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()

    class Meta:
        model = LeadCall
        fields = (
            'id',
            'title',
            'call_date',
            'lead',
            'contact',
            'detail'
        )

    @classmethod
    def get_lead(cls, obj):
        return {}

    @classmethod
    def get_contact(cls, obj):
        return {}


class LeadCallUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadCall
        fields = ('is_cancelled',)

    def validate(self, validate_data):
        if self.instance.is_cancelled is True:
            raise serializers.ValidationError({'Cancelled': SaleMsg.CAN_NOT_REACTIVE})
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class LeadEmailCreateSerializer(serializers.ModelSerializer):
    lead = serializers.UUIDField(required=True)

    class Meta:
        model = LeadEmail
        fields = (
            'subject',
            'lead',
            'email_to_list',
            'email_cc_list',
            'content'
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
            instance = LeadEmail(**validated_data)

            email_sent = ActivitiesCommonFunc.send_email(instance, self.context.get('employee_current'))

            if email_sent:
                instance.save()
                return instance
            else:
                raise Exception("Failed to send email. Model instance will not be saved.")


class LeadEmailDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeadEmail
        fields = (
            'id',
            'title',
        )


class LeadMeetingCreateSerializer(serializers.ModelSerializer):
    lead = serializers.UUIDField(required=True)
    class Meta:
        model = LeadMeeting
        fields = (
            'lead',
            'title',
            'employee_member_list',
            'customer_member_list',
            'meeting_date',
            'meeting_from_time',
            'meeting_to_time',
            'meeting_address',
            'detail',
            'room_location'
        )

    @classmethod
    def validate_lead(cls, value):
        try:
            return Lead.objects.get(pk=value)
        except Lead.DoesNotExist:
            raise serializers.ValidationError({'lead': 'Lead does not exist.'})


    def create(self, validated_data):
        instance = LeadMeeting.objects.create(**validated_data)
        return instance


class LeadMeetingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadMeeting
        fields = (
            'id',
        )


class LeadActivityListSerializer(serializers.ModelSerializer):
    activity_list = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = (
            'id',
            'activity_list'
        )

    @classmethod
    def get_activity_list(cls, obj):
        # Combine data from the three related tables
        activities = []
        lead_title = obj.title
        # Add LeadCall activities
        for call in obj.lead_call_lead.all():
            employee_created = Employee.objects.filter(id=call.employee_created_id).first()
            contact = Contact.objects.filter(id=call.contact_id).first()
            activities.append({
                'lead_name': lead_title,
                'type': 'call',
                'id': call.id,
                'title': call.title,
                'date_created': call.date_created,
                'employee_created': {
                    'id': employee_created.id,
                    'name': employee_created.get_full_name(),
                },
                'date': call.call_date,
                'detail': call.detail,
                'contact_name': contact.fullname
            })

        # Add LeadMeeting activities
        for meeting in obj.lead_meeting_lead.all():
            employee_created = Employee.objects.filter(id=meeting.employee_created_id).first()
            employee_member_list = Employee.objects.filter(id__in=meeting.employee_member_list)
            customer_member_list = Contact.objects.filter(id__in=meeting.customer_member_list)
            activities.append({
                'lead_name': lead_title,
                'type': 'meeting',
                'id': meeting.id,
                'title': meeting.title,
                'date_created': meeting.date_created,
                'employee_created': {
                    'id': employee_created.id,
                    'name': employee_created.get_full_name(),
                },
                'date': meeting.meeting_date,
                'detail': meeting.detail,
                'meeting_from_time': meeting.meeting_from_time,
                'meeting_to_time': meeting.meeting_to_time,
                'meeting_address': meeting.meeting_address,
                'room_location': meeting.room_location,
                'employee_member_list': [{
                    'id': employee.id,
                    'fullname': employee.get_full_name(),
                    'group': {
                        'id': employee.group_id,
                        'title': employee.group.title,
                        'code': employee.group.code
                    } if employee.group else {}
                }  for employee in employee_member_list],
                'customer_member_list': [{
                    'id': contact.id,
                    'fullname': contact.fullname,
                } for contact in customer_member_list]
            })

        # Add LeadEmail activities
        for email in obj.lead_email_lead.all():
            employee_created = Employee.objects.filter(id=email.employee_created_id).first()
            activities.append({
                'lead_name': lead_title,
                'type': 'email',
                'id': email.id,
                'subject': email.subject,
                'date_created': email.date_created,
                'employee_created': {
                    'id': employee_created.id,
                    'name': employee_created.get_full_name(),
                },
                'date': '',
                'detail': email.content,
                'email_cc_list': email.email_cc_list,
                'email_to_list': email.email_to_list,
            })

        # Sort activities by date_created
        sorted_activities = sorted(activities, key=lambda x: x['date_created'], reverse=True)

        return sorted_activities

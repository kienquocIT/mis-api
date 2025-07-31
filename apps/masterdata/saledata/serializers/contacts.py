from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from apps.masterdata.saledata.models.accounts import AccountContacts, Account
from apps.masterdata.saledata.models.contacts import (
    Salutation, Interest, Contact,
)
from apps.shared import AccountsMsg
from apps.core.hr.models import Employee
from apps.sales.lead.models import LeadStage, LeadChartInformation, LeadHint, LeadParser


# Salutation
class SalutationListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Salutation
        fields = ('id', 'title', 'code', 'description', 'is_default')


class SalutationCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100)

    class Meta:
        model = Salutation
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_code(cls, value):
        if value:
            if Salutation.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
            return value
        raise serializers.ValidationError({"code": AccountsMsg.CODE_NOT_NULL})

    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": AccountsMsg.TITLE_NOT_NULL})


class SalutationDetailSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Salutation
        fields = ('id', 'title', 'code', 'description')


class SalutationUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)

    class Meta:
        model = Salutation
        fields = ('title', 'description')

    def validate_title(self, value):
        if value:
            return value
        raise serializers.ValidationError({"code": AccountsMsg.CODE_NOT_NULL})


# Interest
class InterestsListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Interest
        fields = ('id', 'title', 'code', 'description')


class InterestsCreateSerializer(serializers.ModelSerializer):  # noqa
    code = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=100)

    class Meta:
        model = Interest
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_code(cls, value):
        if value:
            if Interest.objects.filter_current(fill__tenant=True, fill__company=True, code=value).exists():
                raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
            return value
        raise serializers.ValidationError({"code": AccountsMsg.CODE_NOT_NULL})


    @classmethod
    def validate_title(cls, value):
        if value:
            return value
        raise serializers.ValidationError({"title": AccountsMsg.TITLE_NOT_NULL})


class InterestsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ('id', 'title', 'code', 'description')


class InterestsUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)

    class Meta:
        model = Interest
        fields = ('title', 'description')

    def validate_title(self, value):
        if value:
            return value
        raise serializers.ValidationError({"title": AccountsMsg.TITLE_NOT_NULL})


# Contact
class ContactListSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    account_name = serializers.SerializerMethodField()
    report_to = serializers.SerializerMethodField()
    employee_created = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            'id',
            'code',
            'fullname',
            'job_title',
            'owner',
            'account_name',
            'mobile',
            'phone',
            'email',
            'report_to',
            'date_created',
            'employee_created'
        )

    @classmethod
    def get_owner(cls, obj):
        return {
            'id': obj.owner_id,
            'code': obj.owner.code,
            'fullname': obj.owner.get_full_name(2),
            'group': {
                'id': obj.owner.group_id,
                'title': obj.owner.group.title,
                'code': obj.owner.group.code
            } if obj.owner.group else {}
        } if obj.owner else {}

    @classmethod
    def get_account_name(cls, obj):
        return {
            'id': obj.account_name_id,
            'code': obj.account_name.code,
            'name': obj.account_name.name
        } if obj.account_name else {}

    @classmethod
    def get_report_to(cls, obj):
        return {
            'id': obj.report_to_id,
            'code': obj.report_to.code,
            'name': obj.report_to.fullname
        } if obj.report_to else {}

    @classmethod
    def get_employee_created(cls, obj):
        return obj.employee_created.get_detail_with_group() if obj.employee_created else {}


class ContactCreateSerializer(serializers.ModelSerializer):
    owner = serializers.UUIDField()
    fullname = serializers.CharField(max_length=100)
    mobile = serializers.CharField(max_length=25, required=False, allow_null=True, allow_blank=True)
    email = serializers.CharField(max_length=150, required=False, allow_null=True, allow_blank=True)
    additional_information = serializers.JSONField(required=False)

    class Meta:
        model = Contact
        fields = (
            "owner",
            "job_title",
            "biography",
            "fullname",
            "salutation",
            "phone",
            "mobile",
            "email",
            "report_to",
            "address_information",
            'home_detail_address',
            'home_address_data',
            'work_detail_address',
            'work_address_data',
            "additional_information",
            'account_name',
        )

    @classmethod
    def validate_owner(cls, value):
        try:
            return Employee.objects.get(id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({"owner": AccountsMsg.OWNER_NOT_NULL})

    @classmethod
    def validate_email(cls, value):
        if value:
            if Contact.objects.filter_current(fill__tenant=True, fill__company=True, email=value).exists():
                raise serializers.ValidationError({"email": AccountsMsg.EMAIL_EXIST})
            return value
        return None

    @classmethod
    def validate_mobile(cls, value):
        if value:
            if Contact.objects.filter_current(fill__tenant=True, fill__company=True, mobile=value).exists():
                raise serializers.ValidationError({"mobile": AccountsMsg.MOBILE_EXIST})
            return value
        return None

    @classmethod
    def validate_additional_information(cls, value):
        interest_list = [{
            'id': item.id,
            'code': item.code,
            'title': item.title
        } for item in Interest.objects.filter(id__in=value.get('interests', []))]
        value['interests'] = interest_list
        return value

    def validate(self, validate_data):
        num = Contact.objects.filter_current(fill__tenant=True, fill__company=True).count()
        validate_data['code'] = f"C00{num + 1}"
        if 'lead' in self.context:
            lead_obj = self.context.get('lead')
            if not lead_obj:
                raise serializers.ValidationError({'lead': _('Lead not found.')})
            validate_data['lead'] = lead_obj
            lead_config = lead_obj.lead_configs.first()
            if not lead_config:
                raise serializers.ValidationError({'lead_config': _('Lead config not found.')})
            validate_data['lead_config'] = lead_config
            if lead_config.create_contact:
                raise serializers.ValidationError({'converted': _('Already converted to contact.')})
        return validate_data

    @classmethod
    def convert_contact(cls, lead_obj, lead_config, contact_obj):
        # convert to a new contact
        current_stage = LeadStage.objects.filter_on_company(level=2).first()
        lead_obj.current_lead_stage = current_stage
        lead_obj.current_lead_stage_data = LeadParser.parse_data(current_stage, 'lead_stage')
        lead_obj.lead_status = 2
        lead_obj.save(update_fields=['current_lead_stage', 'current_lead_stage_data', 'lead_status'])

        lead_config.contact_mapped = contact_obj
        lead_config.contact_mapped_data = LeadParser.parse_data(contact_obj, 'contact')
        lead_config.create_contact = True
        lead_config.save(update_fields=['contact_mapped', 'contact_mapped_data', 'create_contact'])

        LeadChartInformation.create_update_chart_information(contact_obj.tenant_id, contact_obj.company_id)
        return True

    def create(self, validated_data):
        if 'lead' in self.context:
            lead_obj = validated_data.pop('lead')
            lead_config = validated_data.pop('lead_config')
            contact = Contact.objects.create(**validated_data)
            self.convert_contact(lead_obj, lead_config, contact)
        else:
            contact = Contact.objects.create(**validated_data)

        AccountContacts.objects.filter(contact=contact).delete()
        if contact.account_name:
            AccountContacts.objects.create(account=contact.account_name, contact=contact)
        return contact


class ContactDetailSerializer(serializers.ModelSerializer):
    salutation = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    report_to = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    account_name = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            "id",
            "code",
            "owner",
            "job_title",
            "biography",
            "fullname",
            "salutation",
            "phone",
            "mobile",
            "email",
            "report_to",
            "address_information",
            "additional_information",
            "account_name",
        )

    @classmethod
    def get_salutation(cls, obj):
        return {
            'id': obj.salutation_id,
            'code': obj.salutation.code,
            'title': obj.salutation.title
        } if obj.salutation else {}

    @classmethod
    def get_owner(cls, obj):
        return {
            'id': obj.owner_id,
            'code': obj.owner.code,
            'full_name': obj.owner.get_full_name(2)
        } if obj.owner else {}

    @classmethod
    def get_report_to(cls, obj):
        return {
            'id': obj.report_to_id,
            'code': obj.report_to.code,
            'fullname': obj.report_to.fullname
        } if obj.report_to else {}

    @classmethod
    def get_fullname(cls, obj):
        return {
            'fullname': obj.fullname,
            'last_name': obj.fullname.split(' ')[-1],
            'first_name': ' '.join(obj.fullname.split(' ')[:-1])
        } if obj.fullname else {}

    @classmethod
    def get_account_name(cls, obj):
        return {
            "id": obj.account_name_id,
            "code": obj.account_name.code,
            "name": obj.account_name.name
        } if obj.account_name else {}


class ContactUpdateSerializer(serializers.ModelSerializer):
    owner = serializers.UUIDField()
    fullname = serializers.CharField(max_length=100)
    mobile = serializers.CharField(max_length=25, required=False, allow_null=True, allow_blank=True)
    email = serializers.CharField(max_length=150, required=False, allow_null=True, allow_blank=True)
    additional_information = serializers.JSONField(required=False)

    class Meta:
        model = Contact
        fields = (
            "owner",
            "job_title",
            "biography",
            "fullname",
            "salutation",
            "phone",
            "mobile",
            "email",
            "report_to",
            "address_information",
            'home_detail_address',
            'home_address_data',
            'work_detail_address',
            'work_address_data',
            "additional_information",
            'account_name',
        )

    @classmethod
    def validate_owner(cls, value):
        try:
            return Employee.objects.get(id=value)
        except Employee.DoesNotExist:
            raise serializers.ValidationError({"owner": AccountsMsg.OWNER_NOT_NULL})

    def validate_email(self, value):
        if value:
            if all([
                value != self.instance.email,
                Contact.objects.filter_current(fill__tenant=True, fill__company=True, email=value).exists()
            ]):
                raise serializers.ValidationError({"email": AccountsMsg.EMAIL_EXIST})
            return value
        return None

    def validate_mobile(self, value):
        if value:
            if all([
                value != self.instance.mobile,
                Contact.objects.filter_current(fill__tenant=True, fill__company=True, mobile=value).exists()
            ]):
                raise serializers.ValidationError({"mobile": AccountsMsg.MOBILE_EXIST})
            return value
        return None

    def update(self, instance, validated_data):
        if not validated_data.get('account_name'):
            validated_data['account_name'] = None
            Account.objects.filter_on_company(owner=instance).update(owner=None)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        AccountContacts.objects.filter(contact=instance).delete()
        if instance.account_name:
            AccountContacts.objects.create(account=instance.account_name, contact=instance)

        LeadHint.check_and_create_lead_hint(None, instance)
        return instance


class ContactListNotMapAccountSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            'id',
            'code',
            'fullname',
            'job_title',
            'owner',
            'mobile',
            'phone',
            'email'
        )

    @classmethod
    def get_owner(cls, obj):
        return {
            'id': obj.owner_id,
            'code': obj.owner.code,
            'fullname': obj.owner.get_full_name(2)
        } if obj.owner else {}

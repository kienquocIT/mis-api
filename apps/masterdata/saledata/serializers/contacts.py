from rest_framework import serializers

from apps.core.hr.models import Employee
from apps.masterdata.saledata.models.contacts import (
    Salutation, Interest, Contact,
)
from apps.shared import (AccountsMsg,)
from apps.sales.lead.models import LeadStage, LeadChartInformation, LeadHint


# Salutation
class SalutationListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Salutation
        fields = ('id', 'title', 'code', 'description')


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
            'report_to'
        )

    @classmethod
    def get_owner(cls, obj):
        if obj.owner:
            return {
                'id': obj.owner_id,
                'fullname': obj.owner.get_full_name(2)
            }
        return {}

    @classmethod
    def get_account_name(cls, obj):
        if obj.account_name:
            return {
                'id': obj.account_name_id,
                'name': obj.account_name.name
            }
        return {}

    @classmethod
    def get_report_to(cls, obj):
        if obj.report_to:
            return {
                'id': obj.report_to_id,
                'name': obj.report_to.fullname
            }
        return {}


class ContactCreateSerializer(serializers.ModelSerializer):
    owner = serializers.UUIDField()
    fullname = serializers.CharField(max_length=100)
    mobile = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    email = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    additional_information = serializers.JSONField()

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
            "additional_information",
            'account_name',
            'work_detail_address',
            'work_country',
            'work_city',
            'work_district',
            'work_ward',
            'home_detail_address',
            'home_country',
            'home_city',
            'home_district',
            'home_ward',
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
        return validate_data

    @classmethod
    def convert_contact(cls, lead, contact_mapped):
        # convert to a new contact
        lead_configs = lead.lead_configs.first() if lead else None
        if lead_configs:
            if not lead_configs.create_contact:
                current_stage = LeadStage.objects.filter(
                    tenant_id=contact_mapped.tenant_id, company_id=contact_mapped.company_id, level=2
                ).first()
                lead.current_lead_stage = current_stage
                lead.lead_status = 2
                lead.save(update_fields=['current_lead_stage', 'lead_status'])
                lead_configs.contact_mapped = contact_mapped
                lead_configs.create_contact = True
                lead_configs.save(update_fields=['contact_mapped', 'create_contact'])
                LeadChartInformation.create_update_chart_information(
                    contact_mapped.tenant_id, contact_mapped.company_id
                )
                return True
            raise serializers.ValidationError({'converted': 'Converted to contact.'})
        raise serializers.ValidationError({'not found': 'Lead config not found.'})

    def create(self, validated_data):
        contact = Contact.objects.create(**validated_data)
        if contact.account_name:
            contact.account_name.owner = contact
            contact.account_name.save(update_fields=['owner'])

        if 'lead' in self.context:
            self.convert_contact(self.context.get('lead'), contact)

        return contact


class ContactDetailSerializer(serializers.ModelSerializer):
    work_country = serializers.SerializerMethodField()
    work_city = serializers.SerializerMethodField()
    work_district = serializers.SerializerMethodField()
    work_ward = serializers.SerializerMethodField()
    home_country = serializers.SerializerMethodField()
    home_city = serializers.SerializerMethodField()
    home_district = serializers.SerializerMethodField()
    home_ward = serializers.SerializerMethodField()
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
            "avatar",
            "fullname",
            "salutation",
            "phone",
            "mobile",
            "email",
            "report_to",
            "address_information",
            "additional_information",
            "account_name",
            'work_detail_address',
            'work_country',
            'work_city',
            'work_district',
            'work_ward',
            'home_detail_address',
            'home_country',
            'home_city',
            'home_district',
            'home_ward',
        )

    @classmethod
    def get_work_ward(cls, obj):
        return {
            'id': obj.work_ward.id,
            'title': obj.work_ward.title
        } if obj.work_ward else {}

    @classmethod
    def get_home_ward(cls, obj):
        return {
            'id': obj.home_ward.id,
            'title': obj.home_ward.title
        } if obj.home_ward else {}

    @classmethod
    def get_work_district(cls, obj):
        return {
            'id': obj.work_district.id,
            'title': obj.work_district.title,
        } if obj.work_district else {}

    @classmethod
    def get_home_district(cls, obj):
        return {
            'id': obj.home_district.id,
            'title': obj.home_district.title,
        } if obj.home_district else {}

    @classmethod
    def get_work_city(cls, obj):
        return {
            'id': obj.work_city.id,
            'title': obj.work_city.title,
        } if obj.work_city else {}

    @classmethod
    def get_home_city(cls, obj):
        return {
            'id': obj.home_city.id,
            'title': obj.home_city.title,
        } if obj.home_city else {}

    @classmethod
    def get_work_country(cls, obj):
        return {
            'id': obj.work_country.id,
            'title': obj.work_country.title,
        } if obj.work_country else {}

    @classmethod
    def get_home_country(cls, obj):
        return {
            'id': obj.home_country.id,
            'title': obj.home_country.title,
        } if obj.home_country else {}

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
    mobile = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    email = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    additional_information = serializers.JSONField()

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
            "additional_information",
            'account_name',
            'work_detail_address',
            'work_country',
            'work_city',
            'work_district',
            'work_ward',
            'home_detail_address',
            'home_country',
            'home_city',
            'home_district',
            'home_ward',
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

    def validate(self, validate_data):
        return validate_data

    def update(self, instance, validated_data):
        if not validated_data.get('account_name'):
            account_mapped = instance.account_name
            if account_mapped:
                account_mapped.owner = None
                account_mapped.save()

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        LeadHint.check_and_create_lead_hint(None, instance)

        return instance


class ContactListNotMapAccountSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            'id',
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
            'fullname': obj.owner.get_full_name(2)
        } if obj.owner else {}

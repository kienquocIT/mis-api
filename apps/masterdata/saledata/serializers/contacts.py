from rest_framework import serializers
from apps.masterdata.saledata.models.contacts import (
    Salutation, Interest, Contact,
)
from apps.shared import (AccountsMsg,)
from apps.sales.lead.models import Lead, LeadStage


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
    class Meta:
        model = Contact
        fields = (
            "owner",
            "job_title",
            "biography",
            # "avatar",
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
            'system_status',
        )

    @classmethod
    def validate_email(cls, attrs):
        if attrs:
            if Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    email=attrs,
            ).exists():
                raise serializers.ValidationError({"email": AccountsMsg.EMAIL_EXIST})
            return attrs
        return None

    @classmethod
    def validate_mobile(cls, attrs):
        if attrs:
            if Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    mobile=attrs,
            ).exists():
                raise serializers.ValidationError({"mobile": AccountsMsg.MOBILE_EXIST})
            return attrs
        return None

    @classmethod
    def validate_owner(cls, attrs):
        if attrs:
            return attrs
        raise serializers.ValidationError({"owner": AccountsMsg.OWNER_NOT_NULL})

    @classmethod
    def convert_contact(cls, lead_pk, tenant_id, company_id, contact_mapped):
        # convert to a new contact
        lead = Lead.objects.filter(id=lead_pk, system_status=3).first()
        lead_configs = lead.lead_configs.first() if lead else None
        if lead and lead_configs:
            current_stage = LeadStage.objects.filter(tenant_id=tenant_id, company_id=company_id, level=2).first()
            lead.current_lead_stage = current_stage
            lead.lead_status = 2
            lead.save(update_fields=['current_lead_stage', 'lead_status'])
            lead_configs.contact_mapped = contact_mapped
            lead_configs.create_contact = True
            lead_configs.save(update_fields=['contact_mapped', 'create_contact'])
            return True
        raise serializers.ValidationError({'not found': 'Lead || Lead config not found.'})

    def create(self, validated_data):
        if 'code' not in validated_data:
            number = Contact.objects.filter(
                tenant_id=validated_data['tenant_id'],
                company_id=validated_data['company_id']
            ).count() + 1
            validated_data['code'] = f"C00{number}"
        contact = Contact.objects.create(**validated_data)
        if contact.account_name:
            contact.account_name.owner = contact
            contact.account_name.save(update_fields=['owner'])

        if 'lead_id' in self.context:
            self.convert_contact(
                self.context.get('lead_id'),
                validated_data['tenant_id'],
                validated_data['company_id'],
                contact
            )

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
    additional_information = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    account_name = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            "id",
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
        if obj.salutation:
            return {
                'id': obj.salutation_id,
                'title': obj.salutation.title
            }
        return {}

    @classmethod
    def get_owner(cls, obj):
        if obj.owner:
            return {
                'id': obj.owner_id,
                'fullname': obj.owner.get_full_name(2)
            }
        return {}

    @classmethod
    def get_report_to(cls, obj):
        if obj.report_to:
            return {
                'id': obj.report_to_id,
                'fullname': obj.report_to.fullname
            }
        return {}

    @classmethod
    def get_additional_information(cls, obj):
        if obj.additional_information:
            interest_list = []
            interest_id_list = list(obj.additional_information.get('interests', None))
            interest = Interest.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                id__in=interest_id_list
            )
            if interest:
                for item in interest:
                    interest_list.append(
                        {
                            'id': item.id,
                            'title': item.title
                        }
                    )
            obj.additional_information['interests'] = interest_list
            return obj.additional_information
        return {}

    @classmethod
    def get_fullname(cls, obj):
        if obj.fullname:
            return {
                'fullname': obj.fullname,
                'last_name': obj.fullname.split(' ')[-1],
                'first_name': ' '.join(obj.fullname.split(' ')[:-1])
            }
        return {}

    @classmethod
    def get_account_name(cls, obj):
        if obj.account_name:
            return {
                "id": obj.account_name_id,
                "name": obj.account_name.name
            }
        return {}


class ContactUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = (
            "owner",
            "job_title",
            "biography",
            # "avatar",
            "fullname",
            "salutation",
            "phone",
            "mobile",
            "email",
            "report_to",
            "address_information",
            "additional_information",
            'account_name'
        )

    def validate_email(self, attrs):
        if attrs:
            if attrs != self.instance.email and Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    email=attrs,
            ).exists():
                raise serializers.ValidationError({"email": AccountsMsg.EMAIL_EXIST})
            return attrs
        return None

    def validate_mobile(self, attrs):
        if attrs:
            if attrs != self.instance.mobile and Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    mobile=attrs,
            ).exists():
                raise serializers.ValidationError({"mobile": AccountsMsg.MOBILE_EXIST})
            return attrs
        return None

    @classmethod
    def validate_owner(cls, attrs):
        if attrs:
            return attrs
        raise serializers.ValidationError({"owner": AccountsMsg.OWNER_NOT_NULL})

    def validate(self, validate_data):
        home_address_dict = self.initial_data.get('home_address_dict', [])
        work_address_dict = self.initial_data.get('work_address_dict', [])
        if len(home_address_dict) > 0:
            home_address_dict = home_address_dict[0]
            for key, _ in home_address_dict.items():
                if key not in ['home_detail_address']:
                    validate_data[key] = home_address_dict.get(key, None)
                else:
                    validate_data[key] = home_address_dict.get(key, '')
        if len(work_address_dict) > 0:
            work_address_dict = work_address_dict[0]
            for key, _ in work_address_dict.items():
                if key not in ['work_detail_address']:
                    validate_data[key] = work_address_dict.get(key, None)
                else:
                    validate_data[key] = work_address_dict.get(key, '')
        return validate_data

    def update(self, instance, validated_data):
        if 'account_name' not in validated_data.keys():
            validated_data.update({'account_name': None})
            account_mapped = instance.account_name
            if account_mapped:
                account_mapped.owner = None
                account_mapped.save()

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

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

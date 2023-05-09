from rest_framework import serializers
from apps.core.hr.models import Employee
from apps.masterdata.saledata.models.accounts import Account
from apps.masterdata.saledata.models.contacts import (
    Salutation, Interest, Contact
)
from apps.shared import AccountsMsg


# Salutation
class SalutationListSerializer(serializers.ModelSerializer):  # noqa

    class Meta:
        model = Salutation
        fields = ('id', 'title', 'code', 'description')


class SalutationCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Salutation
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_code(cls, value):
        if Salutation.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
        return value

    @classmethod
    def validate_title(cls, value):
        if Salutation.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


class SalutationDetailSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Salutation
        fields = ('id', 'title', 'code', 'description')


class SalutationUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Salutation
        fields = ('title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and Salutation.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


# Interest
class InterestsListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Interest
        fields = ('id', 'title', 'code', 'description')


class InterestsCreateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Interest
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_code(cls, value):
        if Interest.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
        return value

    @classmethod
    def validate_title(cls, value):
        if Interest.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


class InterestsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ('id', 'title', 'code', 'description')


class InterestsUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Interest
        fields = ('title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and Interest.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


# Contact
class ContactListSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    account_name = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            'id',
            'fullname',
            'job_title',
            'owner',
            'account_name',
            'mobile',
            'email'
        )

    @classmethod
    def get_owner(cls, obj):
        if obj.owner:
            owner = Employee.objects.filter(
                id=obj.owner
            ).first()
            if owner:
                return {
                    'id': obj.owner,
                    'fullname': owner.get_full_name(2)
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


class ContactCreateSerializer(serializers.ModelSerializer):
    account_name = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Contact
        fields = (
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
            'account_name'
        )

    @classmethod
    def validate_account_name(cls, attrs):
        if attrs is not None:
            account = Account.objects.filter(
                id=attrs
            ).first()
            if account:
                return account
        raise serializers.ValidationError({"account_name": AccountsMsg.ACCOUNT_NOT_EXIST})

    @classmethod
    def validate_email(cls, attrs):
        if attrs is not None:
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
        if attrs is not None:
            if Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    mobile=attrs,
            ).exists():
                raise serializers.ValidationError({"mobile": AccountsMsg.MOBILE_EXIST})
            return attrs
        return None


class ContactDetailSerializer(serializers.ModelSerializer):
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
            "account_name"
        )

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
            owner = Employee.objects.filter(
                id=obj.owner
            ).first()
            if owner:
                return {
                    'id': obj.owner,
                    'fullname': owner.get_full_name(2)
                }
        return {}

    @classmethod
    def get_report_to(cls, obj):
        if obj.report_to:
            owner = Contact.objects.filter(
                id=obj.report_to
            ).first()
            if owner:
                return {
                    'id': obj.report_to,
                    'fullname': owner.fullname
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
    account_name = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Contact
        fields = (
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
            'account_name'
        )

    @classmethod
    def validate_account_name(cls, value):
        if value is not None:
            account = Account.objects.filter(
                id=value
            ).first()
            if account:
                return account
        raise serializers.ValidationError({"account_name": AccountsMsg.ACCOUNT_NOT_EXIST})

    def validate_email(self, attrs):
        if attrs is not None:
            if attrs != self.instance.email and Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    email=attrs,
            ).exists():
                raise serializers.ValidationError({"email": AccountsMsg.EMAIL_EXIST})
            return attrs
        return None

    def validate_mobile(self, attrs):
        if attrs is not None:
            if attrs != self.instance.mobile and Contact.objects.filter_current(
                    fill__tenant=True,
                    fill__company=True,
                    mobile=attrs,
            ).exists():
                raise serializers.ValidationError({"mobile": AccountsMsg.MOBILE_EXIST})
            return attrs
        return None

    def update(self, instance, validated_data):
        if 'account_name' not in validated_data.keys():
            validated_data.update({'account_name': None})

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
        if obj.owner:
            owner = Employee.objects.filter(
                id=obj.owner
            ).first()
            if owner:
                return {
                    'id': obj.owner,
                    'fullname': owner.get_full_name(2)
                }
        return {}

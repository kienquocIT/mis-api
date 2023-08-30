from rest_framework import serializers
from apps.masterdata.saledata.models.accounts import (
    AccountType, Industry, AccountGroup)
from apps.shared import AccountsMsg


# Account Type
class AccountTypeListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = AccountType
        fields = ('id', 'title', 'code', 'is_default', 'description')


class AccountTypeCreateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150) # noqa

    class Meta:
        model = AccountType
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_code(cls, value):
        if AccountType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
        return value

    @classmethod
    def validate_title(cls, value):
        if AccountType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


class AccountTypeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = ('id', 'title', 'code', 'is_default', 'description')


class AccountTypeUpdateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = AccountType
        fields = ('title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and AccountType.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


# Account Group
class AccountGroupListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = AccountGroup
        fields = ('id', 'title', 'code', 'description')


class AccountGroupCreateSerializer(serializers.ModelSerializer):  # noqa
    title = serializers.CharField(max_length=150)

    class Meta:
        model = AccountGroup
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_code(cls, value):
        if AccountGroup.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
        return value

    @classmethod
    def validate_title(cls, value):
        if AccountGroup.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


class AccountGroupDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountGroup
        fields = ('id', 'title', 'code', 'description')


class AccountGroupUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = AccountGroup
        fields = ('title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and AccountGroup.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


# Industry
class IndustryListSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Industry
        fields = ('id', 'title', 'code', 'description')


class IndustryCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Industry
        fields = ('code', 'title', 'description')

    @classmethod
    def validate_code(cls, value):
        if Industry.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                code=value,
        ).exists():
            raise serializers.ValidationError({"code": AccountsMsg.CODE_EXIST})
        return value

    @classmethod
    def validate_title(cls, value):
        if Industry.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value


class IndustryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ('id', 'title', 'code', 'description')


class IndustryUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150)

    class Meta:
        model = Industry
        fields = ('title', 'description')

    def validate_title(self, value):
        if value != self.instance.title and Industry.objects.filter_current(
                fill__tenant=True,
                fill__company=True,
                title=value,
        ).exists():
            raise serializers.ValidationError({"title": AccountsMsg.NAME_EXIST})
        return value

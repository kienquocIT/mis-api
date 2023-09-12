from rest_framework import serializers

from apps.masterdata.saledata.models import ExpenseItem
from apps.shared.translations.expense import ExpenseMsg

__all__ = ['ExpenseItemListSerializer', 'ExpenseItemCreateSerializer', 'ExpenseItemUpdateSerializer']


class ExpenseItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseItem
        fields = (
            'id',
            'code',
            'title',
            'description',
            'expense_parent',
            'is_active',
            'level',
            'is_parent',
        )


class ExpenseItemCreateSerializer(serializers.ModelSerializer):
    expense_parent = serializers.UUIDField(required=False)  # noqa

    class Meta:
        model = ExpenseItem
        fields = (
            'code',
            'title',
            'description',
            'expense_parent',
        )

    @classmethod
    def validate_expense_parent(cls, value):
        if value:
            try:
                return ExpenseItem.objects.get(id=value)
            except ExpenseItem.DoesNotExist:
                raise serializers.ValidationError({'parent': ExpenseMsg.PARENT_NOT_EXIST})
        return None

    def create(self, validated_data):
        if 'expense_parent' in validated_data:
            instance = ExpenseItem.objects.create(**validated_data, level=validated_data['expense_parent'].level + 1)
            validated_data['expense_parent'].is_parent = True
            validated_data['expense_parent'].save()
        else:
            instance = ExpenseItem.objects.create(**validated_data, level=0)
        return instance


class ExpenseItemUpdateSerializer(serializers.ModelSerializer):
    expense_parent = serializers.UUIDField(required=False)  # noqa
    code = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = ExpenseItem
        fields = (
            'code',
            'title',
            'description',
            'expense_parent',
            'is_active',
        )

    @classmethod
    def validate_expense_parent(cls, value):
        if value:
            try:
                return ExpenseItem.objects.get(id=value)
            except ExpenseItem.DoesNotExist:
                raise serializers.ValidationError({'parent': ExpenseMsg.PARENT_NOT_EXIST})
        return None

    @classmethod
    def get_descendants(cls, instance):
        descendants = ExpenseItem.objects.filter(expense_parent=instance)
        for descendant in descendants:
            descendants |= cls.get_descendants(descendant)
        return descendants

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)

        if 'expense_parent' in validated_data:
            validated_data['expense_parent'].is_parent = True
            validated_data['expense_parent'].save()
            descendants = self.get_descendants(instance)
            for item in descendants:
                item.level += 1
                item.save()

            instance.level += 1
        instance.save()
        return instance


class ExpenseItemDetailSerializer(serializers.ModelSerializer):
    expense_parent = serializers.SerializerMethodField()

    class Meta:
        model = ExpenseItem
        fields = (
            'id',
            'code',
            'title',
            'description',
            'is_active',
            'level',
            'expense_parent'
        )

    @classmethod
    def get_expense_parent(cls, obj):
        if obj.expense_parent:
            return {
                'id': obj.expense_parent_id,
                'title': obj.expense_parent.title,
            }
        return {}

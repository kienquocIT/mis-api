from rest_framework import serializers
from django.db.models import Sum

from apps.accounting.accountingsettings.models import ChartOfAccounts
from apps.accounting.accountingsettings.models.chart_of_account import CHART_OF_ACCOUNT_TYPE
from apps.accounting.journalentry.models import JournalEntryLine


class ChartOfAccountTreeNodeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    total_debit = serializers.SerializerMethodField()
    total_credit = serializers.SerializerMethodField()
    acc_type_name = serializers.SerializerMethodField()

    class Meta:
        model = ChartOfAccounts
        fields = (
            'id',
            'acc_code',
            'acc_name',
            'foreign_acc_name',
            'acc_type',
            'acc_type_name',
            'level',
            'has_child',
            'total_debit',
            'total_credit',
            'children'
        )

    def get_children(self, obj):
        children_map = self.context.get('children_map', {})
        children_obj = children_map.get(obj.id, [])
        return ChartOfAccountTreeNodeSerializer(children_obj, many=True, context=self.context).data

    @classmethod
    def get_total_debit(cls, obj):
        result = JournalEntryLine.objects.filter(
            account=obj,
            journal_entry__je_state=1
        ).aggregate(total=Sum('debit'))
        return result['total'] or 0

    @classmethod
    def get_total_credit(cls, obj):
        result = JournalEntryLine.objects.filter(
            account=obj,
            journal_entry__je_state=1
        ).aggregate(total=Sum('credit'))
        return result['total'] or 0

    @classmethod
    def get_acc_type_name(cls, obj):
        acc_type_dict = dict(CHART_OF_ACCOUNT_TYPE)
        return str(acc_type_dict.get(obj.acc_type, ''))

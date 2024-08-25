__all__ = ['WorkExpenseListSerializers', 'ProjectExpenseHomeListSerializers']
from rest_framework import serializers

from apps.shared import ProjectMsg
from ..models import WorkMapExpense


class WorkExpenseListSerializers(serializers.ModelSerializer):
    expense_name = serializers.SerializerMethodField()
    expense_item = serializers.SerializerMethodField()
    uom = serializers.SerializerMethodField()
    tax = serializers.SerializerMethodField()
    work_id = serializers.SerializerMethodField()

    @classmethod
    def get_expense_name(cls, obj):
        return {
            "id": obj.expense_name.id,
            "title": obj.expense_name.title,
        } if obj.expense_name else {}

    @classmethod
    def get_expense_item(cls, obj):
        return {
            "id": obj.expense_item.id,
            "title": obj.expense_item.title,
        } if obj.expense_item else {}

    @classmethod
    def get_uom(cls, obj):
        return {
            "id": obj.uom.id,
            "title": obj.uom.title,
        } if obj.uom else {}

    @classmethod
    def get_tax(cls, obj):
        return {
            "id": obj.tax.id,
            "title": obj.tax.title,
            "rate": obj.tax.rate
        } if obj.tax else {}

    @classmethod
    def get_work_id(cls, obj):
        return obj.work.id if obj.work else ''

    class Meta:
        model = WorkMapExpense
        fields = (
            'id',
            'title',
            'expense_name',
            'expense_item',
            'uom',
            'quantity',
            'expense_price',
            'tax',
            'sub_total',
            'sub_total_after_tax',
            'is_labor',
            'work_id',
        )


class ProjectExpenseHomeListSerializers(serializers.ModelSerializer):
    project = serializers.SerializerMethodField()

    @classmethod
    def get_project(cls, obj):
        work = obj.work.project_projectmapwork_work.all().first()
        if work:
            return {
                'id': str(work.project_id),
                'title': work.project.title
            }
        raise ValueError(ProjectMsg.PROJECT_NOT_EXIST)

    class Meta:
        model = WorkMapExpense
        fields = (
            'sub_total',
            'project',
        )

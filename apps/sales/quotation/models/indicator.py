from django.db import models

from apps.shared import SimpleAbstractModel


class QuotationIndicatorConfig(SimpleAbstractModel):
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.SET_NULL,
        null=True,
        related_name='indicator_company',
    )
    title = models.CharField(
        max_length=100,
        blank=True
    )
    remark = models.CharField(
        max_length=200,
        blank=True
    )
    example = models.CharField(
        max_length=300,
        blank=True
    )
    application_code = models.CharField(
        max_length=100,
        blank=True
    )
    formula_data = models.JSONField(default=list)
    formula_data_show = models.TextField(
        blank=True,
        null=True
    )
    order = models.IntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Quotation Indicator Config'
        verbose_name_plural = 'Quotation Indicator Configs'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class QuotationIndicator(SimpleAbstractModel):
    quotation = models.ForeignKey(
        'quotation.Quotation',
        on_delete=models.CASCADE,
        verbose_name="quotation",
        related_name="quotation_indicator_quotation",
    )
    indicator = models.ForeignKey(
        QuotationIndicatorConfig,
        on_delete=models.CASCADE,
        verbose_name="indicator",
        related_name="quotation_indicator_indicator",
    )
    indicator_value = models.FloatField(
        default=0,
        help_text="value of specific indicator for quotation"
    )
    indicator_rate = models.FloatField(
        default=0,
        help_text="rate value of specific indicator for quotation"
    )
    order = models.IntegerField(
        default=1
    )

    class Meta:
        verbose_name = 'Quotation Indicator'
        verbose_name_plural = 'Quotation Indicators'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class IndicatorDefaultData:
    INDICATOR_DATA = [
        {
            "title": "Revenue",
            "remark": "Revenue",
            "example": "indicator(Revenue)",
            "application_code": "quotation",
            "formula_data": [
                {
                    "id": "9a8bef37-6812-4d8b-ba6a-dc5669e61029",
                    "code": "total_product_pretax_amount",
                    "type": 6,
                    "title": "Total revenue before tax",
                    "remark": "Total revenue before tax of quotation",
                    "syntax": "prop(Total revenue before tax)",
                    "properties": {},
                    "is_property": True,
                    "syntax_show": "prop(Total revenue before tax)",
                    "content_type": "quotation.Quotation",
                }
            ],
            "formula_data_show": "prop(Total revenue before tax)",
            "order": 1
        },
        {
            "title": "Cost price",
            "remark": "Cost price",
            "example": "indicator(Cost price)",
            "application_code": "quotation",
            "formula_data": [
                {
                    "id": "148843b4-97a9-47ea-a5cf-a5cf1d557abd",
                    "code": "total_cost",
                    "type": 6,
                    "title": "Total cost after tax",
                    "remark": "Total cost of quotation",
                    "syntax": "prop(Total cost after tax)",
                    "properties": {},
                    "is_property": True,
                    "syntax_show": "prop(Total cost after tax)",
                    "content_type": "quotation.Quotation",
                }
            ],
            "formula_data_show": "prop(Total cost after tax)",
            "order": 2
        },
        {
            "title": "Gross profit",
            "remark": "Gross profit",
            "example": "indicator(Gross profit)",
            "application_code": "quotation",
            "formula_data": [
                {
                    "id": "1",
                    "order": 1,
                    "title": "Revenue",
                    "remark": "Doanh thu",
                    "syntax": "indicator(Revenue)",
                    "example": "indicator(Revenue)",
                    "syntax_show": "indicator(Revenue)",
                    "formula_data": [
                        {
                            "id": "9a8bef37-6812-4d8b-ba6a-dc5669e61029",
                            "code": "total_product_pretax_amount",
                            "type": 6,
                            "title": "Total revenue before tax",
                            "remark": "Total revenue before tax of quotation",
                            "syntax": "prop(Total revenue before tax)",
                            "properties": {

                            },
                            "is_property": True,
                            "syntax_show": "prop(Total revenue before tax)",
                            "content_type": "quotation.Quotation",
                        }
                    ],
                    "is_indicator": True,
                    "formula_data_show": "prop(Total revenue before tax)"
                },
                "-",
                {
                    "id": "2",
                    "order": 2,
                    "title": "Cost price",
                    "remark": "Giá vốn",
                    "syntax": "indicator(Cost price)",
                    "example": "indicator(Cost price)",
                    "syntax_show": "indicator(Cost price)",
                    "formula_data": [
                        {
                            "id": "148843b4-97a9-47ea-a5cf-a5cf1d557abd",
                            "code": "total_cost",
                            "type": 6,
                            "title": "Total cost after tax",
                            "remark": "Total cost of quotation",
                            "syntax": "prop(Total cost after tax)",
                            "properties": {

                            },
                            "is_property": True,
                            "syntax_show": "prop(Total cost after tax)",
                            "content_type": "quotation.Quotation",
                        }
                    ],
                    "is_indicator": True,
                    "formula_data_show": "prop(Total cost after tax)"
                }
            ],
            "formula_data_show": "indicator(Revenue) - indicator(Cost price)",
            "order": 3
        },
        {
            "title": "Operating costs",
            "remark": "Operating costs",
            "example": "indicator(Operating costs)",
            "application_code": "quotation",
            "formula_data": [
                {
                    "id": "aebaf647-49ff-4d59-a738-41ed6a583b50",
                    "code": "sumItemIf",
                    "title": "sumItemIf",
                    "remark": "Returns total of items that pass condition.",
                    "syntax": "sumItemIf(",
                    "example": "sumItemIf((5, 2, 9, 3), '>3') == 14",
                    "param_type": 2,
                    "syntax_show": "sumItemIf(item_check_list, condition, item_sum_list)",
                    "function_data": [
                        {
                            "id": "8ecc50e2-e7d6-4b0d-9cd5-92eec83f8f95",
                            "code": "expense_type_title",
                            "type": 1,
                            "title": "Expense type",
                            "remark": "Type expense on quotation expense line",
                            "syntax": "prop(Expense type)",
                            "properties": {},
                            "is_property": True,
                            "syntax_show": "prop(Expense type)",
                            "content_type": None,
                        },
                        "===",
                        "Chiphítriểnkhai",
                        {
                            "id": "6c6af508-c5b0-4295-b92a-bfc53dfad9d3",
                            "code": "expense_subtotal_price_after_tax",
                            "type": 6,
                            "title": "Expense subtotal after tax",
                            "remark": "Subtotal after tax expense on quotation expense line",
                            "syntax": "prop(Expense subtotal after tax)",
                            "properties": {},
                            "is_property": True,
                            "syntax_show": "prop(Expense subtotal after tax)",
                            "content_type": None,
                        }
                    ]
                }
            ],
            "formula_data_show": "sumItemIf(prop(Expense type)=='Chi phí triển khai',prop(Expense subtotal after tax))",
            "order": 4
        },
        {
            "title": "Net profit",
            "remark": "Net profit",
            "example": "indicator(Net profit)",
            "application_code": "quotation",
            "formula_data": [
                {
                    "id": "3",
                    "order": 3,
                    "title": "Gross profit",
                    "remark": "Lợi nhuận gộp",
                    "syntax": "indicator(Gross profit)",
                    "example": "indicator(Gross profit)",
                    "syntax_show": "indicator(Gross profit)",
                    "formula_data": [
                        {
                            "id": "1",
                            "order": 1,
                            "title": "Revenue",
                            "remark": "Doanh thu",
                            "syntax": "indicator(Revenue)",
                            "example": "indicator(Revenue)",
                            "syntax_show": "indicator(Revenue)",
                            "formula_data": [
                                {
                                    "id": "9a8bef37-6812-4d8b-ba6a-dc5669e61029",
                                    "code": "total_product_pretax_amount",
                                    "type": 6,
                                    "title": "Total revenue before tax",
                                    "remark": "Total revenue before tax of quotation",
                                    "syntax": "prop(Total revenue before tax)",
                                    "properties": {},
                                    "is_property": True,
                                    "syntax_show": "prop(Total revenue before tax)",
                                    "content_type": "quotation.Quotation",
                                }
                            ],
                            "is_indicator": True,
                            "formula_data_show": "prop(Total revenue before tax)"
                        },
                        "-",
                        {
                            "id": "2",
                            "order": 2,
                            "title": "Cost price",
                            "remark": "Giá vốn",
                            "syntax": "indicator(Cost price)",
                            "example": "indicator(Cost price)",
                            "syntax_show": "indicator(Cost price)",
                            "formula_data": [
                                {
                                    "id": "148843b4-97a9-47ea-a5cf-a5cf1d557abd",
                                    "code": "total_cost",
                                    "type": 6,
                                    "title": "Total cost after tax",
                                    "remark": "Total cost of quotation",
                                    "syntax": "prop(Total cost after tax)",
                                    "properties": {},
                                    "is_property": True,
                                    "syntax_show": "prop(Total cost after tax)",
                                    "content_type": "quotation.Quotation",
                                }
                            ],
                            "is_indicator": True,
                            "formula_data_show": "prop(Total cost after tax)"
                        }
                    ],
                    "is_indicator": True,
                    "formula_data_show": "indicator(Revenue) - indicator(Cost price)"
                },
                "-",
                {
                    "id": "4",
                    "order": 4,
                    "title": "Operating costs",
                    "remark": "Chi phí hoạt động",
                    "syntax": "indicator(Operating costs)",
                    "example": "indicator(Operating costs)",
                    "syntax_show": "indicator(Operating costs)",
                    "formula_data": [
                        {
                            "id": "aebaf647-49ff-4d59-a738-41ed6a583b50",
                            "code": "sumItemIf",
                            "title": "sumItemIf",
                            "remark": "Returns total of items that pass condition.",
                            "syntax": "sumItemIf(",
                            "example": "sumItemIf((5, 2, 9, 3), '>3') == 14",
                            "param_type": 2,
                            "syntax_show": "sumItemIf(item_check_list, condition, item_sum_list)",
                            "function_data": [
                                {
                                    "id": "8ecc50e2-e7d6-4b0d-9cd5-92eec83f8f95",
                                    "code": "expense_type_title",
                                    "type": 1,
                                    "title": "Expense type",
                                    "remark": "Type expense on quotation expense line",
                                    "syntax": "prop(Expense type)",
                                    "properties": {},
                                    "is_property": True,
                                    "syntax_show": "prop(Expense type)",
                                    "content_type": None,
                                },
                                "===",
                                "Chiphítriểnkhai",
                                {
                                    "id": "6c6af508-c5b0-4295-b92a-bfc53dfad9d3",
                                    "code": "expense_subtotal_price_after_tax",
                                    "type": 6,
                                    "title": "Expense subtotal after tax",
                                    "remark": "Subtotal after tax expense on quotation expense line",
                                    "syntax": "prop(Expense subtotal after tax)",
                                    "properties": {},
                                    "is_property": True,
                                    "syntax_show": "prop(Expense subtotal after tax)",
                                    "content_type": None,
                                }
                            ]
                        }
                    ],
                    "is_indicator": True,
                    "formula_data_show":
                    "sumItemIf(prop(Expense type)=='Chi phí triển khai',prop(Expense subtotal after tax))"
                }
            ],
            "formula_data_show": "indicator(Gross profit) - indicator(Operating costs)",
            "order": 5
        }
    ]

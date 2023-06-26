__all__ = [
    'Currency_data',
    'BaseItemUnit_data',
    'IndicatorParam_data'
]

Currency_data = {
    "14bcc332-1089-49f0-9aae-433f361fc848": {
        "title": "Đồng Việt Nam",
        "code": "VND",
        "symbol": "VND",
    },
    "e66f2870-e34f-4cd3-a9eb-78b539e80bdc": {
        "title": "United States Dollar",
        "code": "USD",
        "symbol": "$",
    },
    "6e9b6378-97fb-4b2e-ac28-7b73b2e35635": {
        "title": "Euro",
        "code": "EUR",
        "symbol": "€",
    },
    "84810a69-20cb-44f0-a4f3-d26aeb71eb76": {
        "title": "Swiss Franc",
        "code": "CHF",
        "symbol": "CHF",
    },
    "82944baf-686e-48dd-8233-e450f0a0b83c": {
        "title": "United Kingdom Pounds",
        "code": "GBP",
        "symbol": "£",
    },
    "2589a8fc-b94e-46a1-8148-ecead8f8bffe": {
        "title": "India Rupees",
        "code": "INR",
        "symbol": "₹",
    },
    "c165c3bd-3ed5-40b4-9ff2-64000206c466": {
        "title": "Australian Dollar",
        "code": "AUD",
        "symbol": "AUD",
    },
    "f3cf7feb-f7ef-492a-9362-7163547dcadb": {
        "title": "Canadian Dollar",
        "code": "CAD",
        "symbol": "CAD",
    },
    "98517b06-6d2c-4545-aa92-df0d6669cba5": {
        "title": "South African Rand",
        "code": "ZAR",
        "symbol": "R",
    },
    "6d4f8bce-7ddc-48e3-9597-538106b807b4": {
        "title": "Japanese Yen",
        "code": "JPY",
        "symbol": "JPY",
    },
    "b2c3bd13-cf72-4403-9331-a476e13169b9": {
        "title": "Chinese Yuan Renminbi",
        "code": "CNY",
        "symbol": "CNY",
    },
}

BaseItemUnit_data = {
    "4db94461-ba4b-4d5e-b9b1-1481ea38591d": {
        "title": "weight",
        "measure": 'gram'
    },
    "6b772eaa-a4a8-44d0-94e3-ab5f428ca2c1": {
        "title": "quantity",
        "measure": "unit"
    },
    "d12f696c-d435-4e93-ab8e-f2ccf5a4093b": {
        "title": "price",
        "measure": "",
    },
    "68305048-03e2-4936-8f4b-f876fcc6b14e": {
        "title": "volume",
        "measure": "cm³"
    },
}

# IndicatorParam in Base model
IndicatorParam_data = {
    # property

    # function
    "9405719c-da51-440c-8e2b-e91d779dd80e": {
        "title": "contains",
        "code": "contains",
        "remark": "Returns true if the second argument is found in the first.",
        "syntax": "contains(",
        "syntax_show": "contains(text, text)",
        "example": "contains('employee', 'emp') == true",
        "param_type": 2,
    },
    "dfcddc32-73ba-401b-9d05-d4ce650048e4": {
        "title": "empty",
        "code": "empty",
        "remark": "Tests if a value is empty.",
        "syntax": "empty(",
        "syntax_show": "empty(number), empty(text), empty(boolean), empty(date)",
        "example": "empty("") == true",
        "param_type": 2,
    },
    "b13fab07-14dd-4aff-ae56-85b066299bbe": {
        "title": "concat",
        "code": "concat",
        "remark": "Concatenates its arguments and returns the result.",
        "syntax": "concat(",
        "syntax_show": "concat(text,...)",
        "example": "concat('mon', 'key') == 'monkey'",
        "param_type": 2,
    },
    "b134be26-c97e-412e-9865-5f080222d711": {
        "title": "min",
        "code": "min",
        "remark": "Returns the smallest of zero or more numbers.",
        "syntax": "min(",
        "syntax_show": "min(number,...)",
        "example": "min(4, 1, 5, 3) == 1",
        "param_type": 2,
    },
    "14ed6103-b79a-4946-a143-87438a70826d": {
        "title": "max",
        "code": "max",
        "remark": "Returns the largest of zero or more numbers.",
        "syntax": "max(",
        "syntax_show": "max(number...)",
        "example": "max(5, 2, 9, 3) == 9",
        "param_type": 2,
    },
    "aebaf647-49ff-4d59-a738-41ed6a583b50": {
        "title": "sumItemIf",
        "code": "sumItemIf",
        "remark": "Returns total of items that pass condition.",
        "syntax": "sumItemIf(",
        "syntax_show": "sumItemIf(item_check_list, condition, item_sum_list)",
        "example": "sumItemIf((5, 2, 9, 3), '>3') == 14",
        "param_type": 2,
    }
}

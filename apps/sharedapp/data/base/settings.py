from rest_framework import serializers

from apps.shared import TypeCheck

__all__ = [
    'ApplicationConfigFrame',
    'PERMIT_MAPPING_COMPANY_DEFAULT',
]

PERMIT_MAPPING_COMPANY_DEFAULT = {
    "view": {
        "range": ["4"],
        "app_depends_on": {},
        "local_depends_on": {},
    },
    "create": {
        "range": ["4"],
        "app_depends_on": {},
        "local_depends_on": {},
    },
    "edit": {
        "range": ["4"],
        "app_depends_on": {},
        "local_depends_on": {},
    },
    "delete": {
        "range": ["4"],
        "app_depends_on": {},
        "local_depends_on": {},
    },
}


class PermitMappingChildSerializer(serializers.Serializer):  # noqa
    range = serializers.ListSerializer(
        child=serializers.CharField(), default=[],
    )
    app_depends_on = serializers.JSONField()
    local_depends_on = serializers.JSONField()

    @classmethod
    def validate_range(cls, attrs, list_or_string="list"):
        if list_or_string == 'list':
            if isinstance(attrs, list):
                for item in attrs:
                    if item not in ApplicationSerializer.range_allowed:
                        msg = f'Value must be in {str(ApplicationSerializer.range_allowed)}, not is: {str(item)}.'
                        raise serializers.ValidationError(
                            {
                                'range allow in depends': msg
                            }
                        )
                return attrs
        elif list_or_string == 'string':
            if attrs not in ApplicationSerializer.range_allowed:
                msg = f'Value must be in {str(ApplicationSerializer.range_allowed)}, not is: {str(attrs)}.'
                raise serializers.ValidationError(
                    {
                        'range allow in depends': msg
                    }
                )
            return attrs
        else:
            serializers.ValidationError({'range allow in depends': 'Type not support, choices in: [list, string]'})
        raise serializers.ValidationError({'range allow in depends': 'Value must be a list of string.'})

    @classmethod
    def validate_app_depends_on(cls, attrs):
        if isinstance(attrs, dict):
            for app_id, config in attrs.items():
                if not TypeCheck.check_uuid(app_id):
                    raise serializers.ValidationError({'app_depends_on__app_id': 'Value must be a UUID4.'})
                cls.validate_local_depends_on(config)
            return attrs
        raise serializers.ValidationError({'app_depends_on': 'Value must be a dictionary.'})

    @classmethod
    def validate_local_depends_on(cls, attrs):
        if isinstance(attrs, dict):
            for permit_code, range_str in attrs.items():
                if permit_code not in ApplicationSerializer.permit_allowed:
                    raise serializers.ValidationError({'permit_mapping': f'Permit code is not support: {str(permit_code)}'})

                if isinstance(range_str, str):
                    cls.validate_range(range_str, list_or_string='string')
                else:
                    raise serializers.ValidationError({'range allow in depends': 'Value must be a string.'})
            return attrs
        raise serializers.ValidationError({'app_depends_on': 'Value must be a dictionary.'})


class ApplicationSerializer(serializers.Serializer):  # noqa
    permit_allowed = ["view", "create", "edit", "delete"]
    range_allowed = ["1", "2", "3", "4", "==", "*"]

    id = serializers.UUIDField()
    title = serializers.CharField(max_length=100)
    code = serializers.CharField(max_length=100)
    model_code = serializers.CharField(max_length=100)
    app_label = serializers.CharField(max_length=100)
    is_workflow = serializers.BooleanField()
    app_depend_on = serializers.ListSerializer(
        child=serializers.UUIDField(), default=[], required=False
    )
    permit_mapping = serializers.JSONField()

    def validate_permit_mapping(self, attrs):
        if isinstance(attrs, dict):
            for key, value in attrs.items():
                if key not in self.permit_allowed:
                    raise serializers.ValidationError({'permit_mapping': f'Permit code is not support: {str(key)}'})

                ser_of_value = PermitMappingChildSerializer(data=value)
                ser_of_value.is_valid(raise_exception=True)

            return attrs
        raise serializers.ValidationError({'permit_mapping': 'Value must be a dictionary.'})


class ApplicationConfigFrame:
    #     "id": "4e48c863-861b-475a-aa5e-97a4ed26f294",
    #     "title": "Account",
    #     "code": "account",
    #     "model_code": "account",
    #     "app_label": "saledata",
    #     "is_workflow": True,
    #     "option_permission": 0,
    #     "option_allowed": [1, 2, 3, 4],
    #     "app_depend_on": [
    #         "50348927-2c4f-4023-b638-445469c66953",  # Employee
    #     ],
    #     "permit_mapping": {
    #         "view": {
    #             "range": ["1", "2", "3", "4"],
    #             "app_depends_on": {
    #               "{app_id}": {
    #                   "view": ["4"],
    #               },
    #             },
    #             "local_depends_on": {
    #                   "view": ["4"],
    #             },
    #         },
    #     }

    default__is_workflow = False
    default__option_permission = 0  # not use in the feature
    default__option_allowed = [4]  # not use in the feature
    default__app_depend_on = []
    default__permit_mapping = {
        "view": {
            "range": ["4"],
            "app_depends_on": {},
            "local_depends_on": {},
        },
        "create": {
            "range": ["4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "==",
            },
        },
        "edit": {
            "range": ["4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "==",
            },
        },
        "delete": {
            "range": ["4"],
            "app_depends_on": {},
            "local_depends_on": {
                "view": "==",
            },
        },
    }

    def __init__(self, **config):
        self._data: dict = {
            "is_workflow": self.default__is_workflow,
            "option_permission": self.default__option_permission,
            "option_allowed": self.default__option_allowed,
            "app_depend_on": self.default__app_depend_on,
            "permit_mapping": self.default__permit_mapping,
            **config
        }

    def valid(self):
        ser = ApplicationSerializer(data=self._data)
        ser.is_valid(raise_exception=True)
        return True

    @property
    def data(self):
        self.valid()
        return self._data

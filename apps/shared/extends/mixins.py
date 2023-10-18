from copy import deepcopy
from typing import Union

from uuid import UUID

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from django_filters import rest_framework as filters

from rest_framework import serializers, exceptions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.core.log.tasks import force_log_activity
from apps.core.workflow.tasks_not_use_import import call_log_update_at_zone

from .controllers import ResponseController
from .utils import TypeCheck
from .mask_view import ViewChecking
from .. import KEY_GET_LIST_FROM_APP, SPLIT_CODE_FROM_APP
from ..translations.server import ServerMsg
from ..translations import HttpMsg
from .tasks import call_task_background

__all__ = ['BaseMixin', 'BaseListMixin', 'BaseCreateMixin', 'BaseRetrieveMixin', 'BaseUpdateMixin', 'BaseDestroyMixin']


class DataFilterHandler:
    def __init__(self):
        ...

    @classmethod
    def get_employee_inherit_from_body_data(cls, body_data: dict[str, any]):
        if body_data and isinstance(body_data, dict):
            employee_id = body_data.get('employee_inherit_id', None)
            if employee_id and TypeCheck.check_uuid(employee_id):
                return employee_id
        return None

    @classmethod
    def push_data_to_key(cls, result, key1, key2, data):
        if key1 in result:
            if key2 in result:
                result[key1][key2] = data
            else:
                result[key1].update({key2: data})
        else:
            result.update(
                {
                    key1: {
                        key2: data,
                    }
                }
            )
        return result

    @classmethod
    def parse_value_to_simple(cls, data):
        if isinstance(data, list):
            return [str(x) for x in data]
        if isinstance(data, dict):
            return {
                str(key): str(value)
                for key, value in data.items()
            }
        return str(data)

    @classmethod
    def unzip_key_and_lookup(
            cls,
            perm_filter_dict: dict,  # {'tenant_id': '', 'employee_created_id__in': []}
    ) -> dict:
        if perm_filter_dict:
            result_parsed = {}  # {'tenant_id': {'': 'data'}, 'employee_created_id': {'in': []}}
            for key, value in perm_filter_dict.items():
                arr_key = key.split("__")
                if len(arr_key) == 1:
                    cls.push_data_to_key(result_parsed, key, '', cls.parse_value_to_simple(value))
                elif len(arr_key) == 2:
                    cls.push_data_to_key(result_parsed, arr_key[0], arr_key[1], cls.parse_value_to_simple(value))
                else:
                    raise ValueError("Don't allow filter over force relate more than 1")
            return result_parsed
        return {}

    @classmethod
    def valid_perm_by_ids(cls, perm_filter_by_ids: dict, instance_obj):
        state_allow = None
        # BY_IDS: check id of document has exists in special allow
        # *** operator: OR *** : One time True = allow, False = skip/next
        if perm_filter_by_ids and isinstance(perm_filter_by_ids, dict):  # pylint: disable=R1702
            doc_id = getattr(instance_obj, 'id', None)
            if doc_id:
                if perm_filter_by_ids and isinstance(perm_filter_by_ids, dict):
                    for key, value in perm_filter_by_ids.items():
                        if key == 'id':
                            if str(doc_id) == value:
                                state_allow = True
                                break
                            state_allow = False
                        elif key == 'id__in':
                            if str(doc_id) in value:
                                state_allow = True
                                break
                            state_allow = False
                    if state_allow is True:
                        # return True when id exists in special allow | else check by configured
                        return True
        return state_allow if isinstance(state_allow, bool) else False

    @classmethod
    def valid_perm_filter_dict(cls, perm_filter_dict: dict, employee_obj, employee_inherit_id):  # pylint: disable=R0912
        state_allow = None
        # BY_CONFIGURED: check some field data in document correct with perm configured
        # *** operator: AND *** : One time False = deny, True = skip/next
        if perm_filter_dict and isinstance(perm_filter_dict, dict):  # pylint: disable=R1702
            unzip_filter_dict = cls.unzip_key_and_lookup(perm_filter_dict)
            if unzip_filter_dict:
                for key, value in unzip_filter_dict.items():
                    if isinstance(value, dict):
                        data_left = None
                        if key == 'tenant_id':
                            data_left = str(employee_obj.tenant_id) if employee_obj.tenant_id else None
                        elif key == 'company_id':
                            data_left = str(employee_obj.company_id) if employee_obj.company_id else None
                        elif key == 'employee_inherit_id':
                            if not employee_inherit_id:
                                state_allow = False
                                break
                            data_left = str(employee_inherit_id)

                        if data_left:
                            for lookup_key, data in value.items():
                                if lookup_key == '':
                                    if data_left != data:
                                        state_allow = False
                                        break
                                    state_allow = True
                                if lookup_key == 'in':
                                    if data_left not in data:
                                        state_allow = False
                                        break
                                    state_allow = True
        return state_allow if isinstance(state_allow, bool) else False

    @classmethod
    def parse_left_and_compare(cls, employee_obj, perm_filter_dict: dict, **kwargs):  # pylint: disable=R0912
        employee_id = kwargs.get('employee_created_id', employee_obj.id)
        if employee_obj and perm_filter_dict:  # pylint: disable=R1702
            unzip_filter_dict = cls.unzip_key_and_lookup(perm_filter_dict)
            if unzip_filter_dict:
                for key, value in unzip_filter_dict.items():
                    if isinstance(value, dict):
                        data_left = None
                        if key == 'tenant_id':
                            data_left = str(employee_obj.tenant_id) if employee_obj.tenant_id else None
                        elif key == 'company_id':
                            data_left = str(employee_obj.company_id) if employee_obj.company_id else None
                        elif key == 'employee_created_id':
                            if employee_id:
                                data_left = str(employee_id)
                            else:
                                return False

                        if data_left:
                            for lookup_key, data in value.items():
                                if lookup_key == '':
                                    return data_left == data
                                if lookup_key == 'in':
                                    return data_left in data
        return False

    @classmethod
    def parse_left_and_compare_check_create(
            cls,
            employee_obj,
            perm_filter_dict: dict,
            employee_inherit_id: Union[None, UUID, str],
    ):
        return cls.valid_perm_filter_dict(
            perm_filter_dict=perm_filter_dict,
            employee_obj=employee_obj,
            employee_inherit_id=employee_inherit_id,
        )

    @classmethod
    def parse_left_and_compare_has_obj(
            cls,
            instance_obj, employee_obj,
            perm_filter_dict: dict, perm_filter_by_ids: dict,
            employee_inherit_id=Union[UUID, None],
            **kwargs
    ):
        if employee_obj:
            # BY_IDS: check id of document has exists in special allow
            # *** operator: OR *** : One time True = allow, False = skip/next
            state_allow = cls.valid_perm_by_ids(
                perm_filter_by_ids=perm_filter_by_ids,
                instance_obj=instance_obj,
            )
            if state_allow is True:
                return True

            # BY_CONFIGURED: check some field data in document correct with perm configured
            # *** operator: AND *** : One time False = deny, True = skip/next
            state_allow = cls.valid_perm_filter_dict(
                perm_filter_dict=perm_filter_dict,
                employee_obj=employee_obj,
                employee_inherit_id=employee_inherit_id,
            )
            return state_allow if isinstance(state_allow, bool) else False
        return False


class BaseMixin(GenericAPIView):  # pylint: disable=R0904
    # decorator
    cls_check: ViewChecking = None

    cls_auth_check = None  # cls authenticate of mask_view
    ser_context: dict[str, any] = {}
    search_fields: list
    filterset_fields: dict
    filterset_class: filters.FilterSet

    # for log
    log_doc_app: str = ''
    log_msg: str = ''

    # exception
    query_extend_base_model = True

    auth_required: dict = None
    perm_filter_dict: dict = None  # {'tenant_id': ''}  ### for CONFIGURED
    perm_filter_ids: dict = None  # {'id__in': []}  ### for BY_IDS
    perm_config_mapped: dict = None  # {"4": {}}  ### for CONFIGURED
    perm_by_ids_mapped: list[str] = None  # ['id1', 'id2']   ### for BY_IDS
    custom_filter_dict: dict = None  # data of get_filter_auth()  ### for function "get_filter_auth" at view class
    state_skip_is_admin: bool = False  # true/false skip auth parse ### for is_admin skip

    # **************************************
    # Serializers
    # **************************************

    # --- Serializer Class for GET LIST | has minimal
    serializer_list: serializers.Serializer = None
    serializer_list_minimal: serializers.Serializer = None

    def get_serializer_list(self, *args, **kwargs):
        """
        Get serializer class for list. Flexible with config view.
        Args:
            *args:
            **kwargs:

        Returns:

        """
        is_minimal = kwargs.pop('is_minimal', None)
        if is_minimal is True:
            tmp = getattr(self, 'serializer_list_minimal', None)
        else:
            tmp = getattr(self, 'serializer_list', None)

        if tmp and callable(tmp):
            return tmp(*args, **self.parse_ser_kwargs(kwargs))  # pylint: disable=E1102
        raise ValueError('Serializer list attribute in view must be implement.')

    # --- // Serializer Class for GET LIST | has minimal

    # --- Serializer Class for POST CREATE
    serializer_create: serializers.Serializer = None

    def get_serializer_create(self, *args, **kwargs):
        """
        Get serializer class for create
        Args:
            *args:
            **kwargs:

        Returns:

        """
        tmp = getattr(self, 'serializer_create', None)
        if tmp and callable(tmp):
            return tmp(*args, **self.parse_ser_kwargs(kwargs))  # pylint: disable=E1102
        raise ValueError('Serializer create attribute in view must be implement.')

    # --- // Serializer Class for POST CREATE

    # --- Serializer Class for return data after call POST CREATE (object just created)
    serializer_detail: serializers.Serializer = None

    def get_serializer_detail(self, *args, **kwargs):
        """
        Get serializer class for retrieve.
        Args:
            *args:
            **kwargs:

        Returns:

        """
        tmp = getattr(self, 'serializer_detail', None)
        if tmp and callable(tmp):
            return tmp(*args, **self.parse_ser_kwargs(kwargs))  # pylint: disable=E1102
        raise ValueError('Serializer detail attribute in view must be implement.')

    # --- // Serializer Class for return data after call POST CREATE (object just created)

    # --- Serializer Class for PUT data
    serializer_update: serializers.Serializer = None

    def get_serializer_update(self, *args, **kwargs):
        """
        Get serializer class for retrieve.
        Args:
            *args:
            **kwargs:

        Returns:

        """
        tmp = getattr(self, 'serializer_update', None)
        if tmp and callable(tmp):
            return tmp(*args, **self.parse_ser_kwargs(kwargs))  # pylint: disable=E1102
        raise ValueError('Serializer update attribute in view must be implement.')

    # --- // Serializer Class for PUT data

    # **************************************
    # // Serializers
    # **************************************

    # **************************************
    # Function customize
    # **************************************

    # --- Field list auto append to filter of current user request
    list_hidden_field: list[str] = []
    list_hidden_field_mapping: dict[str, any] = {}

    def list_hidden_field_manual_before(self) -> dict[str, any]:
        return {}

    def list_hidden_field_manual_after(self) -> dict[str, any]:
        return {}

    # --- // Field list auto append to filter of current user request

    # --- Field list was autofill data when POST CREATE
    create_hidden_field: list[str] = []
    create_hidden_field_mapping: dict[str, any] = {}

    def create_hidden_field_manual_before(self) -> dict[str, any]:
        """
        Autofill return value to create_hidden_fields after generate it to dict
        """
        return {}

    def create_hidden_field_manual_after(self) -> dict[str, any]:
        """
        Autofill return value to create_hidden_fields after generate it to dict
        """
        return {}

    # --- // Field list was autofill data when POST CREATE

    # --- Field list auto append to filtering of current user request
    retrieve_hidden_field: list[str] = []
    retrieve_hidden_field_mapping: dict[str, any] = {}

    def retrieve_hidden_field_manual_before(self) -> dict[str, any]:
        """
        Autofill return value to retrieve_hidden_fields after generate it to dict
        """
        return {}

    def retrieve_hidden_field_manual_after(self) -> dict[str, any]:
        """
        Autofill return value to retrieve_hidden_fields after generate it to dict
        """
        return {}

    # --- // Field list auto append to filtering of current user request

    # --- Field list was autofill data when PUT UPDATE
    update_hidden_field: list[str] = []
    update_hidden_field_mapping: dict[str, any] = {}

    def update_hidden_field_manual_before(self) -> dict[str, any]:
        """
        Autofill return value to update_hidden_fields after generate it to dict
        """
        return {}

    def update_hidden_field_manual_after(self) -> dict[str, any]:
        """
        Autofill return value to update_hidden_fields after generate it to dict
        """
        return {}

    # --- // Field list was autofill data when PUT UPDATE

    # **************************************
    # // Function customize
    # **************************************

    def get_filter_auth(self) -> dict:
        """
        Function customize get_filter (self.filter_dict) in view for special case
        Returns:
            dict
        Notes:
            You need override it when use_get_filter=True in view | or take care to *_filter_hidden attribute
        """
        return {}

    def check_permit_one_time(
            self, employee_inherit_id, opportunity_id, project_id, hidden_field, obj=None, body_data=None
    ):
        if project_id and opportunity_id:
            # Opp and Project can't have together value.
            return False

        if employee_inherit_id and TypeCheck.check_uuid(employee_inherit_id):
            if opportunity_id and TypeCheck.check_uuid(opportunity_id):
                return self.cls_check.permit_cls.config_data__check_by_opp(
                    opp_id=opportunity_id,
                    employee_inherit_id=employee_inherit_id,
                    hidden_field=hidden_field,
                )
            if project_id and TypeCheck.check_uuid(project_id):
                return self.cls_check.permit_cls.config_data__check_by_prj(
                    prj_id=project_id,
                    employee_inherit_id=employee_inherit_id,
                    hidden_field=hidden_field,
                )
        if obj and body_data:
            return self.cls_check.permit_cls.config_data__check_obj_and_body_data(obj=obj, body_data=body_data)
        elif obj:
            return self.cls_check.permit_cls.config_data__check_obj(obj=obj)
        elif body_data:
            return self.cls_check.permit_cls.config_data__check_body_data(body_data=body_data)
        return False

    def check_perm_by_obj_or_body_data(
            self, obj=None, body_data=None, hidden_field: list[str] = list
    ) -> bool:  # pylint: disable=R0911
        """
        Check permission with Instance Object was got from views
        Args:
            hidden_field:
            body_data: Request.body_data
            obj: Instance object

        Returns:
            True: Allow
            False: Deny
        """
        if obj or body_data:
            if self.cls_check.skip_because_match_with_admin is True:
                # allow when flag is_admin skip turn on
                return True

            if self.cls_check.decor.auth_require is True:
                if self.cls_check.permit_cls.config_data__exist:
                    if obj is not None and body_data is not None:
                        opportunity_id__obj = getattr(obj, self.cls_check.permit_cls.KEY_FILTER_OPP_ID_IN_MODEL, None)
                        project_id__obj = getattr(obj, self.cls_check.permit_cls.KEY_FILTER_PRJ_ID_IN_MODEL, None)
                        employee_inherit_id__obj = getattr(
                            obj, self.cls_check.permit_cls.KEY_FILTER_INHERITOR_ID_IN_MODEL, None,
                        )
                        state = self.check_permit_one_time(
                            employee_inherit_id=employee_inherit_id__obj,
                            opportunity_id=opportunity_id__obj,
                            project_id=project_id__obj,
                            hidden_field=hidden_field,
                            obj=obj, body_data=body_data,
                        )
                        if state is True:
                            opportunity_id__body = body_data.get(
                                self.cls_check.permit_cls.KEY_FILTER_OPP_ID_IN_MODEL, opportunity_id__obj
                            )
                            project_id__body = body_data.get(
                                self.cls_check.permit_cls.KEY_FILTER_PRJ_ID_IN_MODEL, project_id__obj
                            )
                            employee_inherit_id__body = body_data.get(
                                self.cls_check.permit_cls.KEY_FILTER_INHERITOR_ID_IN_MODEL, employee_inherit_id__obj
                            )
                            state = self.check_permit_one_time(
                                employee_inherit_id=employee_inherit_id__body,
                                opportunity_id=opportunity_id__body,
                                project_id=project_id__body,
                                hidden_field=hidden_field,
                                obj=obj, body_data=body_data,
                            )
                        return state
                    elif obj is not None:
                        opportunity_id = getattr(obj, self.cls_check.permit_cls.KEY_FILTER_OPP_ID_IN_MODEL, None)
                        project_id = getattr(obj, self.cls_check.permit_cls.KEY_FILTER_PRJ_ID_IN_MODEL, None)
                        employee_inherit_id = getattr(
                            obj,
                            self.cls_check.permit_cls.KEY_FILTER_INHERITOR_ID_IN_MODEL,
                            None,
                        )
                        return self.check_permit_one_time(
                            employee_inherit_id=employee_inherit_id,
                            opportunity_id=opportunity_id,
                            project_id=project_id,
                            hidden_field=hidden_field,
                            obj=obj, body_data=body_data,
                        )
                    elif body_data is not None:
                        opportunity_id = body_data.get(self.cls_check.permit_cls.KEY_FILTER_OPP_ID_IN_MODEL, None)
                        project_id = body_data.get(self.cls_check.permit_cls.KEY_FILTER_PRJ_ID_IN_MODEL, None)
                        employee_inherit_id = body_data.get(
                            self.cls_check.permit_cls.KEY_FILTER_INHERITOR_ID_IN_MODEL, None
                        )
                        return self.check_permit_one_time(
                            employee_inherit_id=employee_inherit_id,
                            opportunity_id=opportunity_id,
                            project_id=project_id,
                            hidden_field=hidden_field,
                            obj=obj, body_data=body_data,
                        )
                    return False
                return False
            return True
        return False

    class Meta:
        abstract = True

    def get_serializer_class(self):
        """
        Get serializer_class for generate API documentations
        """
        if getattr(self, 'serializer_list', None):
            return getattr(self, 'serializer_list', None)
        if getattr(self, 'serializer_detail', None):
            return getattr(self, 'serializer_detail', None)
        if getattr(self, 'serializer_create', None):
            return getattr(self, 'serializer_create', None)
        if getattr(self, 'serializer_update', None):
            return getattr(self, 'serializer_update', None)
        raise AttributeError(
            f'{self.__class__.__name__} must be required serializer_list or serializer_detail attribute.'
        )

    @staticmethod
    def setup_hidden(fields: list, user) -> dict:
        """
        Fill data of hidden_fields
        Args:
            fields:
            user:

        Returns:

        """
        ctx = {}
        for key in fields:
            data = None
            match key:
                case 'tenant_id':
                    data = user.tenant_current_id
                case 'tenant':
                    data = user.tenant_current
                case 'company_id':
                    data = user.company_current_id
                case 'company':
                    data = user.company_current
                case 'space_id':
                    data = user.space_current_id
                case 'space':
                    data = user.space_current
                case 'mode_id':
                    data = getattr(user, 'mode_id', 0)
                case 'mode':
                    data = getattr(user, 'mode', 0)
                case 'employee_created_id':
                    data = user.employee_current_id
                case 'employee_modified_id':
                    data = user.employee_current_id
                case 'employee_id':
                    data = user.employee_current_id
                case 'user_id':
                    data = user.id
                case 'employee_inherit_id':
                    data = user.employee_current_id
            if data is not None:
                ctx[key] = data
        return ctx

    @staticmethod
    def parse_header(request) -> tuple[bool, bool]:
        """
        Parse flag data in request header.
        Args:
            request: REQUEST OF VIEW

        Returns:
            bool(minimal), bool(skip_auth)
        """
        skip_auth = request.META.get(
            'HTTP_DATAISSKIPAUTH',
            None
        ) == settings.HEADER_SKIP_AUTH_CODE if settings.HEADER_SKIP_AUTH_CODE else False
        minimal = request.META.get(
            'HTTP_DATAISMINIMAL',
            None
        ) == settings.HEADER_MINIMAL_CODE if settings.HEADER_MINIMAL_CODE else False

        return minimal, skip_auth

    # Flag is enable cache queryset of view
    use_cache_queryset: bool = False
    # Flag is enable cache queryset minimal view **NOT APPLY FOR CASE HAD RELATE**
    use_cache_minimal: bool = False
    # Flag is enable cache get_object data
    use_cache_object: bool = False

    def parse_ser_kwargs(self, kwargs: dict):
        if 'context' not in kwargs:
            kwargs['context'] = self.ser_context
        return kwargs

    def filter_append_manual(self) -> dict:
        return {}

    @property
    def get_object__field_hidden(self):
        return self.cls_check.attr.setup_hidden(from_view='retrieve')

    def get_lookup_url_kwarg(self) -> dict:
        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            f'Expected view {self.__class__.__name__} to be called with a URL keyword argument '
            f'named "{lookup_url_kwarg}". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.'
        )

        return {self.lookup_field: self.kwargs[lookup_url_kwarg]}

    def get_object(self):
        """
        [OVERRODE from REST FRAMEWORK]
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        if not hasattr(queryset, "get"):
            klass__name = (
                queryset.__name__ if isinstance(queryset, type) else queryset.__class__.__name__
            )
            raise ValueError(
                "First argument to get_object_or_404() must be a Model, Manager, "
                f"or QuerySet, not '{klass__name}'."
            )
        try:
            field_hidden = self.get_object__field_hidden
            filter_kwargs = self.get_lookup_url_kwarg()
            if self.query_extend_base_model:
                obj = queryset.get(
                    **filter_kwargs,
                    **field_hidden,
                    force_cache=self.use_cache_object
                )
            else:
                obj = queryset.get(
                    **filter_kwargs,
                    **field_hidden,
                )
            # May raise a permission denied
            self.check_object_permissions(self.request, obj)
            return obj
        except queryset.model.DoesNotExist:
            raise exceptions.NotFound

    @classmethod
    def check_obj_change_or_delete(cls, instance):
        if instance and hasattr(instance, 'system_status') and getattr(instance, 'system_status', None) == 3:
            return False
        return True

    def get_default_doc_app(self) -> str:
        if not self.log_doc_app:
            if self.queryset:
                cls_queryset = self.queryset.__class__
                if hasattr(cls_queryset, 'get_model_code'):
                    return cls_queryset.get_model_code()
            return ''
        return self.log_doc_app

    def get_default_log_msg(self, task_id=None) -> str:
        real_msg = ''
        if not self.log_msg:
            match self.request.method.upper():
                case 'GET':
                    real_msg = 'Get list or detail'
                case 'POST':
                    real_msg = 'Create new'
                case 'PUT':
                    real_msg = 'Update record'
                case 'DELETE':
                    real_msg = 'Destroy record'
        else:
            real_msg = self.log_msg
        if task_id:
            return real_msg + " at Zone's Workflow"
        return real_msg

    def write_log(
            self, doc_obj, request_data: dict = None, change_partial: bool = False, task_id: Union[UUID, str] = None,
    ):
        user = self.request.user
        call_task_background(
            force_log_activity,
            **{
                'tenant_id': user.tenant_current_id,
                'company_id': user.company_current_id,
                'request_method': self.request.method.upper(),
                'date_created': timezone.now(),
                'doc_id': doc_obj.id,
                'doc_app': self.get_default_doc_app(),
                'automated_logging': False,
                'user_id': user.id,
                'employee_id': user.employee_current_id,
                'msg': self.get_default_log_msg(task_id=task_id),
                'data_change': request_data if isinstance(request_data, dict) else self.request.data,
                'change_partial': change_partial,
                'task_workflow_id': task_id,
            },
        )
        if task_id:
            call_task_background(
                call_log_update_at_zone,
                *[task_id, user.employee_current_id],
            )
        return True

    def error_employee_require(self):
        return ResponseController.forbidden_403()

    def error_auth_require(self):
        return ResponseController.forbidden_403()

    def error_login_require(self):
        return ResponseController.unauthorized_401()


class BaseListMixin(BaseMixin):
    LIST_HIDDEN_FIELD_DEFAULT = ['tenant_id', 'company_id']  # DataAbstract
    LIST_MASTER_DATA_FIELD_HIDDEN_DEFAULT = ['tenant_id', 'company_id']  # MasterData

    @classmethod
    def list_empty(cls) -> Response:
        return ResponseController.success_200(data=[], key_data='result')

    def get_object(self):
        raise TypeError("Not allow use get_object() for List Mixin.")

    def get_query_params(self) -> dict:
        return self.request.query_params.dict()

    def has_get_list_from_app(self) -> (bool, Union[list[str], None]):
        """
        Return state from_app and data if exist
        """
        query_params = self.get_query_params()
        if KEY_GET_LIST_FROM_APP in query_params:
            from_app = query_params.get(KEY_GET_LIST_FROM_APP, None)
            if from_app and isinstance(from_app, str) and SPLIT_CODE_FROM_APP in from_app and len(from_app) > 3:
                arr_from_app = [ite.strip() for ite in from_app.split(SPLIT_CODE_FROM_APP)]
                if len(arr_from_app) == 3:
                    return True, arr_from_app
            return True, None
        return False, None

    def filter_kwargs_q__from_config(self) -> Q:
        """
        Parse config mapped with view to Q() (use for filter in queryset)
        """
        return self.cls_check.permit_cls.config_data__to_q

    def filter_kwargs_q__from_app(self, arr_from_app) -> Q:
        """
        Parse config mapped from_app to Q() (use for filter in queryset - for DD another feature)
        """
        return Q(id__in=[])

    @property
    def filter_kwargs_q(self) -> Union[Q, Response]:
        """
        Check case get list opp for feature or list by configured.
        query_params: from_app=app_label-model_code
        """
        state_from_app, data_from_app = self.has_get_list_from_app()
        if state_from_app is True:
            if data_from_app and isinstance(data_from_app, list) and len(data_from_app) == 3:
                return self.filter_kwargs_q__from_app(data_from_app)
            return self.list_empty()
        return self.filter_kwargs_q__from_config()

    @property
    def filter_kwargs(self) -> dict[str, any]:
        return {
            **self.kwargs,
            **self.cls_check.attr.setup_hidden(from_view='list'),
        }

    def get_queryset_and_filter_queryset(self, is_minimal, filter_kwargs, filter_kwargs_q):
        if is_minimal is True:
            if self.use_cache_minimal and self.query_extend_base_model:
                queryset = self.filter_queryset(
                    self.queryset.filter(**filter_kwargs).filter(filter_kwargs_q)
                ).cache()
            else:
                queryset = self.filter_queryset(
                    self.queryset.filter(**filter_kwargs).filter(filter_kwargs_q)
                )
        else:
            if self.use_cache_queryset and self.query_extend_base_model:
                queryset = self.filter_queryset(
                    self.get_queryset().filter(**filter_kwargs).filter(filter_kwargs_q)
                ).cache()
            else:
                queryset = self.filter_queryset(
                    self.get_queryset().filter(**filter_kwargs).filter(filter_kwargs_q)
                )
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Support call get list data.
        Args:
            request:
            *args:
            **kwargs:

        Returns:

        """
        is_minimal, _is_skip_auth = self.parse_header(request)

        filter_kwargs_q = self.filter_kwargs_q
        if isinstance(filter_kwargs_q, Response):
            return filter_kwargs_q

        filter_kwargs = self.filter_kwargs
        if settings.DEBUG_PERMIT:
            print('# MIXINS.LIST              :', request.path, )
            print('#     - filter_kwargs_q    :', filter_kwargs_q)
            print('#     - filter_kwargs      :', filter_kwargs)
        queryset = self.get_queryset_and_filter_queryset(
            is_minimal=is_minimal,
            filter_kwargs=filter_kwargs,
            filter_kwargs_q=filter_kwargs_q
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer_list(page, many=True, is_minimal=is_minimal)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer_list(queryset, many=True, is_minimal=is_minimal)
        return ResponseController.success_200(data=serializer.data, key_data='result')


class BaseCreateMixin(BaseMixin):
    CREATE_HIDDEN_FIELD_DEFAULT = [
        'tenant_id', 'company_id',
        'employee_created_id',
        'employee_inherit_id',
    ]  # DataAbstract
    CREATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT = ['tenant_id', 'company_id', 'employee_created_id']  # MasterData

    def manual_check_obj_create(self, body_data, **kwargs) -> Union[None, bool]:
        """
        Manual check object | None: continue auto check, Bool: Return by state
        """
        return None

    def get_serializer_detail_return(self, obj):
        return self.get_serializer_detail(obj).data

    def create(self, request, *args, **kwargs):
        field_hidden = self.cls_check.attr.setup_hidden(from_view='create')
        body_data = {**request.data, **field_hidden}

        state_check = self.manual_check_obj_create(body_data=body_data)
        if state_check is None:
            state_check = self.check_perm_by_obj_or_body_data(
                body_data=body_data, hidden_field=self.create_hidden_field
            )
        if state_check is True:
            log_data = deepcopy(request.data)
            serializer = self.get_serializer_create(data=request.data)
            serializer.is_valid(raise_exception=True)
            obj = self.perform_create(serializer, extras=field_hidden)
            self.write_log(doc_obj=obj, request_data=log_data)
            return ResponseController.created_201(data=self.get_serializer_detail_return(obj))
        return ResponseController.forbidden_403()

    @staticmethod
    def perform_create(serializer, extras: dict):
        try:
            with transaction.atomic():
                return serializer.save(**extras)
        except serializers.ValidationError as err:
            raise err
        except Exception as err:
            print(err)
        raise serializers.ValidationError({'detail': ServerMsg.UNDEFINED_ERR})


class BaseRetrieveMixin(BaseMixin):
    RETRIEVE_HIDDEN_FIELD_DEFAULT = ['tenant_id', 'company_id']  # DataAbstract
    RETRIEVE_MASTER_DATA_FIELD_HIDDEN_DEFAULT = ['tenant_id', 'company_id']  # MasterData

    @classmethod
    def retrieve_empty(cls) -> Response:
        return ResponseController.success_200(data={}, key_data='result')

    def manual_check_obj_retrieve(self, instance, **kwargs) -> Union[None, bool]:
        """
        Manual check object | None: continue auto check, Bool: Return by state
        """
        return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        state_check = self.manual_check_obj_retrieve(instance=instance)
        if state_check is None:
            state_check = self.check_perm_by_obj_or_body_data(obj=instance, hidden_field=self.retrieve_hidden_field)
        if state_check is True:
            serializer = self.get_serializer_detail(instance)
            return ResponseController.success_200(data=serializer.data, key_data='result')
        return ResponseController.forbidden_403()


class BaseUpdateMixin(BaseMixin):
    UPDATE_HIDDEN_FIELD_DEFAULT = ['employee_modified_id']  # DataAbstract
    UPDATE_MASTER_DATA_FIELD_HIDDEN_DEFAULT = ['employee_modified_id']  # MasterData

    @classmethod
    def parsed_body(cls, instance, request_data, user) -> (dict, bool, Union[UUID, str, None]):
        """
        Parse request body and return it with partial is True/False.
        Args:
            instance: Model Object
            request_data: request.data
            user: request user object

        Returns:
            request_data: Data parsed with remove key don't accept edit in zone, else return input request_data
            partial: True if request_data don't exist task_id else False (update some field or all field)
        """
        workflow_runtime = getattr(instance, 'workflow_runtime', None)
        if workflow_runtime and hasattr(workflow_runtime, 'find_task_id_get_zones'):
            task_id = request_data.get('task_id', None)
            if task_id and TypeCheck.check_uuid(task_id):
                state, code_field_arr = workflow_runtime.find_task_id_get_zones(
                    task_id=task_id, employee_id=user.employee_current_id
                )
                if state is True:
                    new_body_data = {}
                    for key, value in request_data.items():
                        if key in code_field_arr:
                            new_body_data[key] = value
                    return new_body_data, True, task_id
                # check permission default | wait implement so it is True
        return request_data, False, None

    def manual_check_obj_update(self, instance, body_data, **kwargs) -> Union[None, bool]:
        """
        Manual check object | None: continue auto check, Bool: Return by state
        """
        return None

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.check_obj_change_or_delete(instance):
            field_hidden = self.cls_check.attr.setup_hidden(from_view='update')
            body_data = {
                **request.data,
                **field_hidden
            }

            state_check = self.manual_check_obj_update(instance=instance, body_data=body_data)
            if state_check is None:
                state_check = self.check_perm_by_obj_or_body_data(
                    obj=instance,
                    body_data=body_data,
                    hidden_field=self.update_hidden_field,
                )
            if state_check is True:
                body_data, partial, task_id = self.parsed_body(
                    instance=instance, request_data=request.data, user=request.user
                )
                serializer = self.get_serializer_update(instance, data=body_data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer, extras=field_hidden)
                # request force write log
                self.write_log(doc_obj=instance, request_data=body_data, change_partial=partial, task_id=task_id)
                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}  # pylint: disable=W0212

                return ResponseController.success_200(data={'detail': HttpMsg.SUCCESSFULLY}, key_data='result')
            return ResponseController.forbidden_403()
        return ResponseController.forbidden_403(msg=HttpMsg.OBJ_DONE_NO_EDIT)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @staticmethod
    def perform_update(serializer, extras: dict = None):
        try:
            with transaction.atomic():
                if not extras:
                    extras = {}
                return serializer.save(**extras)
        except serializers.ValidationError as err:
            raise err
        except Exception as err:
            print(err)
        raise serializers.ValidationError({'detail': ServerMsg.UNDEFINED_ERR})


class BaseDestroyMixin(BaseMixin):
    def manual_check_obj_destroy(self, instance, **kwargs) -> Union[None, bool]:
        """
        Manual check object | None: continue auto check, Bool: Return by state
        """
        return None

    def destroy(self, request, *args, **kwargs):
        is_purge = kwargs.pop('is_purge', False)
        instance = self.get_object()
        if self.check_obj_change_or_delete(instance):
            state_check = self.manual_check_obj_destroy(instance=instance)
            if state_check is None:
                state_check = self.check_perm_by_obj_or_body_data(
                    obj=instance,
                    hidden_field=self.retrieve_hidden_field,
                )
            if state_check is True:
                self.perform_destroy(instance, is_purge)
                return ResponseController.no_content_204()
            return ResponseController.forbidden_403()
        return ResponseController.forbidden_403(msg=HttpMsg.OBJ_DONE_NO_EDIT)

    @staticmethod
    def perform_destroy(instance, is_purge=False):
        try:
            with transaction.atomic():
                if is_purge is True:
                    ...
                return instance.delete()
        except serializers.ValidationError as err:
            raise err
        except Exception as err:
            print(err)
        raise serializers.ValidationError({'detail': ServerMsg.UNDEFINED_ERR})

from copy import deepcopy
from typing import Union
from uuid import UUID
from django.conf import settings
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import serializers, exceptions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.core.log.tasks import force_log_activity
from apps.core.workflow.tasks_not_use_import import call_log_update_at_zone

from .controllers import ResponseController
from .utils import TypeCheck
from ..translations import HttpMsg
from .tasks import call_task_background

__all__ = ['BaseMixin', 'BaseListMixin', 'BaseCreateMixin', 'BaseRetrieveMixin', 'BaseUpdateMixin', 'BaseDestroyMixin']


class DataFilterHandler:
    def __init__(self):
        ...

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


class BaseMixin(GenericAPIView):  # pylint: disable=R0904
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
    perm_filter_dict: dict = None  # {'tenant_id': ''}
    perm_config_mapped: dict = None  # {"4": {}}
    custom_filter_dict: dict = None  # data of get_filter_auth()
    state_skip_is_admin: bool = False

    def get_filter_auth(self) -> dict:
        """
        Function customize get_filter (self.filter_dict) in view for special case
        Returns:
            dict
        Notes:
            You need override it when use_get_filter=True in view | or take care to *_filter_hidden attribute
        """
        return {}

    def append_filter_authenticate_for_list(self, main_filter: dict) -> dict:
        really_filter = {}
        if self.custom_filter_dict:
            really_filter = self.custom_filter_dict
        elif self.perm_filter_dict:
            really_filter = self.perm_filter_dict

        return {
            **main_filter,
            **really_filter,
        }

    def check_perm_create(self, body_data: dict, employee_obj=None):
        if self.state_skip_is_admin is True:
            return True

        if self.auth_required is True:
            if not employee_obj:
                if hasattr(self.request.user, 'employee_current'):
                    employee_obj = self.request.user.employee_current
                else:
                    return False

            if employee_obj and hasattr(employee_obj, 'id') and self.perm_config_mapped:
                employee_created_id = body_data.get('employee_created', employee_obj.id)
                return DataFilterHandler.parse_left_and_compare(
                    employee_obj, self.perm_filter_dict,
                    employee_created_id=employee_created_id,
                )
            return False
        return True  # always allow when view has auth_required = False

    def check_perm_by_obj(self, obj, employee_obj=None):
        if self.state_skip_is_admin is True:
            return True

        if self.auth_required is True:
            if not employee_obj:
                if hasattr(self.request.user, 'employee_current'):
                    employee_obj = self.request.user.employee_current
                else:
                    return False
            print('employee_created_id: ', getattr(obj, 'employee_created_id', '1'))
            return DataFilterHandler.parse_left_and_compare(
                employee_obj, self.perm_filter_dict,
                **({'employee_created_id': obj.employee_created_id} if hasattr(obj, 'employee_created_id') else {}),
            )
        return True  # always allow when view has auth_required = False

    class Meta:
        abstract = True

    def get_serializer_class(self):
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

    def setup_create_field_hidden(self, user) -> dict:
        """
        Fill data of hidden fields when create
        Args:
            user:

        Returns:

        """
        return self.setup_hidden(self.create_hidden_field, user)

    def setup_update_field_hidden(self, user) -> dict:
        """
        Fill data of hidden fields when create
        Args:
            user:

        Returns:

        """
        return self.setup_hidden(self.update_hidden_field, user)

    def setup_list_field_hidden(self, user) -> dict:
        """
        Fill data of hidden fields when list data
        Args:
            user:

        Returns:

        """
        return self.append_filter_authenticate_for_list(self.setup_hidden(self.list_hidden_field, user))

    def setup_retrieve_field_hidden(self, user) -> dict:
        """
        Fill data of hidden fields when retrieve data
        Args:
            user:

        Returns:

        """
        return self.setup_hidden(self.retrieve_hidden_field, user)

    # Serializer Class for GET LIST
    serializer_list: serializers.Serializer = None
    # Serializer Class for GET LIST with MINIMAL DATA **NOT APPLY FOR CASE HAD RELATE**
    serializer_list_minimal: serializers.Serializer = None
    # Serializer Class for POST CREATE
    serializer_create: serializers.Serializer = None
    # Serializer Class for return data after call POST CREATE (object just created)
    serializer_detail: serializers.Serializer = None
    # Serializer Class for PUT data
    serializer_update: serializers.Serializer = None
    # Field list auto append to filter of current user request
    list_hidden_field: list[str] = []
    # Field list was autofill data when POST CREATE
    create_hidden_field: list[str] = []
    # Field list was autofill data when PUT UPDATE
    update_hidden_field: list[str] = []
    # Field list auto append to filtering of current user request
    retrieve_hidden_field: list[str] = []
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

    def get_object(self):
        """
        [OVERRODE from REST FRAMEWORK]
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            f'Expected view {self.__class__.__name__} to be called with a URL keyword argument '
            f'named "{lookup_url_kwarg}". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.'
        )

        if not hasattr(queryset, "get"):
            klass__name = (
                queryset.__name__ if isinstance(queryset, type) else queryset.__class__.__name__
            )
            raise ValueError(
                "First argument to get_object_or_404() must be a Model, Manager, "
                f"or QuerySet, not '{klass__name}'."
            )
        try:
            filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            if self.query_extend_base_model:
                obj = queryset.get(
                    **filter_kwargs,
                    **self.setup_retrieve_field_hidden(user=self.request.user),
                    force_cache=self.use_cache_object
                )
            else:
                obj = queryset.get(
                    **filter_kwargs,
                    **self.setup_retrieve_field_hidden(user=self.request.user),
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
    @classmethod
    def list_empty(cls) -> Response:
        return ResponseController.success_200(data=[], key_data='result')

    def get_object(self):
        raise TypeError("Not allow use get_object() for List Mixin.")

    def setup_filter_queryset(self, user, filter_kwargs, is_minial_queryset):
        """
        Get queryset switch any case of minimal and caching.
        Args:
            user: User Obj
            filter_kwargs: kwargs of view mixin
            is_minial_queryset: boolean | enable minimal queryset

        Returns:
            QuerySet, PageQuerySet
        """
        filter_kwargs.update(self.setup_list_field_hidden(user))

        if is_minial_queryset is True:
            if self.use_cache_minimal and self.query_extend_base_model:
                queryset = self.filter_queryset(self.queryset.filter(**filter_kwargs)).cache()
            else:
                queryset = self.filter_queryset(self.queryset.filter(**filter_kwargs))
        else:
            if self.use_cache_queryset and self.query_extend_base_model:
                queryset = self.filter_queryset(self.get_queryset().filter(**filter_kwargs)).cache()
            else:
                queryset = self.filter_queryset(self.get_queryset().filter(**filter_kwargs))

        page = self.paginate_queryset(queryset)
        if page is not None:
            return None, page
        return queryset, None

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
        queryset, page = self.setup_filter_queryset(
            user=request.user,
            filter_kwargs=kwargs,
            is_minial_queryset=is_minimal
        )
        if page is not None:
            serializer = self.get_serializer_list(page, many=True, is_minimal=is_minimal)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer_list(queryset, many=True, is_minimal=is_minimal)
        return ResponseController.success_200(data=serializer.data, key_data='result')


class BaseCreateMixin(BaseMixin):
    def create(self, request, *args, **kwargs):
        if self.check_perm_create(body_data=request.data):
            log_data = deepcopy(request.data)
            serializer = self.get_serializer_create(data=request.data)
            serializer.is_valid(raise_exception=True)
            field_hidden = self.setup_create_field_hidden(request.user)
            obj = self.perform_create(serializer, extras=field_hidden)
            self.write_log(doc_obj=obj, request_data=log_data)
            return ResponseController.created_201(data=self.get_serializer_detail(obj).data)
        return ResponseController.forbidden_403()

    @staticmethod
    def perform_create(serializer, extras: dict):
        return serializer.save(**extras)


class BaseRetrieveMixin(BaseMixin):
    @classmethod
    def retrieve_empty(cls) -> Response:
        return ResponseController.success_200(data={}, key_data='result')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.check_perm_by_obj(obj=instance):
            serializer = self.get_serializer_detail(instance)
            return ResponseController.success_200(data=serializer.data, key_data='result')
        return ResponseController.forbidden_403()


class BaseUpdateMixin(BaseMixin):
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.check_obj_change_or_delete(instance):
            if self.check_perm_by_obj(obj=instance):
                body_data, partial, task_id = self.parsed_body(
                    instance=instance, request_data=request.data, user=request.user
                )
                serializer = self.get_serializer_update(instance, data=body_data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
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
    def perform_update(serializer):
        serializer.save()


class BaseDestroyMixin(BaseMixin):
    def destroy(self, request, *args, **kwargs):
        is_purge = kwargs.pop('is_purge', False)
        instance = self.get_object()
        if self.check_obj_change_or_delete(instance):
            if self.check_perm_by_obj(obj=instance):
                self.perform_destroy(instance, is_purge)
                return ResponseController.no_content_204()
            return ResponseController.forbidden_403()
        return ResponseController.forbidden_403(msg=HttpMsg.OBJ_DONE_NO_EDIT)

    @staticmethod
    def perform_destroy(instance, is_purge=False):
        if is_purge is True:
            ...
        instance.delete()

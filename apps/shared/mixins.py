from rest_framework.generics import GenericAPIView
from apps.shared import ResponseController, HttpMsg


class BaseMixin(GenericAPIView):
    def __init__(self, *args, **kwargs):
        serializer_list = getattr(self, 'serializer_list', None)
        serializer_detail = getattr(self, 'serializer_detail', None)
        if serializer_list:
            self.serializer_class = self.serializer_list
        elif serializer_detail:
            self.serializer_class = self.serializer_detail
        else:
            raise AttributeError(
                f'{self.__class__.__name__} must be required serializer_list or serializer_detail attribute in class view.'
            )

        super().__init__(*args, **kwargs)

    @staticmethod
    def setup_hidden(fields: list, user) -> dict:
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
                case 'user_created':
                    data = user.id
            if data is not None:
                ctx[key] = data
        return ctx

    def setup_create_field_hidden(self, user) -> dict:
        return self.setup_hidden(self.create_hidden_field, user)

    def setup_list_field_hidden(self, user) -> dict:
        return self.setup_hidden(self.list_hidden_field, user)

    def setup_retrieve_field_hidden(self, user) -> dict:
        return self.setup_hidden(self.retrieve_hidden_field, user)

    serializer_list = None
    serializer_create = None
    serializer_detail = None
    list_hidden_field = []
    create_hidden_field = []
    retrieve_hidden_field = []

    def get_serializer_list(self, *args, **kwargs):
        tmp = getattr(self, 'serializer_list', None)
        if tmp:
            return tmp(*args, **kwargs)
        raise ValueError('Serializer list attribute in view must be implement.')

    def get_serializer_create(self, *args, **kwargs):
        tmp = getattr(self, 'serializer_create', None)
        if tmp:
            return tmp(*args, **kwargs)
        raise ValueError('Serializer create attribute in view must be implement.')

    def get_serializer_detail(self, *args, **kwargs):
        tmp = getattr(self, 'serializer_detail', None)
        if tmp:
            return tmp(*args, **kwargs)
        raise ValueError('Serializer detail attribute in view must be implement.')


class BaseListMixin(BaseMixin):
    def list(self, request, *args, **kwargs):
        kwargs.update(self.setup_list_field_hidden(request.user))
        queryset = self.filter_queryset(self.get_queryset().filter(**kwargs))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer_list(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer_list(queryset, many=True)
        return ResponseController.success_200(data=serializer.data, key_data='result')


class BaseCreateMixin(BaseMixin):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_create(data=request.data)
        serializer.is_valid(raise_exception=True)
        field_hidden = self.setup_create_field_hidden(request.user)
        obj = self.perform_create(serializer, extras=field_hidden)
        return ResponseController.created_201(data=self.get_serializer_detail(obj).data)

    @staticmethod
    def perform_create(serializer, extras: dict):
        return serializer.save(**extras)


class BaseRetrieveMixin(BaseMixin):
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer_detail(instance)
        return ResponseController.success_200(data=serializer.data, key_data='result')


class BaseUpdateMixin(BaseMixin):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return ResponseController.success_200(data={'detail': HttpMsg.SUCCESSFULLY}, key_data='result')

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @staticmethod
    def perform_update(serializer):
        serializer.save()


class BaseDestroyMixin(BaseMixin):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ResponseController.no_content_204()

    @staticmethod
    def perform_destroy(instance):
        instance.delete()

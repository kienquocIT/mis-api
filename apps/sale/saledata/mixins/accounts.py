from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.sale.saledata.models import Salutation, Interest, AccountType, Industry, Account, Contact
from apps.shared import ResponseController, BaseCreateMixin, BaseUpdateMixin, HttpMsg
from apps.shared.translations.accounts import AccountsMsg


class SalutationCreateMixin(BaseCreateMixin): # noqa
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_create(data=request.data)
        serializer.is_valid(raise_exception=True)
        field_hidden = self.setup_create_field_hidden(request.user)

        salutation_list = Salutation.object_normal.filter(tenant_id=request.user.tenant_current_id)
        if request.data.get('code', None) in salutation_list.values_list("code", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.CODE_EXIST)
        if request.data.get('title', None) in salutation_list.values_list("title", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.NAME_EXIST)

        obj = self.perform_create(serializer, extras=field_hidden)
        return ResponseController.created_201(data=self.get_serializer_detail(obj).data)


class SalutationUpdateMixin(BaseUpdateMixin):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        salutation_list = Salutation.object_normal.filter(tenant_id=instance.tenant_id)
        if request.data.get('code', None) != instance.code and request.data.get('code', None) in salutation_list.values_list("code", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.CODE_EXIST)
        if request.data.get('title', None) != instance.title and request.data.get('title', None) in salutation_list.values_list("title", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.NAME_EXIST)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return ResponseController.success_200(data={'detail': HttpMsg.SUCCESSFULLY}, key_data='result')


class InterestCreateMixin(BaseCreateMixin): # noqa
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_create(data=request.data)
        serializer.is_valid(raise_exception=True)
        field_hidden = self.setup_create_field_hidden(request.user)

        interest_list = Interest.object_normal.filter(tenant_id=request.user.tenant_current_id)
        if request.data.get('code', None) in interest_list.values_list("code", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.CODE_EXIST)
        if request.data.get('title', None) in interest_list.values_list("title", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.NAME_EXIST)

        obj = self.perform_create(serializer, extras=field_hidden)
        return ResponseController.created_201(data=self.get_serializer_detail(obj).data)


class InterestUpdateMixin(BaseUpdateMixin):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        interest_list = Interest.object_normal.filter(tenant_id=instance.tenant_id)
        if request.data.get('code', None) != instance.code and request.data.get('code', None) in interest_list.values_list("code", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.CODE_EXIST)
        if request.data.get('title', None) != instance.title and request.data.get('title', None) in interest_list.values_list("title", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.NAME_EXIST)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return ResponseController.success_200(data={'detail': HttpMsg.SUCCESSFULLY}, key_data='result')


class AccountTypeCreateMixin(BaseCreateMixin): # noqa
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_create(data=request.data)
        serializer.is_valid(raise_exception=True)
        field_hidden = self.setup_create_field_hidden(request.user)

        accounttype_list = AccountType.object_normal.filter(tenant_id=request.user.tenant_current_id)
        if request.data.get('code', None) in accounttype_list.values_list("code", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.CODE_EXIST)
        if request.data.get('title', None) in accounttype_list.values_list("title", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.NAME_EXIST)

        obj = self.perform_create(serializer, extras=field_hidden)
        return ResponseController.created_201(data=self.get_serializer_detail(obj).data)


class AccountTypeUpdateMixin(BaseUpdateMixin):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        accounttype_list = AccountType.object_normal.filter(tenant_id=instance.tenant_id)
        if request.data.get('code', None) != instance.code and request.data.get('code', None) in accounttype_list.values_list("code", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.CODE_EXIST)
        if request.data.get('title', None) != instance.title and request.data.get('title', None) in accounttype_list.values_list("title", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.NAME_EXIST)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return ResponseController.success_200(data={'detail': HttpMsg.SUCCESSFULLY}, key_data='result')


class IndustryCreateMixin(BaseCreateMixin):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_create(data=request.data)
        serializer.is_valid(raise_exception=True)
        field_hidden = self.setup_create_field_hidden(request.user)

        industry_list = Industry.object_normal.filter(tenant_id=request.user.tenant_current_id)
        if request.data.get('code', None) in industry_list.values_list("code", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.CODE_EXIST)
        if request.data.get('title', None) in industry_list.values_list("title", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.NAME_EXIST)

        obj = self.perform_create(serializer, extras=field_hidden)
        return ResponseController.created_201(data=self.get_serializer_detail(obj).data)


class IndustryUpdateMixin(BaseUpdateMixin):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        industry_list = Industry.object_normal.filter(tenant_id=instance.tenant_id)
        if request.data.get('code', None) != instance.code and request.data.get('code', None) in industry_list.values_list("code", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.CODE_EXIST)
        if request.data.get('title', None) != instance.title and request.data.get('title', None) in industry_list.values_list("title", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.NAME_EXIST)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return ResponseController.success_200(data={'detail': HttpMsg.SUCCESSFULLY}, key_data='result')


class ContactCreateMixin(BaseCreateMixin):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_create(data=request.data)
        serializer.is_valid(raise_exception=True)
        field_hidden = self.setup_create_field_hidden(request.user)

        account_list = Contact.object_normal.filter(tenant_id=request.user.tenant_current_id)
        email = request.data.get('email', None)
        mobile = request.data.get('mobile', None)
        if email and email in account_list.values_list("email", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.EMAIL_EXIST)
        if mobile and mobile in account_list.values_list("mobile", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.MOBILE_EXIST)

        obj = self.perform_create(serializer, extras=field_hidden)
        return ResponseController.created_201(data=self.get_serializer_detail(obj).data)


class ContactUpdateMixin(BaseUpdateMixin):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        account_list = Contact.object_normal.filter(tenant_id=instance.tenant_id)
        email = request.data.get('email', None)
        mobile = request.data.get('mobile', None)
        if email and email != instance.email and email in account_list.values_list("email", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.EMAIL_EXIST)
        if mobile and mobile != instance.mobile and mobile in account_list.values_list("mobile", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.MOBILE_EXIST)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return ResponseController.success_200(data={'detail': HttpMsg.SUCCESSFULLY}, key_data='result')


class AccountCreateMixin(BaseCreateMixin):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_create(data=request.data)
        serializer.is_valid(raise_exception=True)
        field_hidden = self.setup_create_field_hidden(request.user)

        account_list = Account.object_normal.filter(tenant_id=request.user.tenant_current_id)
        if request.data.get('code', None) in account_list.values_list("code", flat=True):
            return ResponseController.bad_request_400(msg=AccountsMsg.CODE_EXIST)

        obj = self.perform_create(serializer, extras=field_hidden)
        return ResponseController.created_201(data=self.get_serializer_detail(obj).data)

from django.db import transaction

from apps.shared import BaseDestroyMixin, ResponseController, LeaveMsg


class LeaveDestroyMixin(BaseDestroyMixin):
    def destroy(self, request, *args, **kwargs):
        if hasattr(request, "user"):
            instance = self.filter_queryset(
                self.get_queryset().filter(**kwargs)
            ).first()
            if not instance.is_lt_system and instance.is_lt_edit:
                state = self.perform_destroy(instance, True)
                if state:
                    return ResponseController.no_content_204()
                return ResponseController.internal_server_error_500()
            return ResponseController.bad_request_400(LeaveMsg.ERROR_DELETE_LEAVE_TYPE)
        return ResponseController.unauthorized_401()

    @classmethod
    def perform_destroy(cls, instance, purge=False):
        try:
            with transaction.atomic():
                if purge:
                    instance.delete()
                    return True
                instance.is_delete = True
                instance.save()
            return True
        except Exception as err:
            print(err)
        return False

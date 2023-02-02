from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import models
from crum import get_current_user


def print_model_hit_db(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if settings.MODEL_HIT_DB_DEBUG and settings.SQL_HIT_DB_DEBUG:
            print(
                f"[{str(self)}] : {str(result.query) if hasattr(result, 'query') else '[SHOW ERRORS]'}"
            )
        elif settings.MODEL_HIT_DB_DEBUG:
            print('[MODEL CALL HIT DB]: ', str(self))
        elif settings.SQL_HIT_DB_DEBUG:
            print('SQL: ', str(result.query) if hasattr(result, 'query') else '[SHOW ERRORS]')
        return result

    return wrapper


class NormalManager(models.Manager):
    @print_model_hit_db
    def get_queryset(self):
        return super().get_queryset()


class GlobalManager(models.Manager):
    @print_model_hit_db
    def get_queryset(self):
        user_obj = get_current_user()
        if user_obj and not isinstance(user_obj, AnonymousUser):
            return super().get_queryset().filter(mode=0, tenant_id=user_obj.tenant_current_id)
        return super().get_queryset().filter(mode=0)


class PrivateManager(models.Manager):
    @print_model_hit_db
    def get_queryset(self):
        user_obj = get_current_user()
        if user_obj and not isinstance(user_obj, AnonymousUser):
            return super().get_queryset().filter(mode=1, tenant_id=user_obj.tenant_current_id)
        return super().get_queryset().filter(mode=1)


class TeamManager(models.Manager):
    @print_model_hit_db
    def get_queryset(self):
        user_obj = get_current_user()
        if user_obj and not isinstance(user_obj, AnonymousUser):
            return super().get_queryset().filter(mode=2, tenant_id=user_obj.tenant_current_id)
        return super().get_queryset().filter(mode=2)

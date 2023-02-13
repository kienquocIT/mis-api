from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import models, connection
from crum import get_current_user

counter_queries = 0


def print_model_hit_db(func):
    def cut_from(sql):
        arr = []
        arr_cut = sql.split("FROM")
        if len(arr_cut) > 1:
            for idx in range(1, len(arr_cut)):
                arr.append(
                    arr_cut[idx].split('WHERE')[0]
                )
        return arr

    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if settings.MODEL_HIT_DB_DEBUG or settings.SQL_HIT_DB_DEBUG:
            global counter_queries
            if settings.MODEL_HIT_DB_DEBUG and settings.SQL_HIT_DB_DEBUG:
                new_counter_queries = len(connection.queries)
                for idx in range(counter_queries, new_counter_queries):
                    time_tmp = connection.queries[idx]["time"]
                    sql_tmp = connection.queries[idx]["sql"]
                    model_tmp = cut_from(sql_tmp)

                    try:
                        print(
                            u'[{time_tmp}] {model_tmp} {sql_tmp}'.format(
                                time_tmp=time_tmp,
                                model_tmp="<FROM>" + " | ".join(model_tmp),
                                sql_tmp="<SQL> " + sql_tmp
                            ).encode("ascii", "ignore").decode()
                        )
                    except Exception as err:
                        print(err)
                counter_queries = new_counter_queries
            elif settings.MODEL_HIT_DB_DEBUG:
                new_counter_queries = len(connection.queries)
                for idx in range(counter_queries, new_counter_queries):
                    time_tmp = connection.queries[idx]["time"]
                    sql_tmp = connection.queries[idx]["sql"]
                    model_tmp = cut_from(sql_tmp)
                    print(f'[{time_tmp}] {("  >>> " + " | ".join(model_tmp)) if model_tmp else " "}')
                counter_queries = new_counter_queries
            elif settings.SQL_HIT_DB_DEBUG:
                new_counter_queries = len(connection.queries)
                for idx in range(counter_queries, new_counter_queries):
                    time_tmp = connection.queries[idx]["time"]
                    sql_tmp = connection.queries[idx]["sql"]
                    print(f'[{time_tmp}] {">>SQL>> " + sql_tmp}')
                counter_queries = new_counter_queries
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

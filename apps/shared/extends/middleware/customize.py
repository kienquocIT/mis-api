from django.conf import settings
from django.db import connection

counter_queries = 0  # pylint: disable=C0103


class CustomizeMiddleware:
    @staticmethod
    def cut_from(sql):
        arr = []
        arr_cut = sql.split("FROM")
        if len(arr_cut) > 1:
            for idx in range(1, len(arr_cut)):
                arr.append(
                    arr_cut[idx].split('WHERE')[0]
                )
        return arr

    @staticmethod
    def to_microseconds(sec, to_str=True):
        result = float(sec) * 1000
        if to_str is True:
            return str(result)
        return result

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        # show query db hit
        if settings.DEBUG_HIT_DB:
            global counter_queries  # pylint: disable=W0603
            new_counter_queries = len(connection.queries)
            for idx in range(counter_queries, new_counter_queries):
                time_tmp = connection.queries[idx]["time"]
                sql_tmp = connection.queries[idx]["sql"]
                model_tmp = self.cut_from(sql_tmp)
                msg = f'[{self.to_microseconds(time_tmp)} ms] {" | ".join(model_tmp)} {">>> " + sql_tmp}'
                try:
                    print(msg)
                except Exception as err:
                    print(err)
                    print(str(msg.encode('utf-8')))
            counter_queries = new_counter_queries

        return response

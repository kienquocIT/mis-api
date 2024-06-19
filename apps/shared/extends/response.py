from django.conf import settings
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response


class ConvertErrors:
    KEY_NOT_CONVERT_EXCEPTIONS = ['id_list']
    KEY_NOT_EXCEPTIONS = ['result', 'status', 'results', 'error_data']

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, data: dict):
        if settings.DEBUG_PERMIT:
            for key, value in data.items():
                if key in self._result:
                    print(f'[ConvertErrors][result.setter] Replace value of key: {key}, {self._result[key]} -> {value}')
        self._result.update(data)

    def __init__(self, opts: dict = None):
        if not opts:
            opts = {}
        self._result = {}
        self.config = {
            'LIST_CONVERT_TO': 'STR',  # 'FIRST', 'LIST_STR', 'STR'
            'LIST_STR_JOIN_CHAR': '. ',
            'DATA_ALWAYS_LIST': False,  # "a" => ["a"]
            **opts
        }

    def handle_list(self, key, value: list):
        if isinstance(value, list) and len(value) > 0:
            if isinstance(value[0], str or ErrorDetail):
                if self.config['LIST_CONVERT_TO'] == 'FIRST':
                    self.result = {key: str(value[0])}
                elif self.config['LIST_CONVERT_TO'] == 'LIST_STR':
                    self.result = {key: [str(item) for item in value]}
                elif self.config['LIST_CONVERT_TO'] == 'STR':
                    self.result = {key: self.config['LIST_STR_JOIN_CHAR'].join([str(item) for item in value])}
            elif isinstance(value[0], dict):
                for item in value:
                    if isinstance(item, dict):
                        for key_dict, value_dict in item.items():
                            self.handle_dict(key=key_dict, value=value_dict)
            else:
                self.result = {key: self.config['LIST_STR_JOIN_CHAR'].join([str(item) for item in value])}
        return True

    def handle_dict(self, key, value):
        if key in self.KEY_NOT_CONVERT_EXCEPTIONS:
            self.result = {key: value}
        elif key not in self.KEY_NOT_EXCEPTIONS:
            if isinstance(value, str or ErrorDetail):
                self.result = {key: value}
            elif isinstance(value, list):
                self.handle_list(key=key, value=value)
            elif isinstance(value, dict):
                for key_dict, value_dict in value.items():
                    self.handle_dict(key=key_dict, value=value_dict)
        return True

    def convert(self, errors: dict, status_code: str or int):
        for key, value in errors.items():
            self.handle_dict(key=key, value=value)
        if status_code:
            return {'status': status_code, "errors": self.result}
        return {"errors": self.result}


def cus_response(data, status, is_errors=False):
    if is_errors:
        data = ConvertErrors().convert(data, status_code=status)
    else:
        data.update({"status": status if status else status.HTTP_200_OK})
        if "results" in data:
            result = data["results"]
            del data["results"]
            data.update({"result": result})
    return Response(data, status=status, content_type="application/json")

#
# KEY_NOT_CONVERT_EXCEPTIONS = ['id_list']
#
# KEY_NOT_EXCEPTIONS = ['result', 'status', 'results', 'error_data']
#
#
# def convert_errors(dict_error, status_code=None, opts=None):  # pylint: disable=R0912
#     if opts is None:
#         opts = {}
#     opts = {
#         'LIST_CONVERT_TO': 'STR',  # 'FIRST', 'LIST_STR', 'STR'
#         'LIST_STR_JOIN_CHAR': '. ',
#         'DATA_ALWAYS_LIST': False,  # "a" => ["a"]
#         **opts
#     }
#
#     errors = {}
#     for field, value in dict_error.items():  # pylint: disable=R1702
#         if value:
#             if field in KEY_NOT_CONVERT_EXCEPTIONS:
#                 errors.update({field: value})
#             elif field not in KEY_NOT_EXCEPTIONS:
#                 if isinstance(value, str or ErrorDetail):
#                     errors.update({field: str(value)})
#                 elif isinstance(value, list):
#                     if opts['LIST_CONVERT_TO'] == 'FIRST':
#                         errors.update({field: str(value[0])})
#                     elif opts['LIST_CONVERT_TO'] == 'LIST_STR':
#                         errors.update({field: [str(item) for item in value]})
#                     elif opts['LIST_CONVERT_TO'] == 'STR':
#                         errors.update({field: opts['LIST_STR_JOIN_CHAR'].join([str(item) for item in value])})
#                 elif isinstance(value, dict):
#                     for key_dict, value_dict in value.items():
#                         if isinstance(value, str or ErrorDetail):
#                             errors.update({field: str(value)})
#                         elif isinstance(value, list):
#                             if opts['LIST_CONVERT_TO'] == 'FIRST':
#                                 errors.update({field: str(value[0])})
#                             elif opts['LIST_CONVERT_TO'] == 'LIST_STR':
#                                 errors.update({field: [str(item) for item in value]})
#                             elif opts['LIST_CONVERT_TO'] == 'STR':
#                                 errors.update({field: ", ".join([str(item) for item in value])})
#                         else:
#                             errors.update({key_dict: str(value_dict)})
#     if status_code:
#         return {"status": status_code, "errors": errors}
#     return {"errors": errors}
#
#
# def convert_errors1(dict_error, status_code=None):  # pylint: disable=R0912
#     data = {"errors": {}}
#     for field, value in dict_error.items():  # pylint: disable=R1702
#         if field in KEY_NOT_CONVERT_EXCEPTIONS:
#             data["errors"].update({field: value})
#         elif field not in KEY_NOT_EXCEPTIONS:
#             if isinstance(value, str):
#                 data["errors"].update({field: value})
#             elif isinstance(value, list):
#                 if isinstance(value[0], dict):
#                     for err in value:
#                         if isinstance(err, dict):
#                             tmp = {}
#                             convert_dict_errors(err, tmp)
#                             data["errors"].update(tmp)
#                 else:
#                     data["errors"].update({field: value[0]})
#             elif isinstance(value, dict):
#                 tmp = {}
#                 convert_dict_errors(value, tmp)
#                 data["errors"].update(tmp)
#             else:
#                 data["errors"].update({field: value})
#         else:
#             data.update({field: value})
#     if status_code:
#         data.update({"status": status_code})
#     return data
#
#
# def convert_dict_errors(errors, tmp):
#     for key, value in errors.items():
#         if isinstance(value, str):
#             tmp.update({key: value})
#         elif isinstance(value, list):
#             convert_list_error(value, key, tmp)
#         elif isinstance(value, dict):
#             convert_dict_errors(value, tmp)
#
#
# def convert_list_error(error, key, tmp):
#     for err in error:
#         if isinstance(err, str):
#             tmp.update({key: err})
#         elif isinstance(err, list):
#             tmp.update(convert_list_error(err, key, tmp))
#         elif isinstance(err, dict):
#             convert_dict_errors(err, tmp)
#

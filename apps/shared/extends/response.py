KEY_NOT_CONVERT_EXCEPTIONS = ['id_list']

KEY_NOT_EXCEPTIONS = ['result', 'status', 'results', 'error_data']


def convert_errors(dict_error, status_code=None):
    data = {"errors": {}}
    for field, value in dict_error.items():
        if field in KEY_NOT_CONVERT_EXCEPTIONS:
            data["errors"].update({field: value})
        elif field not in KEY_NOT_EXCEPTIONS:
            if isinstance(value, str):
                data["errors"].update({field: value})
            elif isinstance(value, list):
                if isinstance(value[0], dict):
                    for err in value:
                        if isinstance(err, dict):
                            tmp = {}
                            convert_dict_errors(err, tmp)
                            data["errors"].update(tmp)
                else:
                    data["errors"].update({field: value[0]})
            elif isinstance(value, dict):
                tmp = {}
                convert_dict_errors(value, tmp)
                data["errors"].update(tmp)
            else:
                data["errors"].update({field: value})
        else:
            data.update({field: value})
    if status_code:
        data.update({"status": status_code})
    return data


def convert_dict_errors(errors, tmp):
    for key, value in errors.items():
        if isinstance(value, str):
            tmp.update({key: value})
        elif isinstance(value, list):
            convert_list_error(value, key, tmp)
        elif isinstance(value, dict):
            convert_dict_errors(value, tmp)


def convert_list_error(error, key, tmp):
    for err in error:
        if isinstance(err, str):
            tmp.update({key: err})
        elif isinstance(err, list):
            tmp.update(convert_list_error(err, key, tmp))
        elif isinstance(err, dict):
            convert_dict_errors(err, tmp)

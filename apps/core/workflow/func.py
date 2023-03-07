

# functions for association


def check_type_number(condition_data):
    data_on_doc = 0
    value = float(condition_data['value'])
    if condition_data['operator'] == "=":
        if data_on_doc == value:
            return True
        else:
            return False
    elif condition_data['operator'] == "!=":
        if data_on_doc != value:
            return True
        else:
            return False
    elif condition_data['operator'] == ">":
        if data_on_doc > value:
            return True
        else:
            return False
    elif condition_data['operator'] == "<":
        if data_on_doc < value:
            return True
        else:
            return False
    elif condition_data['operator'] == ">=":
        if data_on_doc >= value:
            return True
        else:
            return False
    elif condition_data['operator'] == "<=":
        if data_on_doc <= value:
            return True
        else:
            return False
    elif condition_data['operator'] == "is empty":
        if data_on_doc is None:
            return True
        else:
            return False
    elif condition_data['operator'] == "is not empty":
        if data_on_doc is not None:
            return True
        else:
            return False
    return False


def check_type_text(condition_data):
    data_on_doc = ""
    value = str(condition_data['value'])
    if condition_data['operator'] == "is":
        if data_on_doc == value:
            return True
        else:
            return False
    elif condition_data['operator'] == "is not":
        if data_on_doc != value:
            return True
        else:
            return False
    elif condition_data['operator'] == "contains":
        if value in data_on_doc:
            return True
        else:
            return False
    elif condition_data['operator'] == "does not contains":
        if value not in data_on_doc:
            return True
        else:
            return False
    return False


def check_type_boolean(condition_data):
    data_on_doc = False
    value = condition_data['value']
    if condition_data['operator'] == "is":
        if data_on_doc is value:
            return True
        else:
            return False
    elif condition_data['operator'] == "is":
        if data_on_doc is not value:
            return True
        else:
            return False
    return False


# check condition return True or False
def get_true_false_result(condition_data):
    result = False
    if all(key in condition_data for key in ['type', 'operator', 'property', 'value']):
        # number type
        if condition_data['type'] == "number":
            result = check_type_number(condition_data)
        # text type
        elif condition_data['type'] == "text":
            result = check_type_text(condition_data)
        # boolean type
        elif condition_data['type'] == "boolean":
            result = check_type_boolean(condition_data)

    return result


# check condition of association (node in - node out)
def check_condition(condition_list):
    result = []
    for idx in range(0, len(condition_list)):
        if idx % 2 == 0:
            if isinstance(condition_list[idx], dict):
                result.append(get_true_false_result(condition_list[idx]))
            elif isinstance(condition_list[idx], list):
                result.append(check_condition(
                    condition_list=condition_list[idx],
                ))
        else:
            result.append(condition_list[idx].lower())

    return result


def convert_condition_result_to_string(condition_list, result):
    data_str = ""
    if condition_list and not result:
        result = check_condition(
            condition_list=condition_list
        )
    if result and isinstance(result, list):
        for item in result:
            if not isinstance(item, list):
                data_str += (str(item) + " ")
            else:
                data_str += ("(" + convert_condition_result_to_string(
                    condition_list=None,
                    result=item
                ) + ") ")
    return data_str


def eval_result(data):
    return eval(data)

from rest_framework.response import Response
from .extends import convert_errors


def cus_response(data, status=None, is_errors=False):
    if is_errors:
        data = convert_errors(data, status_code=status)
    else:
        data.update({"status": status if status else status.HTTP_200_OK})
        if "results" in data:
            result = data["results"]
            del data["results"]
            data.update({"result": result})
    return Response(data, status=status, content_type="application/json")

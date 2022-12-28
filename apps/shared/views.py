from apps.shared import ResponseController


def view_handler400(request, *args, **kwargs):
    return ResponseController.bad_request_400()


def view_handler401(request, *args, **kwargs):
    return ResponseController.unauthorized_401()


def view_handler403(request, *args, **kwargs):
    return ResponseController.forbidden_403()


def view_handler404(request, *args, **kwargs):
    return ResponseController.notfound_404()


def view_handler500(request, *args, **kwargs):
    return ResponseController.internal_server_error_500()

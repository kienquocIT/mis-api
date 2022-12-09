from django.shortcuts import render


def view_handler404(request, *args, **argv):
    response = render(request, 'basic/404.html', {})
    response.status_code = 404
    return response


def view_handler500(request, *args, **argv):
    response = render(request, 'basic/500.html', {})
    response.status_code = 500
    return response

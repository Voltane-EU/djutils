from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.core.exceptions import ValidationError
from django.contrib.staticfiles.views import serve

from .exceptions import Error
from . import app_settings


def redirect(to):
    """ A simple static redirect for use in the urlpatterns preserving GET parameters """
    def redir(request):
        return HttpResponseRedirect(redirect_to=to+('?' + request.GET.urlencode(safe='/') if request.GET else ''))
    return redir

def static_file(file):
    def serve_static(request):
        return serve(request, file)
    return serve_static

def h404(request):
    """ Raises a Http404. A `HttpResponseNotFound` could also be used instead """
    raise Http404('')

def get_ip_address(request):
    """
    Get the remote address of the client.
    Using the `X-Forwarded-For` Header field if set or the regular `REMOTE_ADDR`.
    """
    return request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')

def error_respond_json(error, status_code):
    response = {
        'message': None,
        'code': None,
    }

    if app_settings.HTTP_ERROR_INCLUDE_CLASS_NAME:
        response['type'] = error.__class__.__name__

    if isinstance(error, Error):
        response['message'] = _(error.message) if error.message else None
        response['code'] = error.code
        status_code = error.status_code or status_code

    elif isinstance(error, ValidationError):
        response['message'] = _(error.message) if error.message else None
        response['code'] = error.code

    else:
        response['message'] = _(str(error.args[0])) if error.args else None
        response['code'] = error.args[1] if len(error.args) > 1 else None
        status_code = 400 if isinstance(error, AssertionError) else status_code

    return JsonResponse(
        {
            "error": response
        } if app_settings.HTTP_ERROR_WRAP_IN_ERROR_DICT else response,
        status=status_code,
    )

def exceptions_to_http(*exceptions, status_code=403):
    """
    Returns occurring exceptions of the defined type(s) as `JsonResponse`.
    A `AssertionError` will resolve with HTTP Status code 400
    """
    def wrap_function(f):
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exceptions as error:
                return error_respond_json(error, status_code)
        return wrapper
    return wrap_function

def respond_json(f):
    """ Converts the returned data into a `JsonResponse` """
    def wrapper(*args, **kwargs):
        ret = f(*args, **kwargs)
        if not isinstance(ret, HttpResponse):
            ret = JsonResponse(ret, safe=False)
        return ret
    return wrapper

from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.contrib.staticfiles.views import serve

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

def exceptions_to_http(*exceptions):
    """
    Returns occurring exceptions of the defined type(s) as `JsonResponse`.
    A `AssertionError` will resolve with HTTP Status code 400
    """
    def wrap_function(f):
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exceptions as error:
                return JsonResponse({"message": _(error.message), "code": error.code}, status=error.status_code or 403)
            except AssertionError as error:
                return JsonResponse({"message": _(error.args[0]), "code": error.args[1] if len(error.args) > 1 else None}, status=400)
        return wrapper
    return wrap_function

def respond_json(f):
    """ Converts the returned data into a `JsonResponse` """
    def wrapper(*args, **kwargs):
        return JsonResponse(f(*args, **kwargs))
    return wrapper

from django.forms import ValidationError

class Error(Exception):
    """
    A base Error class which can be used along with djutils.http.exceptions_to_http decorator to provide an technical
    error code which can be passed to the client and an appropriate http status code.
    """

    code = None
    status_code = None

    def __init__(self, message, code=None, status_code=None, **kw):
        if isinstance(self, ValidationError):
            super().__init__(message=message, code=code, **kw)
        else:
            super().__init__(**kw)
            self.message = message
            self.code = code or self.code
            self.status_code = status_code or self.status_code

    def __str__(self):
        return "%s (%s/%s)" % (self.message, self.code, self.status_code)

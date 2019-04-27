from django.forms import ValidationError

class Error(Exception):
    def __init__(self, message, code=None, status_code=None, **kw):
        if isinstance(self, ValidationError):
            super().__init__(message=message, code=code, **kw)
        else:
            super().__init__(**kw)
            self.message = message
            self.code = code
            self.status_code = status_code

    def __str__(self):
        return "%s (%s/%s)" % (self.message, self.code, self.status_code)

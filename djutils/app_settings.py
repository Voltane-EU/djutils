from django.conf import settings


HTTP_ERROR_INCLUDE_CLASS_NAME = getattr(settings, "HTTP_ERROR_INCLUDE_CLASS_NAME", True)
HTTP_ERROR_WRAP_IN_ERROR_DICT = getattr(settings, "HTTP_ERROR_WRAP_IN_ERROR_DICT", True)

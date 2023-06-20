import warnings
import secrets
import string
import hmac
import hashlib

ASCII_NOT_CONFUSABLE = "ABCEFGHJKLMNPQRSTUWXYZ123456789"

def random_string_generator(size=16, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
    """
    DEPRECATED: Use `get_random_string` from `django.utils.crypto` instead
    Generate a secure random string with length `size` out of the defined charset `chars`.
    """
    warnings.warn("Use `get_random_string` from `django.utils.crypto` instead", category=DeprecationWarning)
    choice = secrets.SystemRandom().choice
    return ''.join(choice(chars) for _ in range(size))

def sha512_hash(key, msg):
    """ SHA512 hexdigest of `msg` salted with `key`. UTF-8 Encoded. """
    return hmac.new(
        key=key.encode('utf-8') if isinstance(key, str) else key,
        msg=msg.encode('utf-8') if isinstance(msg, str) else msg,
        digestmod=hashlib.sha512
    ).hexdigest()

def sha256_hash(key, msg):
    """ SHA256 hexdigest of `msg` salted with `key`. UTF-8 Encoded. """
    return hmac.new(
        key=key.encode('utf-8') if isinstance(key, str) else key,
        msg=msg.encode('utf-8') if isinstance(msg, str) else msg,
        digestmod=hashlib.sha256
    ).hexdigest()

from random import choice
import string
import hmac
import hashlib

ASCII_NOT_CONFUSABLE = "ABCEFGHJKLMNPQRSTUWXYZ123456789"

def random_string_generator(size=16, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
    """ Generate a string with length `size` out of the defined charset `chars` """
    return ''.join(choice(chars) for _ in range(size))

def sha512_hash(key, msg):
    """ SHA512 hexdigest of `msg` salted with `key`. UTF-8 Encoded. """
    return hmac.new(key=key.encode('utf-8'), msg=msg.encode('utf-8'), digestmod=hashlib.sha512).hexdigest()

def sha256_hash(key, msg):
    """ SHA256 hexdigest of `msg` salted with `key`. UTF-8 Encoded. """
    return hmac.new(key=key.encode('utf-8'), msg=msg.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()

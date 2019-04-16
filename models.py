from datetime import datetime
import uuid
from django.db import models

def model_to_dict(instance, fields: list = [], exclude: list = []):
    if not fields:
        fields = [field.name for field in instance._meta.get_fields()]
    data = {}
    for field in fields:
        if field in exclude:
            continue

        value = getattr(instance, field)
        if isinstance(value, datetime):
            value = value.timestamp()
        elif isinstance(value, uuid.UUID):
            value = str(value)
        elif isinstance(value, models.Manager):
            value = [model_to_dict(related) for related in value.all()]

        data[field] = value

    return data

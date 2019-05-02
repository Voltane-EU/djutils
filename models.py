import uuid
import hashlib
from datetime import datetime
from io import BytesIO
from PIL import Image
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.db.models.fields.files import FieldFile

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
        elif isinstance(value, FieldFile):
            value = value.url
        elif isinstance(value, models.Model):
            try:
                value = getattr(value, "values")()
            except AttributeError:
                pass

        data[field] = value

    return data

class CroppedImageStorage(FileSystemStorage):
    def __init__(self, *args, resize_to=(256, 256), resample=Image.BICUBIC, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize_to = resize_to
        self.resample = resample

    def _save(self, name, content):
        file = BytesIO()
        content.image = self.process_picture(content.file)
        content.image.save(file, format='png')
        name = hashlib.sha256(file.read()).hexdigest()
        content.file.seek(0)

        content.file = file

        ret = super()._save(name+".png", content)
        return ret[0:-4]

    def process_picture(self, file):
        """ Process the incomming file, returns Image object """
        image = Image.open(file)
        # Crop image to a square
        box = (
            (image.size[0] - image.size[1]) / 2,
            0,
            image.size[0] - (image.size[0] - image.size[1]) / 2,
            image.size[1],
        )
        if image.size[0] < image.size[1]:
            box = (
                0,
                (image.size[1] - image.size[0]) / 2,
                image.size[0],
                image.size[1] - (image.size[1] - image.size[0]) / 2,
            )
        image = image.resize(self.resize_to, resample=self.resample, box=box)
        return image

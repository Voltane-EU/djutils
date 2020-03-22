import os.path
import uuid
import hashlib
import subprocess
from datetime import datetime
from io import BytesIO
from PIL import Image
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.db.models.fields.files import FieldFile
from django.utils.deconstruct import deconstructible

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


@deconstructible
class MozJPEGPostprocessor:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, file):
        return self.process(file, *self.args, **self.kwargs)

    @classmethod
    def process(cls, file: BytesIO, *args, timeout=10):
        mozjpeg = subprocess.Popen(['mozjpeg', *args], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        try:
            stdout, stderr = mozjpeg.communicate(file.getvalue(), timeout=timeout)

        except subprocess.TimeoutExpired:
            mozjpeg.kill()
            raise TimeoutError

        if stderr:
            raise IOError(stderr)

        return BytesIO(stdout)


class AbstractImageStorage(FileSystemStorage):
    def __init__(self, *args, resize_to: tuple = None, resample=Image.BICUBIC, output_format='png', just_hash=False, hash_algo=hashlib.sha256, post_process=None, **kwargs):
        """
        Image Storage.
        Resamples an Image before storing as File.

        Params:
        resize_to: tuple, (width, height)
        resample: PIL.Image resampling metho
        output_format: Image Format (png, jpg, gif, etc.)
        just_hash: Return only the file hash (file basename without extension) instead of the full storage location path
        post_process: callable for additional processing after self.process_picture(); intended to be used for compression, passes the file (BytesIO) as argument
        """
        super().__init__(*args, **kwargs)
        self.resize_to = resize_to
        self.resample = resample
        self.format = output_format
        self.just_hash = just_hash
        self.hash_algo = hash_algo
        self.post_process = post_process

    def process_picture(self, file):
        raise NotImplementedError

    def _save(self, name, content):
        file = BytesIO()
        content.image = self.process_picture(content.file)
        content.image.save(file, format=self.format)

        if self.post_process:
            file = self.post_process(file)

        hash_name = self.hash_algo(file.read()).hexdigest()
        content.file.seek(0)
        content.file = file

        name = os.path.join(os.path.dirname(name), "%s.%s" % (hash_name, self.format))
        ret = super()._save(name, content)
        if self.just_hash:
            return os.path.basename(ret)[:-(len(self.format) + 1)]

        return ret


class CroppedImageStorage(AbstractImageStorage):
    """
    Image, resized and cropped to a square
    """

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


class ThumbnailImageStorage(AbstractImageStorage):
    """
    Image, resized if larger than given resize_to, aspect ratio is being kept (uses PIL.Image.thumbnail())
    """

    def process_picture(self, file):
        """ Process the incomming file, returns Image object """
        image = Image.open(file)
        image.thumbnail(self.resize_to, resample=self.resample)

        return image

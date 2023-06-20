import os.path
from typing import Any
import uuid
import hashlib
import subprocess
from datetime import datetime
from io import BytesIO
from PIL import Image
from django.db import models
from django.db.models import Func, Value, CharField, JSONField
from django.db.transaction import atomic
from django.db.models.fields.files import FieldFile
from django.core.files.storage import FileSystemStorage
from django.utils.crypto import get_random_string
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
    def __init__(self, *args, resize_to: tuple = None, resample=Image.BICUBIC, output_format='png', just_hash=False, hash_algo=hashlib.sha256, post_process=None, should_fix_colorspace=True, **kwargs):
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
        self.should_fix_colorspace = should_fix_colorspace

    def process_picture(self, file):
        raise NotImplementedError

    @classmethod
    def _fix_colorspace(cls, image, colorspace, output_format):
        """
        From https://github.com/jazzband/sorl-thumbnail/issues/564
        """
        if colorspace == 'RGB':
            # Pillow JPEG doesn't allow RGBA anymore. It was converted to RGB before.
            if image.mode == 'RGBA' and output_format != 'JPEG':
                return image  # RGBA is just RGB + Alpha

            if image.mode == 'LA' or (image.mode == 'P' and 'transparency' in image.info):
                if output_format == 'JPEG':
                    newimage = Image.new('RGB', image.size, '#ffffff')
                    mask = image.convert('RGBA').split()[-1]
                    newimage.paste(image.convert('RGBA'), (0, 0), mask)

                else:
                    newimage = image.convert('RGBA')
                    transparency = image.info.get('transparency')
                    if transparency is not None:
                        mask = image.convert('RGBA').split()[-1]
                        newimage.putalpha(mask)

                return newimage

            return image.convert('RGB')

        if colorspace == 'GRAY':
            return image.convert('L')

        return image

    def _save(self, name, content):
        file = BytesIO()
        content.image = self.process_picture(content.file)
        if self.should_fix_colorspace:
            content.image = self._fix_colorspace(content.image, "RGB", self.format.upper())

        content.image.save(file, format=self.format)

        if self.post_process:
            file = self.post_process(file)

        file.seek(0)

        if self.hash_algo:
            hash_name = self.hash_algo(file.read()).hexdigest()
            file.seek(0)
            name = os.path.join(os.path.dirname(name), "%s.%s" % (hash_name, self.format))

        content.file.seek(0)
        content.file = file

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


# Original code from "olympus", Copyright (C) 2021  LaVita GmbH / Digital Solutions, LGPLv2.1
# https://github.com/LaVita-GmbH/olympus


class ModelAtomicSave(models.Model):
    @atomic
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True


class JSONArrayElements(Func):
    function = 'jsonb_array_elements'
    arity = 1


class JSONExtractPath(Func):
    function = 'jsonb_extract_path'
    arity = 2

    def __init__(self, jsonb, path):
        super().__init__(jsonb, Value(path, output_field=CharField()), output_field=JSONField())


class JSONExtractPathText(Func):
    function = 'jsonb_extract_path_text'
    arity = 2

    def __init__(self, jsonb, path):
        super().__init__(jsonb, Value(path, output_field=CharField()), output_field=CharField())


class RandomIDField(models.CharField):
    description = "A primary key field based on random characters with a given length"

    def __init__(self, length: int, *args, **kwargs):
        self.length = length
        kwargs.setdefault('editable', False)
        kwargs.setdefault('primary_key', True)
        kwargs['max_length'] = self.length

        super().__init__(*args, **kwargs)

    def has_default(self):
        return True

    def get_default(self):
        return get_random_string(self.length)

    def deconstruct(self):
        name, path, args, keywords = super().deconstruct()

        keywords.update({
            'length': self.length,
            'primary_key': self.primary_key,
            'editable': self.editable,
        })

        return name, path, args, keywords

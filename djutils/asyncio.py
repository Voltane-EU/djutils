"""
Original code from "olympus", Copyright (C) 2021  LaVita GmbH / Digital Solutions, LGPLv2.1
https://github.com/LaVita-GmbH/olympus
"""

import os
from asyncio import get_event_loop
from async_tools import is_async  # noqa


class AllowAsyncUnsafe:
    def __init__(self):
        self._django_allow_async_unsafe_before = os.environ.get('DJANGO_ALLOW_ASYNC_UNSAFE')

    def __enter__(self):
        os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = '1'

    def __exit__(self, type, value, traceback):
        if self._django_allow_async_unsafe_before is None:
            del os.environ['DJANGO_ALLOW_ASYNC_UNSAFE']

        else:
            os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = self._django_allow_async_unsafe_before

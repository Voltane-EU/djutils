"""
Original code from "olympus", Copyright (C) 2021  LaVita GmbH / Digital Solutions, LGPLv2.1
https://github.com/LaVita-GmbH/olympus
"""

import logging
from contextvars import ContextVar, copy_context
from asyncio import Future
from inspect import CO_COROUTINE
from functools import wraps
from typing import Callable, Optional
from django.db import transaction
from async_tools import is_async


_logger = logging.getLogger(__name__)

PENDING_TRANSACTION_COMPLETE_OPERATIONS = {}
pending_transaction_complete_operations: ContextVar[dict] = ContextVar('pending_transaction_complete_operations')


def on_transaction_complete(awaitable: bool = False, callback: Optional[Callable] = None, error_callback: Optional[Callable] = None, deduplicate: Optional[Callable] = None):
    def wrapper(callable):
        @wraps(callable)
        def wrapped(*args, **kwargs):
            is_async_ = is_async()
            if is_async_ and not awaitable:
                raise AssertionError("Cannot call not awaitable from async context")

            elif awaitable and not is_async_:
                raise AssertionError("Cannot call awaitable from sync context")

            try:
                pending = pending_transaction_complete_operations.get()

            except LookupError:
                pending = PENDING_TRANSACTION_COMPLETE_OPERATIONS

            if deduplicate:
                dedup_id = deduplicate(*args, **kwargs)
                pending[dedup_id] = callable

            future = Future() if awaitable else None
            def call():
                if deduplicate:
                    if pending.get(dedup_id) != callable:
                        _logger.info("Deduplicated call with dedup_id %r to %s", dedup_id, callable)
                        if awaitable:
                            future.set_result(None)

                        elif callback:
                            callback(None)

                        return

                    try:
                        del pending[dedup_id]

                    except KeyError:
                        pass

                try:
                    result = callable(*args, **kwargs)
                    if awaitable:
                        future.set_result(result)

                    elif callback:
                        callback(result)

                except Exception as error:
                    if awaitable:
                        future.set_exception(error)

                    elif error_callback:
                        error_callback(error)

                    else:
                        _logger.exception(error, exc_info=True, stack_info=True)
                        raise

            context = copy_context()

            if not transaction.get_connection().in_atomic_block:
                context.run(call)

            else:
                transaction.on_commit(lambda: context.run(call))

            return future

        if awaitable:
            wrapped.__code__.co_flags &= CO_COROUTINE

        return wrapped

    return wrapper

'''
Original code from 'olympus', Copyright (C) 2021  LaVita GmbH / Digital Solutions, LGPLv2.1
https://github.com/LaVita-GmbH/olympus
'''

from typing import Optional
import hmac
from django.db import connection, ProgrammingError, InternalError
from django.db.transaction import atomic
from django.utils import timezone

try:
    from psycopg2.extensions import quote_ident
    from psycopg2.errorcodes import UNDEFINED_TABLE

    UndefinedTable = None

except ImportError:
    from psycopg.errors import UndefinedTable
    from psycopg.pq import Escaping

    UNDEFINED_TABLE = None
    quote_ident = lambda string, cursor: str(
        Escaping(cursor._pgconn).escape_identifier(bytes(string, 'utf-8')), 'utf-8'
    )


def number_generator(
    tenant_id: str,
    sequence_name: str,
    number_format: str,
    checksum_salt: Optional[str] = None,
    checksum_algorithm: Optional[str] = None,
    checksum_length: Optional[int] = None,
    checksum_format: Optional[str] = None,
) -> str:
    if not tenant_id:
        raise ValueError('Tenant-ID not given')

    sequence_name = f'{sequence_name}_{tenant_id}'
    val = None
    i = 0

    while not val and i < 2:
        try:
            with connection.cursor() as cursor:
                with atomic():
                    cursor.execute('SELECT nextval(%s);', (quote_ident(sequence_name, cursor.cursor),))
                    val = cursor.fetchone()
                    break

        except (ProgrammingError, InternalError) as error:
            if (UNDEFINED_TABLE and error.__cause__.pgcode != UNDEFINED_TABLE) or (
                UndefinedTable and not isinstance(error.__cause__, UndefinedTable)
            ):
                raise

            i += 1
            with connection.cursor() as cursor:
                with atomic():
                    cursor.execute(
                        'CREATE SEQUENCE IF NOT EXISTS %s START 1;' % quote_ident(sequence_name, cursor.cursor)
                    )

    if not val:
        raise ValueError('cannot_obtain_next_number')

    nextnumber = int(val[0])
    now = timezone.now()
    number = number_format % {
        'year': now.year,
        'month': now.month,
        'number': nextnumber,
    }

    if checksum_length and checksum_length > 0:
        checksum_value = hmac.new(checksum_salt, bytes(number, 'utf-8'), digestmod=checksum_algorithm)
        checksum_int = int(checksum_value.hexdigest(), 16)
        checksum_number = checksum_int % 10**checksum_length
        checksum = '%0*d' % (checksum_length, checksum_number)
        number = checksum_format % {
            'number': number,
            'checksum': checksum,
        }

    return number

from django_cockroachdb.base import DatabaseWrapper as CockroachDatabaseWrapper
from ..postgresql.base import DatabaseWrapper as PGSQLDatabaseWrapper


class DatabaseWrapper(PGSQLDatabaseWrapper, CockroachDatabaseWrapper):
    pass

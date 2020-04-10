from django.db.models import Func
from django.contrib.postgres.operations import CreateExtension


class Levenshtein(Func):
    """ For use of the levenshtein algorithm with a PostgreSQL Database """
    template = "%(function)s(%(expressions)s, '%(search_term)s')"
    function = "levenshtein"

    def __init__(self, expression, search_term, **extras):
        super().__init__(
            expression,
            search_term=search_term,
            **extras
        )


class FuzzystrExtension(CreateExtension):
    def __init__(self):
        self.name = 'fuzzystrmatch'

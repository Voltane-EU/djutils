from django.db.models import Func


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

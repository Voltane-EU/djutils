from django.contrib.postgres.operations import CreateExtension


class FuzzystrExtension(CreateExtension):
    def __init__(self):
        self.name = 'fuzzystrmatch'

def combine_bases(cls):
    subclasses = cls.__subclasses__()
    if not subclasses:
        return [cls]

    bases = []
    for sub in subclasses:
        bases = combine_bases(sub) + bases

    bases += [cls]
    return bases


class CombineWithSubclassesMixin:
    def __new__(cls, *args, **kwargs):
        if cls == CombineWithSubclassesMixin:
            raise AttributeError

        if not hasattr(cls, '_COMBINED_BASES'):
            cls._COMBINED_BASES = tuple(combine_bases(cls))

        if len(cls._COMBINED_BASES) > 1:
            new_cls = type("%s (Combined from %s)" % (cls.__name__, cls._COMBINED_BASES), cls._COMBINED_BASES, {'__module__': cls.__module__})
        else:
            new_cls = cls

        ret = super().__new__(new_cls)
        return ret

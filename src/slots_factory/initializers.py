from slots_factory.tools.SlotsFactoryTools import (
    _slots_factory_setattrs,
    _slots_factory_setattrs_slim,
    _slots_factory_setattrs_from_object,
)


def wrapped_slim():
    """wrapper function for when there are no set defaults."""

    def __init__(self, **kwargs):
        _slots_factory_setattrs_slim(self, kwargs, False)

    return __init__


def wrapped_generic():
    """wrapper function for when initializer only has to handle defined
    methods."""

    def __init__(self, **kwargs):
        _data = __init__.__dict__
        _slots_factory_setattrs(
            self, _data["_callables"], _data["_defaults"], kwargs, False
        )

    return __init__


def wrapped_frozen():
    """generic wrapper function for handling all permutations of initialization
    options."""

    def __init__(self, **kwargs):
        _data = __init__.__dict__
        _slots_factory_setattrs_from_object(
            object, self, _data["_callables"], _data["_defaults"], kwargs
        )

    return __init__

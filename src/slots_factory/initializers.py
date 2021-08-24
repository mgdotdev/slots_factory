from slots_factory.tools.SlotsFactoryTools import (
    _slots_factory_setattrs,
    _slots_factory_setattrs_slim,
    _slots_factory_setattrs_from_object,
)


def wrapped_slim():
    """wrapper function for when there are no set defaults."""

    def wrapped(**kwargs):
        instance = wrapped.__dict__["_type"]()
        _slots_factory_setattrs_slim(instance, kwargs, False)
        return instance

    return wrapped


def wrapped_generic():
    """wrapper function for when initializer only has to handle defined
    methods."""

    def wrapped(**kwargs):
        _data = wrapped.__dict__
        instance = _data["_type"]()
        _slots_factory_setattrs(
            instance, _data["_callables"], _data["_defaults"], kwargs, False
        )
        return instance

    return wrapped


def wrapped_frozen():
    """generic wrapper function for handling all permutations of initialization
    options."""

    def wrapped(**kwargs):
        _data = wrapped.__dict__
        instance = _data["_type"]()
        _slots_factory_setattrs_from_object(
            object, instance, _data["_callables"], _data["_defaults"], kwargs
        )
        return instance

    return wrapped

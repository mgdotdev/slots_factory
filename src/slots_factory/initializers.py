from slots_factory.tools.SlotsFactoryTools import (
    _slots_factory_setattrs,
    _slots_factory_setattrs_from_object,
)


def wrapped_slim():
    """wrapper function for when there are no set defaults."""
    def wrapped(**kwargs):
        instance = wrapped.__dict__["_type"]()
        _slots_factory_setattrs(instance, kwargs, False)
        return instance 
    return wrapped


def wrapped_defaults():
    """wrapper function for when initializer only needs to handle setting
    default values."""
    def wrapped(**kwargs):
        _data = wrapped.__dict__
        _defaults = _data["_defaults"]
        if kwargs:
            _defaults.update(kwargs)
        instance = _data["_type"]()
        _slots_factory_setattrs(instance, _defaults, False)
        return instance 
    return wrapped


def wrapped_functions():
    """wrapper function for when initializer only has to handle defined
    methods."""
    def wrapped(**kwargs):
        _data = wrapped.__dict__
        instance = _data["_type"]()
        _slots_factory_setattrs(instance, kwargs, False)
        for k, v in _data['_functions'].items():
            setattr(instance, k, v.__get__(instance))
        return instance
    return wrapped    


def wrapped_not_frozen():
    """wrapper function for when initializer has both defaults and methods,
    but is not frozen."""
    def wrapped(**kwargs):
        _data = wrapped.__dict__
        _defaults = _data["_defaults"]
        if kwargs:
            _defaults.update(kwargs)
        instance = _data["_type"]()
        _slots_factory_setattrs(instance, _defaults, False)
        for k, v in _data['_functions'].items():
            setattr(instance, k, v.__get__(instance))
        return instance
    return wrapped       


def wrapped_generic():
    """generic wrapper function for handling all permutations of initialization
    options."""
    def wrapped(**kwargs):
        _data = wrapped.__dict__
        _defaults = _data["_defaults"]
        _defaults.update(kwargs)
        instance = _data["_type"]()
        _slots_factory_setattrs_from_object(object, instance, _defaults)
        _functions = _data['_functions']
        if _functions:
            for k, v in _functions.items():
                object.__setattr__(instance, k, v.__get__(instance))
        return instance
    return wrapped
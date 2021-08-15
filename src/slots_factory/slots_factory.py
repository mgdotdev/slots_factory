from slots_factory.tools.SlotsFactoryTools import (
    _slots_factory_hash, 
    _slots_factory_setattrs
)


def type_factory(name, args):
    return _type_factory(name, *args)


def slots_from_type(type_, **kwargs):
    instance = type_()
    _slots_factory_setattrs(instance, kwargs)
    return instance


def _type_factory(_name="SlotsObject", *args):
    def __repr__(self):
        contents = ", ".join(
            [f"{key}={getattr(self, key)}" for key in self.__slots__]
        )
        return f"{self.__class__.__name__}({contents})"
    type_ = type(
        _name,
        (),
        {"__slots__": args, "__repr__": __repr__}
    )
    return type_


def slots_factory(_name="SlotsObject", **kwargs):
    stores = slots_factory.__dict__
    _id = _slots_factory_hash(_name, kwargs)
    type_ = stores.get(_id)
    if not type_:
        type_ = _type_factory(_name, *kwargs.keys())
        stores[_id] = type_
    instance = type_()
    _slots_factory_setattrs(instance, kwargs)
    return instance


def fast_slots(_name="SlotsObject", **kwargs):
    stores = fast_slots.__dict__
    type_ = stores.get(_name)
    if not type_:
        type_ = _type_factory(_name, *kwargs.keys())
        stores[_name] = type_
    try:
        instance = type_()
        _slots_factory_setattrs(instance, kwargs)
        return instance
    except Exception:
        del stores[_name]
        return fast_slots(_name, **kwargs)


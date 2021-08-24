from types import FunctionType


def _frozen(self, *_, **__):
    """For setting instances as immutable, via pointing __setattr__ and
    __delattr__ here"""
    raise AttributeError("Instance is immutable")


def _ordering_methods(_keys, _order):
    """Methods to defining ordering. Includes a new __iter__, and the rich
    comparisons"""
    if _order is True:
        _order = sorted(_keys)

    def __iter__(self):
        for item in _order:
            yield item, getattr(self, item)

    def __lt__(self, other):
        for attr in _order:
            left, right = getattr(self, attr), getattr(other, attr)
            if left == right:
                continue
            if left < right:
                return True
            return False
        return False

    def __le__(self, other):
        if self < other:
            return True
        elif self == other:
            return True
        return False

    return {"__iter__": __iter__, "__lt__": __lt__, "__le__": __le__}


def __repr__(self):
    """SlotsObject(key=value...)"""
    contents = ", ".join([f"{key}={getattr(self, key)}" for key in self.__slots__])
    return f"{self.__class__.__name__}({contents})"


def __len__(self):
    """returns the number of items defined by the SlotObject"""
    return len(self.__slots__)


def __eq__(self, other):
    """SlotObjects are considered equal if both attributes and values match"""
    try:
        if len(self) != len(other):
            return False
        return all(
            getattr(self, attr) == getattr(other, attr) for attr in self.__slots__
        )
    except AttributeError:
        return False


def __hash__(self):
    """Hashing is determined by the attribute names"""
    return hash(tuple(self.__slots__))


def __iter__(self):
    for item in self.__slots__:
        yield item, getattr(self, item)

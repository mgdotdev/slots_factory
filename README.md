slots_factory
===

## Factory functions and decorators for creating slot objects

Slots are a python construct that allows users to create an object that doesn't contain `__dict__` or `__weakref__` attributes. The benefit to a slots object is that it has faster attribute access and it saves on memory use, which make slots objects ideal for when you have lots of instances of a single python object.

I've never been a huge fan of the syntax though, as it requires repetitive code for definition as well as instantiation. **yuck.**

```python
class SlotsObject:
    __slots__ = ('x', 'y', 'z')
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        contents = ", ".join(
            [f"{key}={getattr(self, key)}" for key in self.__slots__]
        )
        return f"SlotsObject({contents})"
```

For funsies, I wanted to see if I could create a different way to instantiate these objects, with less jargon. Something like `collections.namedtuple`, but again without redundant definitions and with the benefits of `__slots__`. This repo is the results of such endeavor.


`TL;DR` - the [`@dataslots`](#dataslots) decorator ends up being the most useful implementation, free to skip to it if you want to see the fireworks.


### `slots_factory()`

The first factory function made available is `slots_factory`. Simply import the function, and all **kwargs are assigned as attributes to an instance of a slots object. Type definitions are handled internally by the function, so successive calls to `slots_factory` with the same `_name` and `**kwargs` keys will return new instances of the same type.

For example:

```python
In [1]: from slots_factory import slots_factory

In [2]: this = slots_factory(x=1, y=2, z=3)

In [3]: this
Out[3]: SlotsObject(x=1, y=2, z=3)

In [4]: that = slots_factory(x=4, y=5, z=6)

In [5]: that
Out[5]: SlotsObject(x=4, y=5, z=6)

In [6]: fizzbuzz = slots_factory(_name="fizzbuzz", fizz="fizz", buzz="buzz")

In [7]: fizzbuzz
Out[7]: fizzbuzz(fizz=fizz, buzz=buzz)

In [8]: slots_factory.__dict__
Out[8]:
{13844952821349480973: slots_factory.slots_factory.SlotsObject,
7572372383060875: slots_factory.slots_factory.fizzbuzz}
```

As we can see, we created three instances, `this`, `that`, and `fizzbuzz`. `this` and `that` are instances of the same type, since the function args were the same. `fizzbuzz` is a different type however, since its function arguments were different.

```python
In [9]: type(this) == type(that)
Out[9]: True

In [10]: type(this) == type(fizzbuzz)
Out[10]: False
```

Another benefit to this `SlotsObject` is that, as the underlying type is a slots object, the attributes are dynamic, unlike the `namedtuple`.

```python
In [11]: this.x = 4

In [12]: this
Out[12]: SlotsObject(x=4, y=2, z=3)
```

The type identification and attribute setting is all done in C, in attempt to make instantiation as fast as possible. Instantiation of a `SlotObject` is still about 80% slower than the instantiation of a `namedtuple` (mainly because it handles type definitions internally). Attribute access is on par however, and faster than a normal object as expected.

```python
In [13]: from collections import namedtuple

In [14]: This = namedtuple('This', ['x', 'y', 'z'])

In [15]: %timeit this = This(x=1, y=2, z=3)
315 ns ± 1.58 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)

In [16]: %timeit that = slots_factory('that', x=1,y=2,z=3)
597 ns ± 1.38 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)

In [17]: %timeit this.c
24.6 ns ± 0.132 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)

In [18]: %timeit that.c
25.8 ns ± 0.13 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)
%time
```

### `fast_slots()`

There's a second factory function, `fast_slots`, which is, obviously, faster. Instead of using the builtin hashing algorithm to generate an ID, it simply uses the object name and assumes that all objects named the same, are the same. Since it skips the hashing step, it builds slot instances much faster.

```python
In [4]: from slots_factory import fast_slots

In [5]: %timeit that = fast_slots('that', x=1, y=2, z=3)
442 ns ± 3.71 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)
```

Instead of relying on an internal ID mechanism, `fast_slots` leverages python's `try/except` functionality. The internal `_slots_factory_setattrs` method throws an exception when the object attributes are thought to be different, so when this happens `fast_slots` deletes its old internalized type definition and then builds a new one. As such, if you expect to be redefining the same type over and over again, it's best to use `slots_factory` for better overall performance. If however you're certain to be creating identical instances of the same type (with differing attribute variables of course, that is indeed allowed by `fast_slots`), then you'll be better of using `fast_slots` to do this.

```python
from slots_factory import slots_factory, fast_slots

# use `slots_factory` like so:
this = slots_factory(x=1)
that = slots_factory(y=2)

# use `fast_slots` like so:
category = fast_slots('category', id=1, name='category 1')
category = fast_slots('category', id=2, name='category 2')
```

### `type_factory()`

Finally, if we're really craving the speeds, the most efficient way to use this module is to individually define your types and then manually spin up instances of these objects. This can be done by importing the `type_factory` and `slots_from_type` functions. 

```python
from slots_factory import type_factory, slots_from_type

type_ = type_factory(['x', 'y', 'z'], _name="SlotsObject")
instance = slots_from_type(type_, x=1, y=2, z=3,)
```

```python
In [6]: %timeit instance = slots_from_type(type_, x=1, y=2, z=3)
323 ns ± 10.4 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)
```


### @dataslots

There's a new decorator provided in the `slots_factory` module which attempts to improve upon Python's `dataclasses.dataclass`. Class definitions can be decorated with the `@dataslots` decorator to generate instances of analogous types with `__slots__`. I say `analogous` because at runtime the decorator instantiates a new type instead of modifying the user's defined type. The user's type is simply used as a sort of blueprint for generating the desired type with `__slots__`.

```python
In [1]: from slots_factory import dataslots

@dataslots
class This:
   x: int
   y: int
   z: int

In [2]: %timeit This(x=1, y=2, z=3)
397 ns ± 1.51 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)

@dataslots
class This:
   x: int = 1
   y: int = 2
   z: int = 3

In [2]: %timeit This()
261 ns ± 1.2 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)
```

The `@dataslots` decorator allows for users to set default values using standard python syntax, and defaults can be overwritten simply by defining a new value at instantiation. There is no ordering restrictions on default definitions. It's also worth noting that, normally, when writing `__slots__` classes, we can't define class attributes which conflict with the `__slots__` structure that Python creates. However due to the internal mechanics of `@dataslots`, we can set `__slots__` object defaults absent any annotations.

```python
@dataslots
class FizzBuzz:
    fizz = 'fizz'
    buzz: str
    fizzbuzz: str = 'spam'

In [5]: this = FizzBuzz(buzz='buzz', fizzbuzz='fizzbuzz')
Out[5]: FizzBuzz(fizz=fizz, buzz=buzz, fizzbuzz=fizzbuzz)
```

#### optional arguments for `@dataslots`

`@dataslots` provides a `frozen` keyword argument as a boolean. Passing `frozen=True` to the `@dataslots` decorator forces instances to be immutable.

```python
@dataslots(frozen=True)
class FizzBuzz:
    fizz: str = 'fizz'
    buzz: str = 'buzz'

In [7]: fb = FizzBuzz()

In [8]: fb
Out[8]: FizzBuzz(fizz=fizz, buzz=buzz)

In [9]: fb.fizz = 'buzz'
-----------------------------------------------------------------------
AttributeError                        Traceback (most recent call last)
<ipython-input-9-63a20d67080e> in <module>
----> 1 fb.fizz = 'buzz'

~/programming/python/slots_factory/src/slots_factory/slots_factory.py in _frozen(self, *_, **__)
127             def _frozen(self, *_, **__):
128                 raise AttributeError("instance is immutable.")
--> 129             methods.update({
130                 "__setattr__": _frozen,
131                 "__delattr__": _frozen

AttributeError: instance is immutable.
```

`@dataslots` also provides an `order` keyword argument as either a boolean or an iterable. If passed as a boolean, items are iterated over in whatever manner Python decides to sort the attribute names. Order can be made explicit by passing an iterable of attribute names for yielding.

```python

@dataslots(order=True)
class This:
    x: int
    y: int
    z: int

In [1]: this = This(x=1, y=2, z=3)

In [2]: [x for x in this]
Out[2]: [('x', 1), ('y', 2), ('z', 3)]     


@dataslots(order=['x', 'z', 'y'])
class This:
    x: int
    y: int
    z: int

In [3]: this = This(x=1, y=2, z=3)

In [4]: [x for x in this]
Out[4]: [('x', 1), ('z', 3), ('y', 2)] 
```

Ordering implies hierarchy, and hierarchy provides a means for rich comparisons. Instances that are ordered can be compared using Python's builtin comparison operators. Comparison is done by applying the respected operator's method as defined on the `self` of the pair of objects, in order, across attributes. Comparison is resolved at first instance of inequality.

```python
@dataslots(order=True)
class This:
    x: int = 1
    y: int = 2
    z: int = 3

@dataslots(order=True)
class That:
    x: int = 4
    y: int = 5
    z: int = 6

In [1]: this, that = This(), That()

In [2]: this < that
Out[2]: True

In [3]: this = This(x=6)

In [4]: this < that
Out[4]: False
```

Though dataslots are not dictionaries, they have many of the properties you would expect from a dictionary object. As such, conversion to and from dictionaries is built in. And as dictionaries are ordered in Python 3.6+, we make sure to preserve order between conversions.

```python
@dataslots(order=["x", "z", "y"])
class This:
    x: int
    y: int
    z: int

In [1]: this = This(x=1, y=2, z=3)

In [2]: that = dict(this)

In [3]: that
Out[3]: {'x': 1, 'z': 3, 'y': 2}

In [4]: dataslots.from_dict(that)
Out[4]: SlotsObject(x=1, z=3, y=2)
```

Dataslots also supports user-defined methods and properties. They can be defined as normal on the class, and @dataslots will be sure to carry these objects over to the `__slots__` object.

```python
@dataslots
class FizzBuzz:
    fizz = 'fizz'
    buzz: str = 'buzz'

    def fizzbuzz(self):
        return self.fizz + self.buzz

In [1]: fizzbuzz = FizzBuzz()

In [2]: fizzbuzz.fizzbuzz()
Out[2]: "fizzbuzz"

@dataslots
class FizzBuzz:
    fizz = 'fizz'
    buzz: str = 'buzz'

    @property
    def fizzbuzz(self):
        return self.fizz + self.buzz

    @fizzbuzz.setter
    def fizzbuzz(self, item):
        self.fizz, self.buzz = item

In [1]: fizzbuzz = FizzBuzz()

In [2]: fizzbuzz.fizzbuzz
Out[2]: 'fizzbuzz'

In [3]: fizzbuzz.fizzbuzz = ("This", "That")

In [4]: fizzbuzz.fizzbuzz
Out[4]: 'ThisThat'
```

#### Mutable default types in `@dataslots` via `lambda`

Given the nature of mutable types in Python, it's always been considered gauche to define default values as mutable types within object definitions. In order to allow for mutable defaults whose references aren't shared across instances, `@dataslots` default values can be assigned as either `type` type or a `lambda` expression with no arguments. These defaults are then called on instantiation, and instances assigned the result of the callable.

```python
@dataslots
class RecordsCollection:
    list_of_records = lambda: [{"record_id": 0, "name": "Terminal Record"}]
    record_count: int = 1

    def add_record(self, _id, name):
        self.record_count += 1
        self.list_of_records.append({
                "record_id": _id,
                "name": name
            }
        )

@dataslots
class RecordIds:
    ids = set

    def ingest_record(self, record):
        for item in record.list_of_records:
            self.ids.add(item["record_id"])


In [1]: n1 = RecordsCollection()

In [2]: %timeit RecordsCollection()
Out[2]: 496 ns ± 1.95 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)

In [3]: n2 = RecordsCollection()

In [4]: n1.add_record(5, "New Record")

In [5]: n1.list_of_records
Out[5]: [{'record_id': 0, 'name': 'Terminal Record'}, {'record_id': 5, 'name': 'New Record'}]

In [6]: n2.list_of_records
Out[6]: [{'record_id': 0, 'name': 'Terminal Record'}]

In [7]: rec_ids = RecordIds()

In [8]: rec_ids.ingest_record(n1)

In [9]: rec_ids.ids
Out[9]: {0, 5}
```


#### Inheritance and Composition in `@dataslots`

`@dataslots` objects can inherit artifacts from other dataslots. However, given that `@dataslots` is regenerating new datatypes on the fly, it currently doesn't have any concept of method resolution order, nor does it understand the concept of `super()`. A derived class simply updates its default values with preference given to the first base class in queue. Given this, class composition is generally regarded as a better implementation strategy, given `@dataslots`'s compatibility with default type instantiations.

```python
"""inheritance"""
@dataslots
class A:
    a: list = lambda: [1,2,3]

@dataslots
class B:
    a = list

@dataslots
class DerivedOne(A, B):
    def get_list(self):
        return self.a

@dataslots
class DerivedTwo(B, A):
    def get_list(self):
        return self.a

In [1]: instance_one = DerivedOne()

In [2]: instance_two = DerivedTwo()

In [3]: instance_one.get_list()
Out[3]: [1,2,3]

In [4]: instance_two.get_list()
Out[4]: []
```

```python
"""composition"""
@dataslots
class SubcomponentOne:
    x = 1

@dataslots
class SubcomponentTwo:
    x = lambda: [1, 2, 3]

@dataslots
class RootClass:
    s1 = SubcomponentOne
    s2 = SubcomponentTwo

In [1]: instance = RootClass()

In [2]: repr(instance)
Out[2]: 'RootClass(s1=SubcomponentOne(x=1), s2=SubcomponentTwo(x=[1, 2, 3]))'

In [3]: instance.s2.x
Out[3]: [1, 2, 3]
```

#### Dependent defaults in `@dataslots`

Attributes oftentimes depend on the state of other attributes within an object. This can be tricky when it comes to default values in __slots__, as if you set values at type definition, those attributes become read-only. One solution to this is to define the attribute as a `@property`, so that the `property` has access to the instance when referenced.

`@dataslots` provides a leaner alternative, once again using the `lambda` function as a means for default assignments. lambda functions assigned to attributes can take a single argument, `self`. At instantiation the lambda is called and the resultant is assigned to the instance attribute.

```python

import pymongo
import redis

from slots_factory import dataslots

@dataslots
class Redis:
    queue = redis.Redis(host="redis-queue")


@dataslots
class Mongo:
    client = pymongo.MongoClient("mongodb://mongo:27017")
    database = lambda self: self.client.get_database("primary")


@dataslots
class Connections:
    mongo = Mongo
    redis = Redis

In [1]: conn = Connections()

In [2]: conn.mongo.database
Out[2]: Database(MongoClient(host=['mongo:27017'], document_class=dict, tz_aware=False, connect=True), 'primary')
```

## Appendix: Some pure-Python implementations

This module uses custom C extensions for trying to speed up attribute write times. However the inclusion of this requires `slots_factory` to be installed and the extensions compiled. If that seems undesirable, here are some pure-Python implementations that can simply be copied into a codebase.

```python

def slots_factory(_name="SlotsObject", **kwargs):
    stores = slots_factory.__dict__
    _keys = frozenset(kwargs)
    if _name == "SlotsObject":
        _id = hash(_keys)
        _type = stores.get(_id)
    else:
        _id = hash(_name) ^ hash(_keys)
        _type = stores.get(_id)
    if not _type:
        def __repr__(self):
            contents = ", ".join(
                [f"{key}={getattr(self, key)}" for key in self.__slots__]
            )
            return f"{self.__class__.__name__}({contents})"
        _type = type(
            _name,
            (),
            {"__slots__": _keys, "__repr__": __repr__}
        )
        stores[_id] = _type
    instance = _type()
    for key, value in kwargs.items():
        setattr(instance, key, value)
    return instance


def fast_slots(_name="SlotsObject", **kwargs):
    _type = fast_slots.__dict__.get(_name)
    if not _type:
        def __repr__(self):
            contents = ", ".join(
                [f"{key}={getattr(self, key)}" for key in self.__slots__]
            )
            return f"{self.__class__.__name__}({contents})"
        _type = type(
            _name,
            (),
            {"__slots__": kwargs.keys(), "__repr__": __repr__}
        )
        fast_slots.__dict__[_name] = _type
    instance = _type()
    try:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        return instance
    except AttributeError:
        del fast_slots.__dict__[_name]
        return fast_slots(_name, **kwargs)
```
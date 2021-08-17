slot_factory 
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


(`TL;DR` - the [`@dataslots`](#dataslots) decorator ends up being the most useful implementation, free to skip to it if you want to see the fireworks.)


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
{1040: slots_factory.slots_factory.SlotsObject,
1419034624: slots_factory.slots_factory.fizzbuzz}
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

type_ = type_factory("SlotsObject", ['x', 'y', 'z'])
instance = slots_from_type(type_, x=1, y=2, z=3,)
```

```python
In [6]: %timeit instance = slots_from_type(type_, x=1, y=2, z=3)
323 ns ± 10.4 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)
```

`slots_from_type` is a convenience function; you can also instantiate your own instance and then pass it through the underlying `_slots_factory_setattrs` function, which is what actually populates the attributes.

```python
from slots_factory import type_factory
from slots_factory.tools.SlotsFactoryTools import _slots_factory_setattrs

my_type = type_factory("SlotsObject", ['x', 'y', 'z'])
instance = my_type()
_slots_factory_setattrs(my_type, {'x': 1, 'y': 2, 'z': 3})
```

### @dataslots

There's a new decorator provided in the `slots_factory` module which attempts to improve upon Python's `dataclasses.dataclass`. Class definitions can be decorated with the `@dataslots` decorator to generate instances of analogous types with `__slots__`. I say `analogous` because at runtime the decorator instantiates a new type instead of modifying the user's defined type. The user's type is simply used as a sort of blueprint for generating the desired type with `__slots__`.

```python
In [1]: from slots_factory import dataslots

In [2]: @dataslots
   ...: class This:
   ...:    x: int
   ...:    y: int
   ...:    z: int
   ...:

In [3]: %timeit This(x=1, y=2, z=3)
344 ns ± 7.07 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)
```

The `@dataslots` decorator allows for users to set default values using standard python syntax, and defaults can be overwritten simply by defining a new value at instantiation. There is no ordering restrictions on default definitions.

```python
In [4]: @dataslots
   ...: class FizzBuzz:
   ...:     fizz: str = 'fizz'
   ...:     buzz: str
   ...:     fizzbuzz: str = 'spam'

In [5]: this = FizzBuzz(buzz='buzz', fizzbuzz='fizzbuzz')
Out[5]: FizzBuzz(fizz=fizz, buzz=buzz, fizzbuzz=fizzbuzz)
```

#### optional arguments for `@dataslots`

`@dataslots` provides a `frozen` keyword argument as a boolean. Passing `frozen=True` to the `@dataslots` decorator forces instances to be immutable.

```python
In [6]: @dataslots(frozen=True)
   ...: class FizzBuzz:
   ...:     fizz: str = 'fizz'
   ...:     buzz: str = 'buzz'

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
    def test_order_true(self):
        @dataslots(order=True)
        class This:
            x: int
            y: int
            z: int

        this = This(x=1, y=2, z=3)
        assert [x for x in this] == [1, 2, 3]     

    def test_order_explicit(self):
        @dataslots(order=['x', 'z', 'y'])
        class This:
            x: int
            y: int
            z: int

        this = This(x=1, y=2, z=3)
        assert [x for x in this] == [1, 3, 2]
```
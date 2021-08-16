slot_factory 
===

## Factory functions for creating slot objects

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

### `slots_factory()`

The first factory function made available is `slots_factory`. Simply import the function, and all **kwargs are assigned as attributes to an instance of a slots object. Type definitions are handled internally by the function, so successive calls to `slots_factory` with the same `_name` and `**kwargs` keys will return new instances of the same type.

For example:

```python
In [1]: from slots_factory import slots_factory

In [2]: this = slots_factory(x=1,y=2,z=3)

In [3]: this
Out[3]: SlotsObject(x=1, y=2, z=3)

In [4]: that = slots_factory(x=4,y=5,z=6)

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

The type identification and attribute setting is all done in C, in attempt to make instantiation as fast as possible. Instantiation of a `SlotObject` is about 80% slower than the instantiation of a `namedtuple` (mainly because it handles type definitions internally). Attribute access is on par however, and faster than a normal object as expected.

```python
In [13]: from collections import namedtuple

In [14]: This = namedtuple('This', ['x', 'y', 'z', 'a', 'b', 'c'])

In [15]: %timeit this = This(x=1,y=2,z=3,a=4,b=5,c=6)
444 ns ± 5.2 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)

In [16]: %timeit that = slots_factory('that', x=1,y=2,z=3,a=4,b=5,c=6)
809 ns ± 2.65 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)

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

In [5]: %timeit that = fast_slots('that', x=1,y=2,z=3,a=4,b=5,c=6)
579 ns ± 4.64 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)
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

type_ = type_factory("SlotsObject", ['x', 'y', 'z', 'a', 'b', 'c'])
instance = slots_from_type(type_, x=1, y=2, z=3, a=4, b=5, c=6)
```

```python
In [6]: %timeit instance = slots_from_type(type_, x=1, y=2, z=3, a=4, b=5, c=6)
521 ns ± 2.73 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)
```

`slots_from_type` is a convenience function; you can also instantiate your own instance and then pass it through the underlying `_slots_factory_setattrs` function, which is what actually populates the attributes.

```python
from slots_factory import type_factory
from slots_factory.tools.SlotsFactoryTools import _slots_factory_setattrs

my_type = type_factory("SlotsObject", ['x', 'y', 'z', 'a', 'b', 'c'])
instance = my_type()
_slots_factory_setattrs(my_type, {'x': 1, 'y': 2, 'z': 3, 'a': 4, 'b': 5, 'c': 6})
```

Using the `type_factory` is essentially equivalent to the use of a `namedtuple`, but without it's `count` and `index` methods, and with dynamic attributes. Also, all of that redundant typing is back... `¯\_(ツ)_/¯`

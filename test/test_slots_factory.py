import pytest

from slots_factory import (
    slots_factory,
    fast_slots,
    slots_from_type,
    type_factory,
    slots_from_dict,
    dataslots,
)


from slots_factory.tools.SlotsFactoryTools import (
    _slots_factory_hash,
    _slots_factory_setattrs,
    _slots_factory_setattrs_slim,
)


@pytest.fixture(scope="session")
def type_():
    args = ("x", "y", "z")
    _type = type_factory(args)
    yield _type


@pytest.fixture(scope="class")
def _ordered_types():
    @dataslots(order=True)
    class This:
        """Docstrings"""

        x: int = 1
        y: int = 2
        z: int = 3

    @dataslots(order=True)
    class That:
        """Docstrings"""

        x: int = 4
        y: int = 5
        z: int = 6

    yield This, That


@pytest.fixture(scope="class")
def ds(_ordered_types):
    This, _ = _ordered_types
    this = This(x=1, y=2, z=3)
    yield this


@pytest.fixture(scope="session")
def dict_():
    return {"x": 1, "y": 2, "z": 3}


class TestTools:
    def test_hashing(self):
        one = _slots_factory_hash("SlotsObject", {"x": 1, "y": 2})
        two = _slots_factory_hash("SlotsObject", {"x": 1, "y": 2, "z": 3})
        assert one != two

    def test_attr_setting_slim(self, type_, dict_):
        instance = type_()
        _slots_factory_setattrs_slim(instance, dict_, True)
        assert all(getattr(instance, key) == value for key, value in dict_.items())

    def test_attr_error(self, type_):
        instance = type_()
        with pytest.raises(AttributeError) as e:
            _slots_factory_setattrs_slim(instance, {"x": 1, "y": 2}, True)
        assert e.type == AttributeError
        assert e.value.args == ("Mismatch in number of attributes",)


class TestSlotsFactory:
    def test_slots_factory(self):
        instance = slots_factory(x=1, y=2)
        assert instance.x == 1
        assert instance.y == 2
        assert repr(instance) == "SlotsObject(x=1, y=2)"

    def test_caching(self):
        _, _ = slots_factory(x=1, y=2), slots_factory(x=1, y=2)
        assert len(slots_factory.__dict__) == 1

        _ = slots_factory("fizz", x=1, y=2)
        assert len(slots_factory.__dict__) == 2

        _ = slots_factory(x=1, y=2, z=3)
        assert len(slots_factory.__dict__) == 3

    def test_names(self):
        _name = "category"
        instance = slots_factory(_name, cat_id=1, name="category 1")
        assert instance.__class__.__name__ == _name


class TestFastSlots:
    def test_fast_slots(self):
        instance = fast_slots(x=1, y=2)
        assert instance.x == 1
        assert instance.y == 2
        assert repr(instance) == "SlotsObject(x=1, y=2)"

    def test_caching(self):
        _ = fast_slots("SlotsObject", x=1, y=2)
        _ = fast_slots("SlotsObject", x=1, y=2, z=3)
        assert len(fast_slots.__dict__) == 1


class TestSlotsFromType:
    def test_slots_from_type(self, type_):
        instance = slots_from_type(type_, x=1, y=2, z=3)
        assert instance.x == 1
        assert instance.y == 2
        assert instance.z == 3


class TestTypeFactory:
    def test_type_factory(self):
        args = ("x", "y")
        _type = type_factory(args)
        assert _type.__slots__ == args


class TestDataSlots:
    def test_data_slots(self, ds):
        assert (ds.x, ds.y, ds.z) == (1, 2, 3)

    def test_docs(self, ds):
        assert ds.__doc__ == "Docstrings"

    def test_repr(self, ds):
        assert repr(ds) == str(ds) == "This(x=1, y=2, z=3)"

    def test_len(self, ds):
        assert len(ds) == 3

    def test_hash(self, ds):
        assert hash(ds)

    def test_default_iter(self):
        @dataslots
        class That:
            x: int = 1
            y: int = 2
            z: int = 3

        # iterable, but order not defined
        assert [x for x in That()]

    def test_eq(self, ds):
        @dataslots
        class That:
            x: int = 1
            y: int = 2
            z: int = 3

        that = That()
        assert ds == that
        assert repr(ds) != repr(that)

    def test_eq_bad_len(self, ds):
        @dataslots
        class That:
            x: int = 1
            y: int = 2
            z: int = 3
            a: int = 4

        that = That()
        assert ds != that

    def test_eq_bad_name(self, ds):
        @dataslots
        class That:
            x: int = 1
            y: int = 2
            a: int = 3

        that = That()
        assert ds != that

    def test_eq_different_values(self, ds):
        @dataslots
        class That:
            x: int = 1
            y: int = 2
            z: int = 4

        that = That()
        assert ds != that

    def test_sorting(self):
        @dataslots(order=True)
        class This:
            x: int
            y: int
            z: int

        one = This(x=1, y=2, z=3)
        two = This(x=1, y=0, z=4)
        three = This(x=2, y=1, z=0)

        list_ = [one, two, three]
        list_.sort()
        actual = [[getattr(item, attr) for attr in ("x", "y", "z")] for item in list_]
        expected = [[1, 0, 4], [1, 2, 3], [2, 1, 0]]
        assert actual == expected

    def test_orderings(self, _ordered_types):
        This, That = _ordered_types

        this = This()
        that = That()

        assert this < that
        assert that > this
        assert this <= that
        assert that >= this
        assert this != that

        this = This(x=6)

        assert this > that
        assert not this < that

        this = This(x=4, y=5, z=6)
        assert not that > this
        assert that <= this

        this = This(x=7, y=8, z=9)
        assert not this <= that


class TestDataSlotsOptions:
    def test_frozen(self):
        @dataslots(frozen=True)
        class This:
            x: int
            y: int
            z: int

        this = This(x=1, y=2, z=3)
        with pytest.raises(AttributeError) as e:
            this.z = 2

        assert e.type == AttributeError
        assert e.value.args == ("Instance is immutable",)

    def test_order_true(self):
        @dataslots(order=True)
        class This:
            x: int
            y: int
            z: int

        this = This(x=1, y=2, z=3)
        assert [x for x in this] == [("x", 1), ("y", 2), ("z", 3)]

    def test_order_explicit(self):
        @dataslots(order=["x", "z", "y"])
        class This:
            x: int
            y: int
            z: int

        this = This(x=1, y=2, z=3)
        assert [x for x in this] == [("x", 1), ("z", 3), ("y", 2)]


class TestDataSlotsConversions:
    def test_slots_from_dict(self):
        expected = {"this": "this", "that": "that"}
        this = slots_from_dict(expected, _name="ThisThat")
        actual = dict(this)
        assert all(a == b for (a, b) in zip(actual, expected))

    def test_to_dict(self, ds, dict_):
        actual = dict(ds)
        assert all(a == b for (a, b) in zip(actual, dict_))

        @dataslots(order=["x", "z", "y"])
        class This:
            x: int
            y: int
            z: int

        this = This(x=1, y=2, z=3)
        actual = dict(this)
        expected = {"x": 1, "z": 3, "y": 2}
        assert all(a == b for (a, b) in zip(actual, expected))

    def test_from_dict(self, dict_):
        this = dataslots.from_dict(dict_)
        assert all(a == b for ((a, _), b) in zip(this, dict_))

    def test_order_preserved(self, dict_):
        ds = dataslots.from_dict(dict_)
        actual = dict(ds)
        assert all(a == b for (a, b) in zip(actual, dict_))


class TestUserDefinitions:
    def test_no_annotations(self):
        @dataslots
        class Fizz:
            fizz = "fizz"
            buzz: str = "buzz"
            fizzbuzz: str

        fizz = Fizz(fizzbuzz="fizzbuzz")
        assert all(hasattr(fizz, item) for item in ["fizz", "buzz", "fizzbuzz"])

        fizz = Fizz(fizz="buzz", buzz="fizz", fizzbuzz="fizzbuzz")
        assert fizz.buzz == "fizz"
        assert fizz.fizz == "buzz"

    def test_user_methods(self):
        @dataslots
        class FizzBuzz:
            fizz = "fizz"
            buzz: str = "buzz"

            def fizzbuzz(self):
                return self.fizz + self.buzz

        fizzbuzz = FizzBuzz()
        assert fizzbuzz.fizzbuzz() == "fizzbuzz"

        fizzbuzz = FizzBuzz(fizz="This", buzz="That")
        assert fizzbuzz.fizzbuzz() == "ThisThat"

    def test_functions_only(self):
        @dataslots
        class FizzBuzz:
            fizz: str
            buzz: str

            def fizzbuzz(self):
                return self.fizz + self.buzz

        fizzbuzz = FizzBuzz(fizz="fizz", buzz="buzz")
        assert fizzbuzz.fizzbuzz() == "fizzbuzz"

    def test_property(self):
        @dataslots
        class FizzBuzz:
            _fizz = "fizz"
            _buzz: str = "buzz"

            @property
            def fizzbuzz(self):
                return self._fizz + self._buzz

            @fizzbuzz.setter
            def fizzbuzz(self, item):
                self._fizz, self._buzz = item

        fizzbuzz = FizzBuzz()

        assert fizzbuzz.fizzbuzz == "fizzbuzz"
        fizzbuzz.fizzbuzz = ("This", "That")
        assert fizzbuzz.fizzbuzz == "ThisThat"

    def test_frozen_functions(self):
        @dataslots(frozen=True)
        class FizzBuzz:
            fizz: str
            buzz: str

            def fizzbuzz(self):
                return self.fizz + self.buzz

        fizzbuzz = FizzBuzz(fizz="fizz", buzz="buzz")

        assert fizzbuzz.fizzbuzz() == "fizzbuzz"
        with pytest.raises(AttributeError) as e:
            fizzbuzz.fizzbuzz = "spam"

        assert e.type == AttributeError
        assert e.value.args == ("Instance is immutable",)


class TestEdgeCases:
    def test_mutable_defaults(self):
        @dataslots
        class This:
            items = set

        this = This()

        this.items.add(1)

        that = This()

        assert this != that
        assert this.items != that.items

    def test_lambda_function(self):
        @dataslots
        class This:
            items: set = lambda: set([1, 2])

        this = This()
        that = This()

        this.items.add(3)

        assert this.items != that.items
        assert len(this.items) == 3


# class TestDerivedObjects:
#     def test_derived_dataslots(self):
#         @dataslots
#         class Base:
#             x: int = 1

#         class Derived(Base):
#             y: int = 2

#         instance = Derived()
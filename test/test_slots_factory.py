import pytest

from slots_factory import (
    slots_factory,
    fast_slots,
    slots_from_type,
    type_factory,
    dataslots,
)


from slots_factory.tools.SlotsFactoryTools import (
    _slots_factory_hash,
    _slots_factory_setattrs,
)


@pytest.fixture(scope="session")
def type_():
    _type = type_factory("SlotsObject", ("a", "b", "c"))
    yield _type


@pytest.fixture(scope="class")
def ds():
    @dataslots
    class This:
        """Docstrings"""

        x: int
        y: int
        z: int

    this = This(x=1, y=2, z=3)
    yield this


class TestTools:
    def test_hashing(self):
        one = _slots_factory_hash("SlotsObject", {"x": 1, "y": 2})
        two = _slots_factory_hash("SlotsObject", {"x": 1, "y": 2, "z": 3})
        assert one != two

    def test_attr_setting(self, type_):
        mapping = {"a": 1, "b": 2, "c": 3}
        instance = type_()
        _slots_factory_setattrs(instance, mapping, True)
        assert all(getattr(instance, key) == value for key, value in mapping.items())

    def test_attr_error(self, type_):
        instance = type_()
        with pytest.raises(AttributeError) as e:
            _slots_factory_setattrs(instance, {"a": 1, "b": 2}, True)
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
        instance = slots_from_type(type_, a=1, b=2, c=3)
        assert instance.a == 1
        assert instance.b == 2
        assert instance.c == 3


class TestTypeFactory:
    def test_type_factory(self):
        args = ("x", "y")
        _type = type_factory("Slots_Object", args)
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

    def test_eq(self, ds):
        @dataslots
        class That:
            x: int = 1
            y: int = 2
            z: int = 3

        that = That()
        assert ds == that

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
        expected = [[2, 1, 0], [1, 0, 4], [1, 2, 3]]
        assert actual == expected


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
        assert e.value.args == ("Instance is immutable.",)

    def test_order_true(self):
        @dataslots(order=True)
        class This:
            x: int
            y: int
            z: int

        this = This(x=1, y=2, z=3)
        assert [x for x in this] == [1, 2, 3]

    def test_order_explicit(self):
        @dataslots(order=["x", "z", "y"])
        class This:
            x: int
            y: int
            z: int

        this = This(x=1, y=2, z=3)
        assert [x for x in this] == [1, 3, 2]

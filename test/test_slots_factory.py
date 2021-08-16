import pytest

from slots_factory import slots_factory, fast_slots, slots_from_type, type_factory


from slots_factory.tools.SlotsFactoryTools import (
    _slots_factory_hash,
    _slots_factory_setattrs,
)


@pytest.fixture(scope="session")
def type_():
    _type = type_factory("SlotsObject", ("a", "b", "c"))
    yield _type


class TestTools:
    def test_hashing(self):
        one = _slots_factory_hash("SlotsObject", {"x": 1, "y": 2})
        two = _slots_factory_hash("SlotsObject", {"x": 1, "y": 2, "z": 3})
        assert one != two

    def test_attr_setting(self, type_):
        mapping = {"a": 1, "b": 2, "c": 3}
        instance = type_()
        _slots_factory_setattrs(instance, mapping)
        assert all(getattr(instance, key) == value for key, value in mapping.items())

    def test_attr_error(self, type_):
        instance = type_()
        with pytest.raises(AttributeError) as e:
            _slots_factory_setattrs(instance, {"a": 1, "b": 2})
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

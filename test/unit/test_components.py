from slots_factory.slots_factory import DSMeta

class TestMetaClass:
    def test_no_bases(self):
        class This:
            pass

        my_type = DSMeta("my_type", (This, ), {})

        assert my_type.__class__.__bases__ == (type, )

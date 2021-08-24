import timeit

from slots_factory import dataslots


class TestDataSlotsInitializationBenchmarks:
    def test_slim_benchmark(self):
        @dataslots
        class This:
            x: int
            y: int
            z: int

        res = timeit.timeit("This(x=1, y=2, z=3)", globals=locals(), number=1_000_000)

        # res typically around 0.32 seconds /1M instances
        # or 320 nanoseconds / instance
       
        assert res < 0.39

    def test_defaults_benchmark(self):
        @dataslots
        class This:
            x: int = 1
            y: int = 2
            z: int = 3

        res = timeit.timeit("This(x=1, y=2, z=3)", globals=locals(), number=1_000_000)

        # res typically around 0.41 seconds /1M instances
        # or 410 nanoseconds / instance if all kwargs are
        # defined
        
        assert res < 0.48

        res = timeit.timeit("This()", globals=locals(), number=1_000_000)

        # res typically around 0.30 seconds /1M instances
        # or 300 nanoseconds / instance if no kwargs are
        # defined
        
        assert res < 0.37

    def test_property_benchmark(self):
        @dataslots
        class This:
            x: int
            y: int
            z: int

            @property
            def summation(self):
                return self.x + self.y + self.z

        res = timeit.timeit("This(x=1, y=2, z=3)", globals=locals(), number=1_000_000)

        # res typically around 0.30 seconds /1M instances
        # or 300 nanoseconds / instance
        
        assert res < 0.37

    def test_functions_benchmark(self):
        @dataslots
        class This:
            x: int
            y: int
            z: int

            def summation(self):
                return self.x + self.y + self.z

        res = timeit.timeit("This(x=1, y=2, z=3)", globals=locals(), number=1_000_000)

        # res typically around 0.30 seconds /1M instances
        # or 300 nanoseconds / instance
        
        assert res < 0.37

    def test_no_frozen_benchmark(self):
        @dataslots
        class This:
            x: int = 1
            y: int = 2
            z: int = 3

            @property
            def summation(self):
                return self.x + self.y + self.z
        
        res = timeit.timeit("This(x=1, y=2, z=3)", globals=locals(), number=1_000_000)

        # res typically around 0.43 seconds /1M instances
        # or 430 nanoseconds / instance if all kwargs are
        # defined
        
        assert res < 0.50

        res = timeit.timeit("This()", globals=locals(), number=1_000_000)

        # res typically around 0.27 seconds /1M instances
        # or 270 nanoseconds / instance if no kwargs are
        # defined

        assert res < 0.35

    def test_frozen_benchmark(self):
        @dataslots(frozen=True)
        class This:
            x: int = 1
            y: int = 2
            z: int = 3

        res = timeit.timeit("This(x=1, y=2, z=3)", globals=locals(), number=1_000_000)

        # res typically around 1.40 seconds /1M instances
        # or 1400 nanoseconds / instance if all kwargs are
        # defined
        
        assert res < 1.47

        res = timeit.timeit("This()", globals=locals(), number=1_000_000)

        # res typically around 0.78 seconds /1M instances
        # or 780 nanoseconds / instance if no kwargs are
        # defined

        assert res < 0.84

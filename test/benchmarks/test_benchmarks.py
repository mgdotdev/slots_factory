"""benchmarks for comparing relative changes in execution speed. Note, these
values tend to run slower than in vivo (terimal)"""

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

        # res typically around 0.51 seconds /1M instances
        # or 510 nanoseconds / instance

        assert res < 0.57

    def test_defaults_benchmark(self):
        @dataslots
        class This:
            x: int = 1
            y: int = 2
            z: int = 3

        res = timeit.timeit("This()", globals=locals(), number=1_000_000)

        # res typically around 0.29 seconds /1M instances
        # or 290 nanoseconds / instance if no kwargs are
        # defined

        assert res < 0.35

        res = timeit.timeit("This(x=1, y=2, z=3)", globals=locals(), number=1_000_000)

        # res typically around 0.55 seconds /1M instances
        # or 550 nanoseconds / instance if all kwargs are
        # defined

        assert res < 0.62

        @dataslots
        class That:
            x: set
            y: list = lambda: []

        res = timeit.timeit("That()", globals=locals(), number=1_000_000)

        # res typically around 0.33 seconds /1M instances
        # or 330 nanoseconds / instance if all kwargs are
        # defined

        assert res < 0.4

        res = timeit.timeit("That(x=set(), y=[])", globals=locals(), number=1_000_000)

        # res typically around 0.58 seconds /1M instances
        # or 580 nanoseconds / instance if all kwargs are
        # defined

        assert res < 0.65

    def test_property_benchmark(self):
        @dataslots
        class This:
            x: int = 1
            y: int = 2
            z: int = 3

            @property
            def summation(self):
                return self.x + self.y + self.z

        res = timeit.timeit("This()", globals=locals(), number=1_000_000)

        # res typically around 0.29 seconds /1M instances
        # or 290 nanoseconds / instance

        assert res < 0.35

        res = timeit.timeit("This(x=1, y=2, z=3)", globals=locals(), number=1_000_000)

        # res typically around 0.54 seconds /1M instances
        # or 540 nanoseconds / instance

        assert res < 0.60

    def test_functions_benchmark(self):
        @dataslots
        class This:
            x: int
            y: int
            z: int

            def summation(self):
                return self.x + self.y + self.z

        res = timeit.timeit("This(x=1, y=2, z=3)", globals=locals(), number=1_000_000)

        # res typically around 0.53 seconds /1M instances
        # or 530 nanoseconds / instance

        assert res < 0.60

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

        # res typically around 0.55 seconds /1M instances
        # or 550 nanoseconds / instance if all kwargs are
        # defined

        assert res < 0.62

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

        # res typically around 1.59 seconds /1M instances
        # or 1590 nanoseconds / instance if all kwargs are
        # defined

        assert res < 1.66

        res = timeit.timeit("This()", globals=locals(), number=1_000_000)

        # res typically around 0.78 seconds /1M instances
        # or 780 nanoseconds / instance if no kwargs are
        # defined

        assert res < 0.84

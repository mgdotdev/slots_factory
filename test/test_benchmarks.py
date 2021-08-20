import timeit

from slots_factory import (
    dataslots
)


class TestDataSlotsInitializationBenchmarks:
    def test_slim_benchmark(self):
        @dataslots
        class This:
            x: int
            y: int
            z: int

        res = timeit.timeit(
            "This(x=1, y=2, z=3)",
            globals=locals(),
            number=1_000_000
        )

        # res typically around 0.32 seconds /1M instances 
        # or 320 nanoseconds / instance
        assert res < 0.4


    def test_defaults_benchmark(self):
        @dataslots
        class This:
            x: int = 1
            y: int = 2
            z: int = 3

        res = timeit.timeit(
            "This(x=1, y=2, z=3)",
            globals=locals(),
            number=1_000_000
        )

        # res typically around 0.43 seconds /1M instances 
        # or 430 nanoseconds / instance if all kwargs are
        # defined
        assert res < 0.5

        res = timeit.timeit(
            "This()",
            globals=locals(),
            number=1_000_000
        )

        # res typically around 0.27 seconds /1M instances 
        # or 270 nanoseconds / instance if no kwargs are
        # defined
        assert res < 0.32


    def test_functions_benchmark(self):
        @dataslots
        class This:
            x: int
            y: int
            z: int

            @property
            def sum(self):
                return self.x + self.y + self.z

        res = timeit.timeit(
            "This(x=1, y=2, z=3)",
            globals=locals(),
            number=1_000_000
        )

        # res typically around 0.63 seconds /1M instances 
        # or 630 nanoseconds / instance
        assert res < 0.70


    def test_no_frozen_benchmark(self):
        @dataslots
        class This:
            x: int = 1
            y: int = 2
            z: int = 3

            @property
            def summation(self):
                return self.x + self.y + self.z

        res = timeit.timeit(
            "This(x=1, y=2, z=3)",
            globals=locals(),
            number=1_000_000
        )

        # res typically around 0.43 seconds /1M instances 
        # or 430 nanoseconds / instance if all kwargs are
        # defined

        assert res < 0.50

        res = timeit.timeit(
            "This()",
            globals=locals(),
            number=1_000_000
        )

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

        res = timeit.timeit(
            "This(x=1, y=2, z=3)",
            globals=locals(),
            number=1_000_000
        )

        # res typically around 0.97 seconds /1M instances 
        # or 970 nanoseconds / instance if all kwargs are
        # defined
        assert res < 1.04

        res = timeit.timeit(
            "This()",
            globals=locals(),
            number=1_000_000
        )

        # res typically around 0.90 seconds /1M instances 
        # or 900 nanoseconds / instance if no kwargs are
        # defined
        assert res < 0.97

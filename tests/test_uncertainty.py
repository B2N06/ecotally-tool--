import unittest

from ecotally.uncertainty import bootstrap_diversity


class UncertaintyTests(unittest.TestCase):
    def test_reproducible_intervals_contain_ordered_bounds(self):
        first = bootstrap_diversity([8, 4, 2], replicates=50, seed=42)
        second = bootstrap_diversity([8, 4, 2], replicates=50, seed=42)
        self.assertEqual(first, second)
        for interval in first.values():
            self.assertLessEqual(interval["lower"], interval["upper"])

    def test_even_single_species_is_stable(self):
        result = bootstrap_diversity([10], replicates=20)
        self.assertEqual(
            result["richness"],
            {"estimate": 1.0, "lower": 1.0, "upper": 1.0},
        )

    def test_invalid_parameters(self):
        for kwargs in (
            {"replicates": 9},
            {"confidence": 1},
            {"confidence": 0},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    bootstrap_diversity([2, 1], **kwargs)
        with self.assertRaises(ValueError):
            bootstrap_diversity([1.5, 2])


if __name__ == "__main__":
    unittest.main()

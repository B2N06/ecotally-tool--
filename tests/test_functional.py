import unittest

from ecotally.functional import calculate_functional_diversity


class FunctionalTests(unittest.TestCase):
    def test_weighted_traits_and_distances(self):
        result = calculate_functional_diversity(
            {"oak": 3, "fern": 1},
            {
                "oak": {"height": 10, "leaf_area": 4},
                "fern": {"height": 2, "leaf_area": 4},
            },
        )
        self.assertEqual(result.trait_coverage, 1)
        self.assertEqual(result.community_weighted_means["height"], 8)
        self.assertEqual(result.community_weighted_means["leaf_area"], 4)
        self.assertEqual(result.functional_dispersion, 3)
        self.assertEqual(result.rao_q, 3)

    def test_partial_trait_coverage(self):
        result = calculate_functional_diversity(
            {"oak": 3, "unknown": 1},
            {"oak": {"height": 10}},
        )
        self.assertEqual(result.trait_coverage, 0.75)
        self.assertEqual(result.functional_dispersion, 0)

    def test_requires_usable_consistent_traits(self):
        with self.assertRaises(ValueError):
            calculate_functional_diversity({"oak": 1}, {})
        with self.assertRaises(ValueError):
            calculate_functional_diversity(
                {"oak": 1, "fern": 1},
                {"oak": {"height": 1}, "fern": {"mass": 2}},
            )


if __name__ == "__main__":
    unittest.main()

import unittest

from ecotally.beta import compare_communities


class BetaDiversityTests(unittest.TestCase):
    def test_identical_communities_have_zero_dissimilarity(self):
        result = compare_communities({"oak": 2, "fern": 3}, {"oak": 2, "fern": 3})
        self.assertEqual(result.jaccard_dissimilarity, 0)
        self.assertEqual(result.sorensen_dissimilarity, 0)
        self.assertEqual(result.sorensen_turnover, 0)
        self.assertEqual(result.sorensen_nestedness, 0)
        self.assertEqual(result.bray_curtis_dissimilarity, 0)
        self.assertEqual(result.shared_species, 2)
        self.assertEqual(result.unique_to_first, 0)
        self.assertEqual(result.unique_to_second, 0)

    def test_disjoint_communities_have_complete_dissimilarity(self):
        result = compare_communities({"oak": 2}, {"reed": 8})
        self.assertEqual(result.jaccard_dissimilarity, 1)
        self.assertEqual(result.sorensen_dissimilarity, 1)
        self.assertEqual(result.sorensen_turnover, 1)
        self.assertEqual(result.sorensen_nestedness, 0)
        self.assertEqual(result.bray_curtis_dissimilarity, 1)
        self.assertEqual(result.unique_to_first, 1)
        self.assertEqual(result.unique_to_second, 1)

    def test_partial_overlap(self):
        result = compare_communities({"oak": 3, "fern": 1}, {"oak": 1, "reed": 2})
        self.assertAlmostEqual(result.jaccard_dissimilarity, 2 / 3)
        self.assertAlmostEqual(result.sorensen_dissimilarity, 0.5)
        self.assertAlmostEqual(result.sorensen_turnover, 0.5)
        self.assertAlmostEqual(result.sorensen_nestedness, 0)
        self.assertAlmostEqual(result.bray_curtis_dissimilarity, 5 / 7)

    def test_nested_subset_has_nestedness_but_no_turnover(self):
        result = compare_communities({"oak": 2}, {"oak": 1, "fern": 1})
        self.assertAlmostEqual(result.sorensen_dissimilarity, 1 / 3)
        self.assertEqual(result.sorensen_turnover, 0)
        self.assertAlmostEqual(result.sorensen_nestedness, 1 / 3)
        self.assertAlmostEqual(
            result.sorensen_turnover + result.sorensen_nestedness,
            result.sorensen_dissimilarity,
        )

    def test_balanced_unique_species_has_exact_zero_nestedness(self):
        result = compare_communities(
            {"shared-a": 1, "shared-b": 1, "only-a": 1},
            {"shared-a": 1, "shared-b": 1, "only-b": 1},
        )
        self.assertEqual(result.sorensen_nestedness, 0)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            compare_communities({"oak": -1}, {"reed": 1})
        with self.assertRaises(ValueError):
            compare_communities({}, {})


if __name__ == "__main__":
    unittest.main()

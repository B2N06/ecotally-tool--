import math
import unittest

from ecotally.diversity import calculate_diversity


class DiversityTests(unittest.TestCase):
    def test_equal_community(self):
        result = calculate_diversity([10, 10, 10, 10])
        self.assertEqual(result.richness, 4)
        self.assertEqual(result.total_abundance, 40)
        self.assertAlmostEqual(result.shannon, math.log(4))
        self.assertAlmostEqual(result.simpson, 0.75)
        self.assertAlmostEqual(result.pielou_evenness, 1.0)
        self.assertAlmostEqual(result.hill_q1, 4.0)

    def test_zeros_do_not_count_as_species(self):
        result = calculate_diversity([0, 3, 0])
        self.assertEqual(result.richness, 1)
        self.assertEqual(result.pielou_evenness, 1.0)

    def test_invalid_abundances(self):
        for values in ([], [0, 0], [1, -1], [float("nan")], [float("inf")]):
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    calculate_diversity(values)


if __name__ == "__main__":
    unittest.main()

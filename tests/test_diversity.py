import math
import unittest

from ecotally.diversity import calculate_diversity, hill_number


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

    def test_generalized_hill_numbers(self):
        abundances = [4, 4, 4, 4]
        for order in (0, 0.5, 1, 2, 3):
            with self.subTest(order=order):
                self.assertAlmostEqual(hill_number(abundances, order), 4)
        self.assertAlmostEqual(
            hill_number([3, 1], 0.5),
            ((3 / 4) ** 0.5 + (1 / 4) ** 0.5) ** 2,
        )

    def test_invalid_hill_order(self):
        with self.assertRaises(ValueError):
            hill_number([1, 2], -1)


if __name__ == "__main__":
    unittest.main()

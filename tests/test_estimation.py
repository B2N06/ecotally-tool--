import unittest

from ecotally.estimation import (
    estimate_richness,
    expected_richness,
    rarefaction_curve,
)


class EstimationTests(unittest.TestCase):
    def test_chao1_and_coverage(self):
        result = estimate_richness([1, 1, 2, 5])
        self.assertEqual(result.observed_richness, 4)
        self.assertAlmostEqual(result.chao1_richness, 4.5)
        self.assertAlmostEqual(result.sample_coverage, 7 / 9)
        self.assertEqual(result.singletons, 2)
        self.assertEqual(result.doubletons, 1)

    def test_rarefaction_endpoints(self):
        abundances = [2, 2, 1]
        self.assertAlmostEqual(expected_richness(abundances, 1), 1)
        self.assertAlmostEqual(expected_richness(abundances, 5), 3)
        curve = rarefaction_curve(abundances, points=3)
        self.assertEqual(curve[0], {"sample_size": 1, "expected_richness": 1.0})
        self.assertEqual(curve[-1], {"sample_size": 5, "expected_richness": 3.0})

    def test_rejects_continuous_and_invalid_counts(self):
        for values in ([1.5, 2], [-1, 2], [float("inf")], [0, 0]):
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    estimate_richness(values)
        with self.assertRaises(ValueError):
            rarefaction_curve([1, 2], points=1)


if __name__ == "__main__":
    unittest.main()

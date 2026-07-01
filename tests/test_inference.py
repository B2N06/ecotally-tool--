import unittest

from ecotally.inference import permutation_group_difference


class InferenceTests(unittest.TestCase):
    def test_group_test_is_reproducible_and_directional(self):
        values = {"a1": 1, "a2": 2, "b1": 8, "b2": 9}
        groups = {"a1": "control", "a2": "control", "b1": "restored", "b2": "restored"}
        first = permutation_group_difference(
            values, groups, metric="richness", permutations=100, seed=42
        )
        second = permutation_group_difference(
            values, groups, metric="richness", permutations=100, seed=42
        )
        self.assertEqual(first, second)
        self.assertEqual(first["group_a"], "control")
        self.assertEqual(first["group_b"], "restored")
        self.assertEqual(first["difference_b_minus_a"], 7)
        self.assertTrue(0 < first["p_value"] <= 1)

    def test_group_test_requires_exactly_two_groups(self):
        with self.assertRaises(ValueError):
            permutation_group_difference(
                {"a": 1}, {"a": "only"}, metric="shannon", permutations=10
            )
        with self.assertRaises(ValueError):
            permutation_group_difference(
                {"a": 1, "b": 2, "c": 3},
                {"a": "one", "b": "two", "c": "three"},
                metric="shannon",
                permutations=10,
            )


if __name__ == "__main__":
    unittest.main()

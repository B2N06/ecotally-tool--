import unittest

from ecotally.contribution import beta_contributions, lcbd_significance


class ContributionTests(unittest.TestCase):
    def test_contributions_sum_to_one(self):
        result = beta_contributions(
            {
                "forest": {"oak": 8, "fern": 2},
                "marsh": {"oak": 1, "reed": 9},
                "edge": {"oak": 5, "fern": 3, "reed": 2},
            }
        )
        self.assertAlmostEqual(sum(row["lcbd"] for row in result["lcbd"]), 1)
        self.assertAlmostEqual(sum(row["scbd"] for row in result["scbd"]), 1)
        self.assertEqual(
            {row["site"] for row in result["lcbd"]},
            {"forest", "marsh", "edge"},
        )

    def test_identical_sites_have_zero_contributions(self):
        result = beta_contributions({"a": {"oak": 2}, "b": {"oak": 8}})
        self.assertEqual([row["lcbd"] for row in result["lcbd"]], [0, 0])
        self.assertEqual(result["scbd"][0]["scbd"], 0)

    def test_empty_sites_are_omitted(self):
        result = beta_contributions(
            {"empty": {"oak": 0}, "forest": {"oak": 2}}
        )
        self.assertEqual(result["lcbd"], [{"site": "forest", "lcbd": 0.0}])

    def test_lcbd_permutation_test_is_reproducible(self):
        communities = {
            "forest": {"oak": 9, "reed": 1},
            "marsh": {"oak": 1, "reed": 9},
            "edge": {"oak": 5, "reed": 5},
        }
        first = lcbd_significance(communities, permutations=50, seed=42)
        second = lcbd_significance(communities, permutations=50, seed=42)
        self.assertEqual(first, second)
        self.assertTrue(all(0 < row["p_value"] <= 1 for row in first))
        self.assertTrue(all(row["permutations"] == 50 for row in first))

    def test_lcbd_permutation_count_is_validated(self):
        with self.assertRaises(ValueError):
            lcbd_significance({"forest": {"oak": 1}}, permutations=9)

    def test_symmetric_two_site_lcbd_is_not_split_by_float_noise(self):
        result = lcbd_significance(
            {
                "a": {"oak": 9, "reed": 1},
                "b": {"oak": 1, "reed": 9},
            },
            permutations=20,
        )
        self.assertEqual([row["p_value"] for row in result], [1, 1])


if __name__ == "__main__":
    unittest.main()

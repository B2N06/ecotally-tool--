import unittest

from ecotally.contribution import beta_contributions


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


if __name__ == "__main__":
    unittest.main()

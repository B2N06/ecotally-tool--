import unittest

from ecotally.quality import audit_communities


class QualityTests(unittest.TestCase):
    def test_empty_site_and_zero_species(self):
        issues = audit_communities(
            {"empty": {"oak": 0, "ghost": 0}, "forest": {"oak": 2, "ghost": 0}}
        )
        codes = {issue.code for issue in issues}
        self.assertIn("empty_site", codes)
        self.assertIn("unobserved_species", codes)

    def test_sampling_imbalance(self):
        issues = audit_communities({"small": {"oak": 1}, "large": {"oak": 10}})
        self.assertIn("sampling_imbalance", {issue.code for issue in issues})

    def test_balanced_dataset_has_no_warning(self):
        issues = audit_communities({"a": {"oak": 5}, "b": {"oak": 8}})
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()

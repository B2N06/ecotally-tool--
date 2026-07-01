import unittest

from ecotally.summary import summarize_dataset, summarize_species


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.communities = {
            "forest": {"oak": 4, "fern": 2, "reed": 0},
            "marsh": {"oak": 1, "reed": 5},
        }

    def test_dataset_partition(self):
        result = summarize_dataset(self.communities)
        self.assertEqual(result.site_count, 2)
        self.assertEqual(result.gamma_richness, 3)
        self.assertEqual(result.mean_alpha_richness, 2)
        self.assertEqual(result.whittaker_beta, 1.5)
        self.assertEqual(result.total_abundance, 12)

    def test_species_occupancy(self):
        rows = summarize_species(self.communities)
        oak = next(row for row in rows if row["species"] == "oak")
        fern = next(row for row in rows if row["species"] == "fern")
        self.assertEqual(oak["occupancy"], 1)
        self.assertEqual(oak["total_abundance"], 5)
        self.assertEqual(fern["occupancy"], 0.5)

    def test_empty_dataset_is_rejected(self):
        with self.assertRaises(ValueError):
            summarize_dataset({})


if __name__ == "__main__":
    unittest.main()

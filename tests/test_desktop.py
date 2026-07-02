import tempfile
import unittest
from pathlib import Path

from ecotally.desktop import (
    COLORS,
    EcoTallyDesktop,
    analysis_options,
    plain_language_summary,
    preview_tabular_file,
)


class DesktopLogicTests(unittest.TestCase):
    def test_analysis_start_ignores_duplicate_click(self):
        app = EcoTallyDesktop.__new__(EcoTallyDesktop)
        app.analysis_running = True
        app.start_analysis()

    def test_selected_file_state_is_visually_distinct(self):
        self.assertNotEqual(COLORS["background"], COLORS["surface"])
        self.assertNotEqual(COLORS["background"], COLORS["surface_selected"])
        self.assertNotEqual(COLORS["surface"], COLORS["surface_selected"])
        self.assertNotEqual(COLORS["line"], COLORS["line_strong"])

    def test_preview_supports_detected_delimiters(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        source = Path(directory.name) / "data.tsv"
        source.write_text(
            "site\tspecies\tabundance\nforest\toak\t3\n",
            encoding="utf-8",
        )
        headers, rows = preview_tabular_file(source)
        self.assertEqual(headers, ["site", "species", "abundance"])
        self.assertEqual(rows, [["forest", "oak", "3"]])

    def test_student_choices_map_to_reproducible_parameters(self):
        options = analysis_options(
            sampling=True,
            uncertainty=True,
            hill_profile=True,
            traits_path="traits.csv",
        )
        self.assertEqual(options["bootstrap"], 200)
        self.assertEqual(options["rarefaction"], 12)
        self.assertEqual(options["hill_orders"], [0, 0.5, 1, 2, 3])
        self.assertTrue(options["standardize_trait_values"])

    def test_plain_language_summary(self):
        report = {
            "sites": [
                {
                    "site": "core",
                    "richness": 3,
                    "pielou_evenness": 0.6,
                    "shannon": 0.8,
                },
                {
                    "site": "edge",
                    "richness": 4,
                    "pielou_evenness": 0.9,
                    "shannon": 1.2,
                },
            ]
        }
        summary = plain_language_summary(report)
        self.assertIn("edge 的物种丰富度最高", summary)
        self.assertIn("edge 的个体分布最均匀", summary)

    def test_plain_language_summary_reports_equal_richness(self):
        report = {
            "sites": [
                {
                    "site": "core",
                    "richness": 3,
                    "pielou_evenness": 0.6,
                    "shannon": 0.8,
                },
                {
                    "site": "edge",
                    "richness": 3,
                    "pielou_evenness": 0.9,
                    "shannon": 1.2,
                },
            ]
        }
        summary = plain_language_summary(report)
        self.assertIn("各样方物种丰富度相同（均为 3 种）", summary)
        self.assertNotIn("core 的物种丰富度最高", summary)

    def test_plain_language_summary_reports_tied_leaders(self):
        report = {
            "sites": [
                {
                    "site": "north",
                    "richness": 5,
                    "pielou_evenness": 0.8,
                    "shannon": 1.1,
                },
                {
                    "site": "south",
                    "richness": 5,
                    "pielou_evenness": 0.8,
                    "shannon": 1.0,
                },
                {
                    "site": "west",
                    "richness": 3,
                    "pielou_evenness": 0.5,
                    "shannon": 0.7,
                },
            ]
        }
        summary = plain_language_summary(report)
        self.assertIn("north、south 的物种丰富度并列最高", summary)
        self.assertIn("north、south 的个体分布并列最均匀", summary)


if __name__ == "__main__":
    unittest.main()

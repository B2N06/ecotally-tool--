import csv
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from ecotally import __version__
from ecotally.cli import main, render_markdown, render_matrix
from ecotally.io import (
    read_communities_csv,
    read_long_csv,
    read_traits_csv,
    read_wide_csv,
)


class IoAndCliTests(unittest.TestCase):
    def write_csv(self, rows, headers=("site", "species", "abundance")):
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "observations.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        self.addCleanup(directory.cleanup)
        return path

    def test_reader_combines_duplicate_observations(self):
        path = self.write_csv(
            [
                {"site": "wetland", "species": "reed", "abundance": 2},
                {"site": "wetland", "species": "reed", "abundance": 3},
            ]
        )
        self.assertEqual(read_long_csv(path), {"wetland": {"reed": 5.0}})

    def test_reader_reports_line_number(self):
        path = self.write_csv(
            [{"site": "wetland", "species": "reed", "abundance": "many"}]
        )
        with self.assertRaisesRegex(ValueError, "line 2"):
            read_long_csv(path)

    def test_reader_requires_standard_columns(self):
        path = self.write_csv([], headers=("plot", "taxon", "count"))
        with self.assertRaisesRegex(ValueError, "missing CSV columns"):
            read_long_csv(path)

    def test_wide_reader_and_auto_detection(self):
        path = self.write_csv(
            [
                {"site": "marsh", "reed": 8, "sedge": 3},
                {"site": "pond", "reed": 1, "sedge": 5},
            ],
            headers=("site", "reed", "sedge"),
        )
        expected = {
            "marsh": {"reed": 8.0, "sedge": 3.0},
            "pond": {"reed": 1.0, "sedge": 5.0},
        }
        self.assertEqual(read_wide_csv(path), expected)
        self.assertEqual(read_communities_csv(path), expected)

    def test_wide_reader_rejects_duplicate_sites(self):
        path = self.write_csv(
            [
                {"site": "marsh", "reed": 8},
                {"site": "marsh", "reed": 2},
            ],
            headers=("site", "reed"),
        )
        with self.assertRaisesRegex(ValueError, "duplicate site"):
            read_wide_csv(path)

    def test_trait_reader(self):
        path = self.write_csv(
            [{"species": "oak", "height": 10, "mass": 4}],
            headers=("species", "height", "mass"),
        )
        self.assertEqual(
            read_traits_csv(path),
            {"oak": {"height": 10.0, "mass": 4.0}},
        )

    def test_json_cli_output(self):
        path = self.write_csv(
            [
                {"site": "forest", "species": "oak", "abundance": 4},
                {"site": "forest", "species": "fern", "abundance": 4},
            ]
        )
        output = StringIO()
        with redirect_stdout(output):
            code = main([str(path), "--format", "json"])
        self.assertEqual(code, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["sites"][0]["site"], "forest")
        self.assertEqual(payload["sites"][0]["richness"], 2)
        self.assertEqual(payload["sites"][0]["sample_coverage"], 1)
        self.assertEqual(payload["pairwise"], [])
        self.assertEqual(payload["dataset"][0]["gamma_richness"], 2)
        self.assertEqual(len(payload["species"]), 2)
        self.assertEqual(payload["metadata"][0]["ecotally_version"], __version__)
        self.assertEqual(len(payload["metadata"][0]["source_sha256"]), 64)

    def test_json_report_contains_pairwise_comparison(self):
        path = self.write_csv(
            [
                {"site": "a", "species": "oak", "abundance": 2},
                {"site": "b", "species": "reed", "abundance": 2},
            ]
        )
        output = StringIO()
        with redirect_stdout(output):
            code = main([str(path), "--format", "json"])
        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["pairwise"][0]["jaccard_dissimilarity"], 1)

    def test_cli_failure_has_nonzero_exit(self):
        errors = StringIO()
        with redirect_stderr(errors):
            code = main(["missing.csv"])
        self.assertEqual(code, 2)
        self.assertIn("error", errors.getvalue())

    def test_markdown_report(self):
        report = {
            "sites": [{"site": "marsh", "shannon": 0.123456}],
            "pairwise": [],
        }
        content = render_markdown(report)
        self.assertIn("# EcoTally biodiversity report", content)
        self.assertIn("| marsh | 0.1235 |", content)
        self.assertIn("No comparisons available", content)

    def test_square_dissimilarity_matrix(self):
        report = {
            "sites": [{"site": "b"}, {"site": "a"}],
            "pairwise": [
                {
                    "site_a": "a",
                    "site_b": "b",
                    "bray_curtis_dissimilarity": 0.25,
                }
            ],
        }
        content = render_matrix(report, "bray_curtis")
        self.assertEqual(
            content.splitlines(),
            ["site,a,b", "a,0.0,0.25", "b,0.25,0.0"],
        )

    def test_empty_site_is_reported_instead_of_crashing(self):
        path = self.write_csv(
            [
                {"site": "empty", "oak": 0},
                {"site": "forest", "oak": 3},
            ],
            headers=("site", "oak"),
        )
        output = StringIO()
        with redirect_stdout(output):
            code = main([str(path), "--format", "json"])
        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["sites"][0]["status"], "empty")
        self.assertEqual(payload["quality"][0]["code"], "empty_site")

    def test_cli_bootstrap_report(self):
        path = self.write_csv(
            [
                {"site": "forest", "species": "oak", "abundance": 4},
                {"site": "forest", "species": "fern", "abundance": 2},
            ]
        )
        output = StringIO()
        with redirect_stdout(output):
            code = main([str(path), "--format", "json", "--bootstrap", "10"])
        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(len(payload["uncertainty"]), 4)

    def test_cli_rarefaction_and_standardization(self):
        path = self.write_csv(
            [
                {"site": "a", "species": "oak", "abundance": 4},
                {"site": "a", "species": "fern", "abundance": 2},
                {"site": "b", "species": "oak", "abundance": 2},
                {"site": "b", "species": "fern", "abundance": 2},
            ]
        )
        output = StringIO()
        with redirect_stdout(output):
            code = main([str(path), "--format", "json", "--rarefaction", "3"])
        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["dataset"][0]["standardized_sample_size"], 4)
        self.assertEqual(len(payload["rarefaction"]), 6)

    def test_cli_functional_diversity(self):
        observations = self.write_csv(
            [
                {"site": "forest", "species": "oak", "abundance": 3},
                {"site": "forest", "species": "fern", "abundance": 1},
            ]
        )
        traits = self.write_csv(
            [
                {"species": "oak", "height": 10},
                {"species": "fern", "height": 2},
            ],
            headers=("species", "height"),
        )
        output = StringIO()
        with redirect_stdout(output):
            code = main(
                [
                    str(observations),
                    "--format",
                    "json",
                    "--traits",
                    str(traits),
                    "--standardize-traits",
                ]
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(len(payload["functional"]), 4)

    def test_cli_hill_profile(self):
        path = self.write_csv(
            [
                {"site": "forest", "species": "oak", "abundance": 3},
                {"site": "forest", "species": "fern", "abundance": 1},
            ]
        )
        output = StringIO()
        with redirect_stdout(output):
            code = main(
                [str(path), "--format", "json", "--hill-orders", "0,0.5,1,2"]
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(len(payload["hill_profile"]), 4)
        self.assertEqual(payload["hill_profile"][0]["diversity"], 2)


if __name__ == "__main__":
    unittest.main()

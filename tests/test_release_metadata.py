import re
import unittest
from pathlib import Path

from ecotally import __version__


ROOT = Path(__file__).parents[1]


class ReleaseMetadataTests(unittest.TestCase):
    def test_version_is_consistent_across_release_files(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        self.assertIn(f'version = "{__version__}"', pyproject)
        self.assertRegex(citation, rf"(?m)^version: {re.escape(__version__)}$")

    def test_primary_documentation_links_exist(self):
        for name in (
            "README.md",
            "README.zh-CN.md",
            "METHODOLOGY.md",
            "CONTRIBUTING.md",
            "LICENSE",
            "SECURITY.md",
        ):
            with self.subTest(name=name):
                self.assertTrue((ROOT / name).is_file())

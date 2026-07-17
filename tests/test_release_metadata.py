import ast
import re
import unittest
from pathlib import Path

from ecotally import __version__


ROOT = Path(__file__).parents[1]


class ReleaseMetadataTests(unittest.TestCase):
    def test_version_is_consistent_across_release_files(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        windows_info = (
            ROOT / "packaging/windows_version_info.txt"
        ).read_text(encoding="utf-8")
        self.assertIn(f'version = "{__version__}"', pyproject)
        self.assertRegex(citation, rf"(?m)^version: {re.escape(__version__)}$")
        self.assertIn(f"StringStruct('FileVersion', '{__version__}')", windows_info)
        self.assertIn(f"StringStruct('ProductVersion', '{__version__}')", windows_info)

    def test_desktop_source_has_no_network_imports(self):
        prohibited = {
            "aiohttp",
            "http",
            "requests",
            "socket",
            "ssl",
            "urllib",
            "webbrowser",
            "websockets",
        }
        found = []
        for source in (ROOT / "src/ecotally").glob("*.py"):
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [alias.name.split(".", 1)[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module.split(".", 1)[0]]
                else:
                    continue
                found.extend(
                    (source.name, name) for name in names if name in prohibited
                )
        self.assertEqual(found, [])

    def test_primary_documentation_links_exist(self):
        for name in (
            "README.md",
            "README.zh-CN.md",
            "METHODOLOGY.md",
            "CONTRIBUTING.md",
            "LICENSE",
            "SECURITY.md",
            "WINDOWS_SECURITY.md",
            "RELEASE_NOTES.md",
            "ROADMAP.md",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/pull_request_template.md",
            ".github/workflows/windows-build.yml",
            "packaging/windows_version_info.txt",
        ):
            with self.subTest(name=name):
                self.assertTrue((ROOT / name).is_file())

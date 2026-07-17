import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import desktop_entry


class DesktopEntryTests(unittest.TestCase):
    def test_packaged_self_test_exercises_two_sites(self):
        self.assertEqual(desktop_entry._self_test(), 0)

    def test_main_routes_self_test_without_starting_gui(self):
        with patch.object(desktop_entry, "_self_test", return_value=0) as check:
            with patch.object(
                desktop_entry.sys,
                "argv",
                ["EcoTally.exe", "--self-test"],
            ):
                self.assertEqual(desktop_entry._main(), 0)
        check.assert_called_once_with()

    def test_self_test_does_not_leave_source_files(self):
        original = set(Path(tempfile.gettempdir()).glob("ecotally-self-test-*"))
        desktop_entry._self_test()
        current = set(Path(tempfile.gettempdir()).glob("ecotally-self-test-*"))
        self.assertEqual(current, original)


if __name__ == "__main__":
    unittest.main()

import unittest
import xml.etree.ElementTree as ET

from ecotally.svg import render_diversity_svg


class SvgTests(unittest.TestCase):
    def test_svg_is_valid_accessible_xml_and_escapes_site_names(self):
        content = render_diversity_svg(
            {
                "sites": [
                    {"site": "forest & edge", "richness": 3, "shannon": 1.2},
                    {"site": "marsh", "richness": 2, "shannon": 0.8},
                ]
            }
        )
        root = ET.fromstring(content)
        self.assertTrue(root.tag.endswith("svg"))
        self.assertEqual(root.attrib["role"], "img")
        self.assertIn("forest &amp; edge", content)
        self.assertIn("Species richness", content)

    def test_empty_data_is_rejected(self):
        with self.assertRaises(ValueError):
            render_diversity_svg({"sites": [{"site": "empty", "status": "empty"}]})


if __name__ == "__main__":
    unittest.main()

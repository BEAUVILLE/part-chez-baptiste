import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

class SitemapTest(unittest.TestCase):
 def test_sitemap(self):
  root=Path(__file__).resolve().parents[1]
  doc=ET.parse(root/'sitemap.xml').getroot()
  locs=[e.text for e in doc.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
  self.assertEqual(locs,['https://part-chez-baptiste.digiylyfe.com/'])

"""Regression: 10 languages on Saly rental without changing reservation, pricing or owner flows."""
import json, re, subprocess, shutil, unittest
from pathlib import Path
S=(Path(__file__).resolve().parents[1]/"index.html").read_text(encoding="utf-8")
LANGS={"fr","en","es","pt","it","de","nl","ar","wo","zh"}
class TestLanguages(unittest.TestCase):
 def test_translations(self):
  m=re.search(r'const translations = \{\s*wo:(\{.*?\}),\s*zh:(\{.*?\}),\s*fr:',S,re.S)
  self.assertIsNotNone(m)
  wo,zh=json.loads(m.group(1)),json.loads(m.group(2))
  self.assertEqual(set(wo),set(zh))
  self.assertEqual(len(wo),65)
  self.assertTrue(all(v for v in wo.values()))
  self.assertIn('30 000 FCFA',wo["moreBody"])
  self.assertIn('30,000',zh["moreBody"])
  self.assertIn('550 000 FCFA',wo["moreBody"])
  self.assertIn('550,000',zh["moreBody"])
 def test_buttons(self):
  b=re.findall(r'<button[^>]+data-lang="([^"]+)"',S)
  self.assertEqual(set(b),LANGS)
  self.assertIn('lang="wo"',S)
  self.assertIn('lang="zh-CN"',S)
  self.assertIn("const SUPPORTED_LANGS=['fr','en','es','pt','de','it','nl','ar','wo','zh']",S)
  self.assertIn('document.documentElement.lang=lang==="zh"?"zh-CN":lang',S)
 def test_calendar_and_price_source_unchanged(self):
  for item in ('loadMasterCalendar()','renderAvailabilityOverview()','updateWhatsApp()','applyLanguage(saved)','chezBaptisteLang','0 % commission DIGIY','550 000 FCFA','175 000 FCFA'):
   self.assertIn(item,S)
  self.assertIn('history.replaceState',S)
 @unittest.skipUnless(shutil.which("node"),"Node unavailable")
 def test_script_syntax(self):
  chunks=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',S,re.S)
  for code in chunks:
   if 'const translations = {' not in code:continue
   p=subprocess.run(["node","--check"],input=code,text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stderr)
if __name__=="__main__":unittest.main()

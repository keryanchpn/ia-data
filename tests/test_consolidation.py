import tempfile
import unittest
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd


class ConsolidationTest(unittest.TestCase):
    def test_module_imports_from_project_root(self):
        project_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "-c", "import src.consolidation"],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_write_consolidated_csv_replaces_previous_output(self):
        from src import consolidation

        bulletin = {
            "id_anssi": "CERTFR-2026-AVI-0001",
            "titre": "Bulletin test",
            "type_bulletin": "Avis",
            "date_publication": "Thu, 18 Jun 2026 00:00:00 +0000",
            "lien": "https://www.cert.ssi.gouv.fr/avis/CERTFR-2026-AVI-0001/",
        }
        cve_info = {
            "cve_id": "CVE-2026-0001",
            "description": "Description test",
            "cvss_score": 9.1,
            "base_severity": "CRITICAL",
            "cwe": "CWE-79",
            "cwe_desc": "Cross-site Scripting",
            "epss_score": 0.7,
            "produits": [{"vendor": "Vendor", "product": "Product", "versions": ["1.0"]}],
        }

        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "vulnerabilites_anssi.csv"
            output_path.write_text("old,data\nstale,row\n", encoding="utf-8")

            with patch.object(consolidation, "extract_cves_from_bulletin", return_value=["CVE-2026-0001"]), \
                    patch.object(consolidation, "enrich_cve", return_value=cve_info):
                df = consolidation.write_consolidated_csv(
                    [bulletin], output_path, verbose=False, use_cache=True, refresh_cache=False
                )

            saved = pd.read_csv(output_path)
            self.assertEqual(len(df), 1)
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved.loc[0, "cve"], "CVE-2026-0001")
            self.assertNotIn("old", saved.columns)

    def test_write_consolidated_csv_normalizes_text_and_removes_duplicates(self):
        from src import consolidation

        bulletins = [
            {
                "id_anssi": "CERTFR-2026-AVI-0001",
                "titre": "Bulletin\ntest",
                "type_bulletin": "Avis",
                "date_publication": "Thu, 18 Jun 2026 00:00:00 +0000",
                "lien": "https://www.cert.ssi.gouv.fr/avis/CERTFR-2026-AVI-0001/",
            }
        ]
        cve_info = {
            "cve_id": "CVE-2026-0001",
            "description": "Description\r\nmulti ligne",
            "cvss_score": 9.1,
            "base_severity": "CRITICAL",
            "cwe": "CWE-79",
            "cwe_desc": "Cross-site Scripting",
            "epss_score": 0.7,
            "produits": [{"vendor": "Vendor", "product": "Product", "versions": ["1.0"]}],
        }

        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "vulnerabilites_anssi.csv"

            with patch.object(consolidation, "extract_cves_from_bulletin", return_value=["CVE-2026-0001", "CVE-2026-0001"]), \
                    patch.object(consolidation, "enrich_cve", return_value=cve_info):
                df = consolidation.write_consolidated_csv([bulletins[0]], output_path, verbose=False)

            content = output_path.read_text(encoding="utf-8")
            saved = pd.read_csv(output_path)

        self.assertEqual(len(df), 1)
        self.assertEqual(len(saved), 1)
        self.assertNotIn("\r\n", content)
        self.assertEqual(saved.loc[0, "titre_anssi"], "Bulletin test")
        self.assertEqual(saved.loc[0, "description"], "Description multi ligne")


if __name__ == "__main__":
    unittest.main()

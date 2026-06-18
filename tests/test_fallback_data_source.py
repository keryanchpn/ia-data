import json
import tempfile
import unittest
from pathlib import Path


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


class FallbackDataSourceTest(unittest.TestCase):
    def test_extracts_bulletins_from_fallback_directory(self):
        from src.rss_extraction import extract_all_bulletins

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "avis" / "CERTFR-2026-AVI-0001",
                {
                    "reference": "CERTFR-2026-AVI-0001",
                    "title": "Avis local",
                    "summary": "Resume local",
                    "revisions": [{"revision_date": "2026-06-18T00:00:00.000000"}],
                },
            )
            write_json(
                root / "alertes" / "CERTFR-2026-ALE-0002.json",
                {
                    "reference": "CERTFR-2026-ALE-0002",
                    "title": "Alerte locale",
                    "revisions": [{"revision_date": "2026-06-19T00:00:00.000000"}],
                },
            )

            bulletins = extract_all_bulletins(data_source="fallback", fallback_root=root)

        self.assertEqual([b["id_anssi"] for b in bulletins], ["CERTFR-2026-AVI-0001", "CERTFR-2026-ALE-0002"])
        self.assertEqual([b["type_bulletin"] for b in bulletins], ["Avis", "Alerte"])
        self.assertEqual(bulletins[0]["lien"], "https://www.cert.ssi.gouv.fr/avis/CERTFR-2026-AVI-0001/")

    def test_extracts_bulletins_from_nested_data_directory_with_capitalized_avis(self):
        from src.rss_extraction import extract_all_bulletins

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "data" / "Avis" / "CERTFR-2026-AVI-0001",
                {
                    "reference": "CERTFR-2026-AVI-0001",
                    "title": "Avis local",
                    "revisions": [{"revision_date": "2026-06-18T00:00:00.000000"}],
                },
            )
            write_json(
                root / "data" / "alertes" / "CERTFR-2026-ALE-0002",
                {
                    "reference": "CERTFR-2026-ALE-0002",
                    "title": "Alerte locale",
                    "revisions": [{"revision_date": "2026-06-19T00:00:00.000000"}],
                },
            )

            bulletins = extract_all_bulletins(data_source="fallback", fallback_root=root)

        self.assertEqual([b["id_anssi"] for b in bulletins], ["CERTFR-2026-AVI-0001", "CERTFR-2026-ALE-0002"])

    def test_extracts_cves_from_fallback_bulletin_json(self):
        from src.cve_extraction import extract_cves_from_bulletin

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "avis" / "CERTFR-2026-AVI-0001.json",
                {
                    "cves": [{"name": "CVE-2026-0001"}],
                    "content": "Mention supplementaire CVE-2026-0002",
                },
            )

            cves = extract_cves_from_bulletin(
                "https://www.cert.ssi.gouv.fr/avis/CERTFR-2026-AVI-0001/",
                data_source="fallback",
                fallback_root=root,
            )

        self.assertEqual(cves, ["CVE-2026-0001", "CVE-2026-0002"])

    def test_builds_dataframe_with_fallback_mitre_and_first_data(self):
        from src.consolidation import build_dataframe

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(root / "avis" / "CERTFR-2026-AVI-0001", {"cves": [{"name": "CVE-2026-0001"}]})
            write_json(
                root / "mitre" / "CVE-2026-0001",
                {
                    "containers": {
                        "cna": {
                            "descriptions": [{"value": "Description locale"}],
                            "metrics": [{"cvssV3_1": {"baseScore": 9.1, "baseSeverity": "CRITICAL"}}],
                            "problemTypes": [{"descriptions": [{"cweId": "CWE-79", "description": "XSS"}]}],
                            "affected": [
                                {
                                    "vendor": "Vendor",
                                    "product": "Product",
                                    "versions": [{"version": "1.0", "status": "affected"}],
                                }
                            ],
                        }
                    }
                },
            )
            write_json(root / "first" / "CVE-2026-0001.json", {"data": [{"epss": "0.42"}]})
            bulletins = [
                {
                    "id_anssi": "CERTFR-2026-AVI-0001",
                    "titre": "Avis local",
                    "type_bulletin": "Avis",
                    "date_publication": "2026-06-18T00:00:00.000000",
                    "lien": "https://www.cert.ssi.gouv.fr/avis/CERTFR-2026-AVI-0001/",
                }
            ]

            df = build_dataframe(
                bulletins,
                verbose=False,
                data_source="fallback",
                fallback_root=root,
            )

        self.assertEqual(len(df), 1)
        self.assertEqual(df.loc[0, "cve"], "CVE-2026-0001")
        self.assertEqual(df.loc[0, "cvss_score"], 9.1)
        self.assertEqual(df.loc[0, "epss_score"], 0.42)
        self.assertEqual(df.loc[0, "produit"], "Product")


if __name__ == "__main__":
    unittest.main()

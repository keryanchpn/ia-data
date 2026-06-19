import json
from pathlib import Path

import pandas as pd


def test_export_presentation_data_builds_chart_json_from_csv(tmp_path):
    from scripts.export_presentation_data import export_presentation_data

    csv_path = tmp_path / "vulnerabilites_anssi.csv"
    output_path = tmp_path / "charts.json"
    rows = [
        {
            "id_anssi": "A-1",
            "titre_anssi": "Avis Microsoft",
            "type_bulletin": "Avis",
            "date_publication": "2026-01-01",
            "cve": "CVE-2026-0001",
            "cvss_score": 9.1,
            "base_severity": "CRITICAL",
            "cwe": "CWE-79",
            "cwe_desc": "XSS",
            "epss_score": 0.75,
            "lien_anssi": "https://example.test/a-1",
            "description": "desc",
            "editeur": "Microsoft",
            "produit": "Windows",
            "versions_affectees": "1",
        },
        {
            "id_anssi": "A-2",
            "titre_anssi": "Avis Apple",
            "type_bulletin": "Avis",
            "date_publication": "2026-01-02",
            "cve": "CVE-2026-0002",
            "cvss_score": 5.4,
            "base_severity": "MEDIUM",
            "cwe": "CWE-89",
            "cwe_desc": "SQLi",
            "epss_score": 0.02,
            "lien_anssi": "https://example.test/a-2",
            "description": "desc",
            "editeur": "Apple",
            "produit": "macOS",
            "versions_affectees": "1",
        },
        {
            "id_anssi": "A-3",
            "titre_anssi": "Avis Microsoft duplicate vendor",
            "type_bulletin": "Avis",
            "date_publication": "2026-01-03",
            "cve": "CVE-2026-0003",
            "cvss_score": 7.8,
            "base_severity": "HIGH",
            "cwe": "CWE-79",
            "cwe_desc": "XSS",
            "epss_score": 0.15,
            "lien_anssi": "https://example.test/a-3",
            "description": "desc",
            "editeur": "Microsoft",
            "produit": "Office",
            "versions_affectees": "1",
        },
    ]
    for index in range(4, 14):
        rows.append(
            {
                "id_anssi": f"A-{index}",
                "titre_anssi": f"Avis Vendor {index}",
                "type_bulletin": "Avis",
                "date_publication": "2026-01-04",
                "cve": f"CVE-2026-{index:04d}",
                "cvss_score": 4.0,
                "base_severity": "LOW",
                "cwe": f"CWE-{index}",
                "cwe_desc": "desc",
                "epss_score": 0.01,
                "lien_anssi": f"https://example.test/a-{index}",
                "description": "desc",
                "editeur": f"Vendor {index}",
                "produit": "Product",
                "versions_affectees": "1",
            }
        )
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    export_presentation_data(csv_path, output_path, run_ml=False)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["meta"]["source_rows"] == 13
    assert payload["cvssDistribution"]["values"]
    assert payload["epssLinear"]["values"]
    assert payload["epssLog"]["values"]
    assert payload["severityDistribution"]["labels"] == ["CRITICAL", "HIGH", "LOW", "MEDIUM"]
    assert payload["severityDistribution"]["values"] == [1, 1, 10, 1]
    assert payload["cweDistribution"]["labels"][:2] == ["CWE-79", "CWE-89"]
    assert payload["cweDistribution"]["values"][:2] == [2, 1]
    assert "Autres" not in payload["cweDistribution"]["labels"]
    assert payload["topVendors"]["labels"][:2] == ["Microsoft", "Apple"]
    assert payload["topVendors"]["values"][:2] == [2, 1]
    assert payload["kmeans"]["points"] == []
    assert payload["knn"]["kValues"] == []

"""Consolidation des données ANSSI + CVE enrichies dans un DataFrame pandas.

Une ligne du DataFrame = un (bulletin ANSSI, CVE, produit affecté).
Un bulletin référençant plusieurs CVE, ou un CVE affectant plusieurs
produits, génère donc plusieurs lignes (cf. consigne du sujet).
"""
import csv
import os
from pathlib import Path

import pandas as pd

from cve_enrichment import enrich_cve
from cve_extraction import extract_cves_from_bulletin

COLUMNS = [
    "id_anssi", "titre_anssi", "type_bulletin", "date_publication",
    "cve", "cvss_score", "base_severity", "cwe", "cwe_desc", "epss_score",
    "lien_anssi", "description", "editeur", "produit", "versions_affectees",
]


def build_dataframe(
    bulletins, verbose=True, incremental_csv_path=None, use_cache=True, refresh_cache=False
):
    """Construit le DataFrame consolidé à partir d'une liste de bulletins
    (telle que retournée par rss_extraction.extract_all_bulletins).

    Si incremental_csv_path est fourni, chaque ligne est aussi ajoutée
    immédiatement à ce fichier CSV, afin de ne rien perdre en cas
    d'interruption (le pipeline interroge des API externes qui peuvent
    être lentes ou instables).
    """
    rows = []
    csv_file = None
    csv_writer = None

    if incremental_csv_path:
        file_exists = os.path.exists(incremental_csv_path)
        csv_file = open(incremental_csv_path, "a", newline="", encoding="utf-8")
        csv_writer = csv.DictWriter(csv_file, fieldnames=COLUMNS)
        if not file_exists:
            csv_writer.writeheader()

    def emit(row):
        rows.append(row)
        if csv_writer:
            csv_writer.writerow(row)
            csv_file.flush()

    for bulletin in bulletins:
        try:
            cve_ids = extract_cves_from_bulletin(
                bulletin["lien"], use_cache=use_cache, refresh_cache=refresh_cache
            )
        except Exception as exc:
            if verbose:
                print(f"[WARN] Échec extraction CVE pour {bulletin['id_anssi']}: {exc}")
            continue

        if not cve_ids:
            emit({
                "id_anssi": bulletin["id_anssi"],
                "titre_anssi": bulletin["titre"],
                "type_bulletin": bulletin["type_bulletin"],
                "date_publication": bulletin["date_publication"],
                "cve": None, "cvss_score": None, "base_severity": None,
                "cwe": None, "cwe_desc": None, "epss_score": None,
                "lien_anssi": bulletin["lien"],
                "description": None, "editeur": None, "produit": None,
                "versions_affectees": None,
            })
            continue

        for cve_id in cve_ids:
            if verbose:
                print(f"  -> enrichissement {cve_id}")
            try:
                info = enrich_cve(cve_id, use_cache=use_cache, refresh_cache=refresh_cache)
            except Exception as exc:
                if verbose:
                    print(f"[WARN] Échec enrichissement {cve_id}: {exc}")
                continue

            produits = info["produits"] or [{"vendor": None, "product": None, "versions": []}]
            for prod in produits:
                emit({
                    "id_anssi": bulletin["id_anssi"],
                    "titre_anssi": bulletin["titre"],
                    "type_bulletin": bulletin["type_bulletin"],
                    "date_publication": bulletin["date_publication"],
                    "cve": info["cve_id"],
                    "cvss_score": info["cvss_score"],
                    "base_severity": info["base_severity"],
                    "cwe": info["cwe"],
                    "cwe_desc": info["cwe_desc"],
                    "epss_score": info["epss_score"],
                    "lien_anssi": bulletin["lien"],
                    "description": info["description"],
                    "editeur": prod["vendor"],
                    "produit": prod["product"],
                    "versions_affectees": ", ".join(prod["versions"]) if prod["versions"] else None,
                })

    if csv_file:
        csv_file.close()

    df = pd.DataFrame(rows, columns=COLUMNS)
    df["date_publication"] = pd.to_datetime(
        df["date_publication"], errors="coerce", utc=True, format="mixed"
    )
    return df


def save_dataframe(df, path):
    df.to_csv(path, index=False)
    print(f"DataFrame sauvegardé dans {path} ({len(df)} lignes)")


if __name__ == "__main__":
    from rss_extraction import extract_all_bulletins

    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    OUTPUT_PATH = PROJECT_ROOT / "data" / "vulnerabilites_anssi.csv"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    bulletins = extract_all_bulletins()
    df = build_dataframe(bulletins, incremental_csv_path=OUTPUT_PATH)
    print(f"Pipeline terminé : {len(df)} lignes écrites dans {OUTPUT_PATH}")

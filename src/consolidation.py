"""Consolidation des données ANSSI + CVE enrichies dans un DataFrame pandas.

Une ligne du DataFrame = un (bulletin ANSSI, CVE, produit affecté).
Un bulletin référençant plusieurs CVE, ou un CVE affectant plusieurs
produits, génère donc plusieurs lignes (cf. consigne du sujet).
"""
import csv
import os
import argparse
from pathlib import Path

import pandas as pd

try:
    from .cve_enrichment import enrich_cve
    from .cve_extraction import extract_cves_from_bulletin
except ImportError:
    from cve_enrichment import enrich_cve
    from cve_extraction import extract_cves_from_bulletin

COLUMNS = [
    "id_anssi", "titre_anssi", "type_bulletin", "date_publication",
    "cve", "cvss_score", "base_severity", "cwe", "cwe_desc", "epss_score",
    "lien_anssi", "description", "editeur", "produit", "versions_affectees",
]


def _clean_cell(value):
    if isinstance(value, str):
        return " ".join(value.split())
    return value


def _clean_row(row):
    return {key: _clean_cell(value) for key, value in row.items()}


def build_dataframe(
    bulletins,
    verbose=True,
    incremental_csv_path=None,
    use_cache=True,
    refresh_cache=False,
    data_source="live",
    fallback_root=None,
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
        csv_writer = csv.DictWriter(csv_file, fieldnames=COLUMNS, lineterminator="\n")
        if not file_exists:
            csv_writer.writeheader()

    def emit(row):
        row = _clean_row(row)
        rows.append(row)
        if csv_writer:
            csv_writer.writerow(row)
            csv_file.flush()

    for bulletin in bulletins:
        try:
            cve_ids = extract_cves_from_bulletin(
                bulletin["lien"],
                use_cache=use_cache,
                refresh_cache=refresh_cache,
                data_source=data_source,
                fallback_root=fallback_root,
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
                info = enrich_cve(
                    cve_id,
                    use_cache=use_cache,
                    refresh_cache=refresh_cache,
                    data_source=data_source,
                    fallback_root=fallback_root,
                )
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
    df = df.drop_duplicates()
    df.to_csv(path, index=False, lineterminator="\n")
    print(f"DataFrame sauvegardé dans {path} ({len(df)} lignes)")


def write_consolidated_csv(
    bulletins,
    output_path,
    verbose=True,
    use_cache=True,
    refresh_cache=False,
    data_source="live",
    fallback_root=None,
):
    """Construit le DataFrame et remplace le CSV final par une sortie propre.

    Le pipeline écrit d'abord dans un fichier temporaire incrémental pour
    conserver l'intérêt du flush ligne par ligne sans réappendre sur un ancien
    livrable lors des relances.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_name(f".{output_path.name}.tmp")
    if tmp_path.exists():
        tmp_path.unlink()

    df = build_dataframe(
        bulletins,
        verbose=verbose,
        incremental_csv_path=tmp_path,
        use_cache=use_cache,
        refresh_cache=refresh_cache,
        data_source=data_source,
        fallback_root=fallback_root,
    )
    df = df.drop_duplicates()
    df.to_csv(output_path, index=False, lineterminator="\n")
    tmp_path.unlink(missing_ok=True)
    return df


if __name__ == "__main__":
    from rss_extraction import extract_all_bulletins

    parser = argparse.ArgumentParser(description="Pipeline ANSSI/CVE vers CSV consolide")
    parser.add_argument("--data-source", choices=["live", "fallback"], default="live")
    parser.add_argument("--fallback-root", default=None, help="Racine locale data_fallback/")
    parser.add_argument("--output", default=None, help="Chemin du CSV de sortie")
    args = parser.parse_args()

    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    OUTPUT_PATH = Path(args.output) if args.output else PROJECT_ROOT / "data" / "vulnerabilites_anssi.csv"
    fallback_root = Path(args.fallback_root) if args.fallback_root else PROJECT_ROOT / "data_fallback"
    bulletins = extract_all_bulletins(data_source=args.data_source, fallback_root=fallback_root)
    df = write_consolidated_csv(
        bulletins,
        OUTPUT_PATH,
        data_source=args.data_source,
        fallback_root=fallback_root,
    )
    print(f"Pipeline terminé : {len(df)} lignes écrites dans {OUTPUT_PATH}")

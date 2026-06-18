"""Extraction des CVE référencées dans un bulletin ANSSI (avis ou alerte)."""
import re
import time

import requests

CVE_PATTERN = r"CVE-\d{4}-\d{4,7}"
REQUEST_DELAY = 2  # secondes, rate limiting imposé par le sujet


def fetch_bulletin_json(lien_bulletin):
    """Récupère le JSON d'un bulletin ANSSI à partir de son lien (ajout de 'json/')."""
    url = lien_bulletin.rstrip("/") + "/json/"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    time.sleep(REQUEST_DELAY)
    return response.json()


def extract_cves_from_bulletin(lien_bulletin):
    """Retourne la liste des identifiants CVE référencés dans un bulletin.

    Utilise en priorité la clé 'cves' du JSON, et complète par une regex
    sur l'ensemble du document au cas où certains CVE ne seraient cités
    que dans le texte (descriptions, risques...).
    """
    data = fetch_bulletin_json(lien_bulletin)

    ref_cves = [c["name"] for c in data.get("cves", []) if "name" in c]
    regex_cves = re.findall(CVE_PATTERN, str(data))

    return sorted(set(ref_cves) | set(regex_cves))


if __name__ == "__main__":
    lien = "https://www.cert.ssi.gouv.fr/avis/CERTFR-2026-AVI-0632/"
    print(extract_cves_from_bulletin(lien))

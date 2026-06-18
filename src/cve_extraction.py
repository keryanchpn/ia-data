"""Extraction des CVE référencées dans un bulletin ANSSI (avis ou alerte)."""
import re
import time

import requests

from cache_utils import get_json_with_cache

CVE_PATTERN = r"CVE-\d{4}-\d{4,7}"
REQUEST_DELAY = 2  # secondes, rate limiting imposé par le sujet


def _bulletin_cache_key(lien_bulletin):
    return lien_bulletin.rstrip("/").split("/")[-1]


def fetch_bulletin_json(lien_bulletin, use_cache=True, refresh_cache=False):
    """Récupère le JSON d'un bulletin ANSSI à partir de son lien (ajout de 'json/')."""
    cache_key = _bulletin_cache_key(lien_bulletin)

    def fetch_json():
        url = lien_bulletin.rstrip("/") + "/json/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return response.json()

    return get_json_with_cache(
        "anssi", cache_key, fetch_json, use_cache=use_cache, refresh_cache=refresh_cache
    )


def extract_cves_from_bulletin(lien_bulletin, use_cache=True, refresh_cache=False):
    """Retourne la liste des identifiants CVE référencés dans un bulletin.

    Utilise en priorité la clé 'cves' du JSON, et complète par une regex
    sur l'ensemble du document au cas où certains CVE ne seraient cités
    que dans le texte (descriptions, risques...).
    """
    data = fetch_bulletin_json(lien_bulletin, use_cache=use_cache, refresh_cache=refresh_cache)

    ref_cves = [c["name"] for c in data.get("cves", []) if "name" in c]
    regex_cves = re.findall(CVE_PATTERN, str(data))

    return sorted(set(ref_cves) | set(regex_cves))


if __name__ == "__main__":
    lien = "https://www.cert.ssi.gouv.fr/avis/CERTFR-2026-AVI-0632/"
    print(extract_cves_from_bulletin(lien))

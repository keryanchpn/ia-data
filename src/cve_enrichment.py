"""Enrichissement des CVE via l'API MITRE (CVSS, CWE, produits affectés)
et l'API EPSS de FIRST (probabilité d'exploitation)."""
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from .cache_utils import get_json_with_cache
    from .fallback_data import read_fallback_json
except ImportError:
    from cache_utils import get_json_with_cache
    from fallback_data import read_fallback_json

MITRE_URL = "https://cveawg.mitre.org/api/cve/{cve_id}"
EPSS_URL = "https://api.first.org/data/v1/epss?cve={cve_id}"
REQUEST_DELAY = 2  # secondes, rate limiting imposé par le sujet
REQUEST_TIMEOUT = 10  # secondes, pour échouer rapidement plutôt que de bloquer

_session = requests.Session()
_retry = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
_session.mount("https://", HTTPAdapter(max_retries=_retry))

# Clés CVSS possibles selon la version du record (cf. avertissement du sujet)
CVSS_KEYS = ["cvssV4_0", "cvssV3_1", "cvssV3_0", "cvssV2_0"]


def _extract_cvss(metrics):
    """Cherche un score CVSS et sa sévérité dans la liste 'metrics', quelle
    que soit la clé de version utilisée (cvssV3_1, cvssV3_0, ...)."""
    for metric in metrics or []:
        for key in CVSS_KEYS:
            if key in metric:
                cvss = metric[key]
                return cvss.get("baseScore"), cvss.get("baseSeverity")
    return None, None


def _extract_cwe(problem_types):
    if problem_types and "descriptions" in problem_types[0]:
        desc = problem_types[0]["descriptions"][0]
        return desc.get("cweId", "Non disponible"), desc.get("description", "Non disponible")
    return "Non disponible", "Non disponible"


def _extract_affected(affected):
    products = []
    for product in affected or []:
        vendor = product.get("vendor", "Non disponible")
        product_name = product.get("product", "Non disponible")
        versions = [v["version"] for v in product.get("versions", []) if v.get("status") == "affected"]
        products.append({"vendor": vendor, "product": product_name, "versions": versions})
    return products


def fetch_mitre_info(cve_id, use_cache=True, refresh_cache=False, data_source="live", fallback_root=None):
    """Interroge l'API MITRE pour un CVE et retourne ses informations clés."""
    def fetch_json():
        url = MITRE_URL.format(cve_id=cve_id)
        response = _session.get(url, timeout=REQUEST_TIMEOUT)
        time.sleep(REQUEST_DELAY)
        response.raise_for_status()
        return response.json()

    try:
        if data_source == "fallback":
            data = read_fallback_json("mitre", cve_id, fallback_root=fallback_root)
        elif data_source == "live":
            data = get_json_with_cache(
                "mitre", cve_id, fetch_json, use_cache=use_cache, refresh_cache=refresh_cache
            )
        else:
            raise ValueError("data_source doit être 'live' ou 'fallback'")
    except (requests.RequestException, FileNotFoundError):
        return {
            "cve_id": cve_id, "description": "Non disponible", "cvss_score": None,
            "base_severity": "Non disponible", "cwe": "Non disponible",
            "cwe_desc": "Non disponible", "produits": [],
        }

    containers = data.get("containers", {})
    cna = containers.get("cna", {})

    descriptions = cna.get("descriptions", [])
    description = descriptions[0]["value"] if descriptions else "Non disponible"

    cvss_score, base_severity = _extract_cvss(cna.get("metrics"))
    if cvss_score is None:
        # Certains CNA (ex: Google/Chrome) ne renseignent pas le CVSS et le
        # laissent à un ADP (Authorized Data Publisher, ex: CISA).
        for adp in containers.get("adp", []):
            cvss_score, base_severity = _extract_cvss(adp.get("metrics"))
            if cvss_score is not None:
                break

    cwe, cwe_desc = _extract_cwe(cna.get("problemTypes", []))
    produits = _extract_affected(cna.get("affected", []))

    return {
        "cve_id": cve_id,
        "description": description,
        "cvss_score": cvss_score,
        "base_severity": base_severity,
        "cwe": cwe,
        "cwe_desc": cwe_desc,
        "produits": produits,
    }


def fetch_epss_score(cve_id, use_cache=True, refresh_cache=False, data_source="live", fallback_root=None):
    """Interroge l'API EPSS de FIRST et retourne la probabilité d'exploitation."""
    def fetch_json():
        url = EPSS_URL.format(cve_id=cve_id)
        response = _session.get(url, timeout=REQUEST_TIMEOUT)
        time.sleep(REQUEST_DELAY)
        response.raise_for_status()
        return response.json()

    try:
        if data_source == "fallback":
            response_data = read_fallback_json("first", cve_id, fallback_root=fallback_root)
        elif data_source == "live":
            response_data = get_json_with_cache(
                "epss", cve_id, fetch_json, use_cache=use_cache, refresh_cache=refresh_cache
            )
        else:
            raise ValueError("data_source doit être 'live' ou 'fallback'")
    except (requests.RequestException, FileNotFoundError):
        return None

    data = response_data.get("data", [])
    if not data:
        return None
    return float(data[0]["epss"])


def enrich_cve(cve_id, use_cache=True, refresh_cache=False, data_source="live", fallback_root=None):
    """Combine les informations MITRE et EPSS pour un CVE donné."""
    info = fetch_mitre_info(
        cve_id,
        use_cache=use_cache,
        refresh_cache=refresh_cache,
        data_source=data_source,
        fallback_root=fallback_root,
    )
    info["epss_score"] = fetch_epss_score(
        cve_id,
        use_cache=use_cache,
        refresh_cache=refresh_cache,
        data_source=data_source,
        fallback_root=fallback_root,
    )
    return info


if __name__ == "__main__":
    print(enrich_cve("CVE-2026-6517"))

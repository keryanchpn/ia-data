"""Cache JSON local pour les réponses ANSSI, MITRE et EPSS."""
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CACHE_ROOT = PROJECT_ROOT / "data" / "cache"


def _safe_cache_key(key):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(key)).strip("_") or "cache"


def get_cache_path(namespace, key, cache_root=None):
    root = Path(cache_root) if cache_root is not None else DEFAULT_CACHE_ROOT
    return root / _safe_cache_key(namespace) / f"{_safe_cache_key(key)}.json"


def read_json_cache(namespace, key, cache_root=None):
    path = get_cache_path(namespace, key, cache_root=cache_root)
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json_cache(namespace, key, data, cache_root=None):
    path = get_cache_path(namespace, key, cache_root=cache_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2, sort_keys=True)
    return path


def get_json_with_cache(
    namespace,
    key,
    fetch_json,
    cache_root=None,
    use_cache=True,
    refresh_cache=False,
    fallback_to_cache=True,
):
    """Retourne un JSON depuis le cache ou via fetch_json().

    - use_cache=True lit/ecrit dans data/cache.
    - refresh_cache=True force un nouvel appel et remplace le cache.
    - fallback_to_cache=True relit le cache si l'appel externe échoue.
    """
    path = get_cache_path(namespace, key, cache_root=cache_root)

    if use_cache and not refresh_cache and path.exists():
        return read_json_cache(namespace, key, cache_root=cache_root)

    try:
        data = fetch_json()
    except Exception:
        if use_cache and fallback_to_cache and path.exists():
            return read_json_cache(namespace, key, cache_root=cache_root)
        raise

    if use_cache:
        write_json_cache(namespace, key, data, cache_root=cache_root)
    return data

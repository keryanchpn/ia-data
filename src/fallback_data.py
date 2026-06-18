"""Lecture des donnees JSON locales fournies dans data_fallback/."""
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FALLBACK_ROOT = PROJECT_ROOT / "data_fallback"

FALLBACK_DIRS = {
    "avis": "avis",
    "alerte": "alertes",
    "alertes": "alertes",
    "mitre": "mitre",
    "first": "first",
    "epss": "first",
}


def _fallback_root(fallback_root=None):
    return Path(fallback_root) if fallback_root is not None else DEFAULT_FALLBACK_ROOT


def _candidate_directories(root, directory):
    names = dict.fromkeys([directory, directory.lower(), directory.capitalize()])
    for base in (root, root / "data"):
        for name in names:
            yield base / name


def _candidate_paths(root, directory, key):
    for candidate_dir in _candidate_directories(root, directory):
        base = candidate_dir / key
        yield base
        if base.suffix != ".json":
            yield base.with_suffix(".json")


def read_fallback_json(namespace, key, fallback_root=None):
    """Lit un JSON fallback par namespace et identifiant.

    Les fichiers peuvent s'appeler soit `KEY`, soit `KEY.json`.
    """
    root = _fallback_root(fallback_root)
    if namespace == "anssi":
        directories = ["avis", "alertes"]
    else:
        directories = [FALLBACK_DIRS[namespace]]

    searched = []
    for directory in directories:
        for path in _candidate_paths(root, directory, key):
            searched.append(path)
            if path.exists():
                with path.open("r", encoding="utf-8") as file:
                    return json.load(file)

    searched_text = ", ".join(str(path) for path in searched)
    raise FileNotFoundError(f"Aucun JSON fallback trouve pour {namespace}/{key}. Chemins testes: {searched_text}")


def iter_fallback_json(namespace, fallback_root=None):
    """Itere sur les fichiers JSON d'un namespace fallback."""
    root = _fallback_root(fallback_root)
    seen = set()
    for directory in _candidate_directories(root, FALLBACK_DIRS[namespace]):
        if not directory.exists():
            continue
        for path in sorted(p for p in directory.iterdir() if p.is_file()):
            if path in seen:
                continue
            seen.add(path)
            with path.open("r", encoding="utf-8") as file:
                yield path, json.load(file)

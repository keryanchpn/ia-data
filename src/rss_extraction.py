"""Extraction des flux RSS des avis et alertes ANSSI (CERT-FR)."""
try:
    from .fallback_data import iter_fallback_json
except ImportError:
    from fallback_data import iter_fallback_json

RSS_URLS = {
    "avis": "https://www.cert.ssi.gouv.fr/avis/feed/",
    "alerte": "https://www.cert.ssi.gouv.fr/alerte/feed/",
}


def _first_revision_date(data):
    revisions = data.get("revisions") or []
    if revisions:
        return revisions[0].get("revision_date")
    return data.get("date") or data.get("last_revision_date")


def _extract_fallback_bulletins(bulletin_type, fallback_root=None):
    namespace = "alerte" if bulletin_type == "alerte" else "avis"
    type_label = "Alerte" if bulletin_type == "alerte" else "Avis"
    url_part = "alerte" if bulletin_type == "alerte" else "avis"
    bulletins = []

    for path, data in iter_fallback_json(namespace, fallback_root=fallback_root):
        id_anssi = data.get("reference") or path.stem
        bulletins.append({
            "id_anssi": id_anssi,
            "titre": data.get("title", id_anssi),
            "type_bulletin": type_label,
            "date_publication": _first_revision_date(data),
            "description": data.get("summary", data.get("content", "")),
            "lien": f"https://www.cert.ssi.gouv.fr/{url_part}/{id_anssi}/",
        })
    return bulletins


def extract_bulletins(bulletin_type, data_source="live", fallback_root=None):
    """Extrait les bulletins (avis ou alerte) d'un flux RSS ANSSI.

    Retourne une liste de dicts avec id_anssi, titre, type, date, lien.
    """
    if bulletin_type not in RSS_URLS:
        raise ValueError("bulletin_type doit être 'avis' ou 'alerte'")

    if data_source == "fallback":
        return _extract_fallback_bulletins(bulletin_type, fallback_root=fallback_root)
    if data_source != "live":
        raise ValueError("data_source doit être 'live' ou 'fallback'")

    import feedparser

    feed = feedparser.parse(RSS_URLS[bulletin_type])
    bulletins = []
    for entry in feed.entries:
        lien = entry.link.rstrip("/")
        id_anssi = lien.split("/")[-1]
        bulletins.append({
            "id_anssi": id_anssi,
            "titre": entry.title,
            "type_bulletin": "Alerte" if bulletin_type == "alerte" else "Avis",
            "date_publication": getattr(entry, "published", None),
            "description": entry.get("summary", ""),
            "lien": entry.link,
        })
    return bulletins


def extract_all_bulletins(data_source="live", fallback_root=None):
    """Extrait l'ensemble des avis et alertes disponibles dans les flux RSS."""
    return (
        extract_bulletins("avis", data_source=data_source, fallback_root=fallback_root)
        + extract_bulletins("alerte", data_source=data_source, fallback_root=fallback_root)
    )


if __name__ == "__main__":
    bulletins = extract_all_bulletins()
    print(f"{len(bulletins)} bulletins extraits")
    for b in bulletins[:3]:
        print(b)

"""Extraction des flux RSS des avis et alertes ANSSI (CERT-FR)."""
import feedparser

RSS_URLS = {
    "avis": "https://www.cert.ssi.gouv.fr/avis/feed/",
    "alerte": "https://www.cert.ssi.gouv.fr/alerte/feed/",
}


def extract_bulletins(bulletin_type):
    """Extrait les bulletins (avis ou alerte) d'un flux RSS ANSSI.

    Retourne une liste de dicts avec id_anssi, titre, type, date, lien.
    """
    if bulletin_type not in RSS_URLS:
        raise ValueError("bulletin_type doit être 'avis' ou 'alerte'")

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


def extract_all_bulletins():
    """Extrait l'ensemble des avis et alertes disponibles dans les flux RSS."""
    return extract_bulletins("avis") + extract_bulletins("alerte")


if __name__ == "__main__":
    bulletins = extract_all_bulletins()
    print(f"{len(bulletins)} bulletins extraits")
    for b in bulletins[:3]:
        print(b)

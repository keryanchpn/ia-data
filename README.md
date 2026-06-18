# Sup de Vinci - M1 DEV - Projet IA & Data

Projet IA & Data : analyse des avis et alertes ANSSI avec enrichissement des CVE.

Pipeline d'extraction, d'enrichissement et d'analyse des avis et alertes de
sécurité publiés par l'ANSSI (CERT-FR), avec enrichissement des CVE via les
API MITRE et FIRST (EPSS).

Documents produits :

- [Synthèse du projet](docs/synthese_projet.md)
- [Cahier des charges](docs/cahier_des_charges.md)

## Structure du projet

```
.
├── src/
│   ├── rss_extraction.py    # Étape 1 : extraction des flux RSS ANSSI (avis + alertes)
│   ├── cve_extraction.py    # Étape 2 : extraction des CVE depuis le JSON des bulletins
│   ├── cve_enrichment.py    # Étape 3 : enrichissement via API MITRE (CVSS, CWE) et API EPSS (FIRST)
│   ├── consolidation.py     # Étape 4 : consolidation dans un DataFrame pandas + export CSV
│   └── alerting.py          # Étape 7 : génération d'alertes personnalisées + notification email
├── data/
│   └── vulnerabilites_anssi.csv   # Données consolidées (généré par consolidation.py)
├── notebook/
│   └── analyse_anssi.ipynb        # Exploration, visualisations, ML (supervisé + non supervisé)
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### 1. Lancer le pipeline complet (extraction → enrichissement → CSV)

```bash
cd src
python3 consolidation.py
```

Cela va :
1. Récupérer tous les avis et alertes disponibles dans les flux RSS de l'ANSSI.
2. Pour chaque bulletin, extraire les CVE référencés (champ `cves` du JSON, complété par une regex de sécurité).
3. Enrichir chaque CVE via l'API MITRE (score CVSS, sévérité, CWE, produits/versions affectés) et l'API EPSS de FIRST (probabilité d'exploitation).
4. Consolider le tout dans un DataFrame pandas (une ligne par couple bulletin/CVE/produit) et l'exporter en CSV dans `data/vulnerabilites_anssi.csv`.

**Rate limiting** : un délai de 2 secondes est respecté entre chaque requête HTTP (RSS, JSON ANSSI, API MITRE, API EPSS) pour ne pas surcharger les serveurs externes, conformément à la consigne du sujet. Le traitement complet de tous les bulletins peut donc prendre plusieurs dizaines de minutes.

### 2. Explorer les données et lancer les modèles ML

```bash
jupyter notebook notebook/analyse_anssi.ipynb
```

Le notebook charge le CSV généré, explore le DataFrame, produit une série de
visualisations (distribution des scores CVSS, types de CWE, scores EPSS,
classement des éditeurs/produits les plus touchés, corrélation CVSS/EPSS,
évolution temporelle...), puis applique :
- un modèle **non supervisé** (clustering des vulnérabilités),
- un modèle **supervisé** (prédiction de la sévérité/criticité),

avec validation des deux modèles.

### 3. Générer des alertes personnalisées (et notifications email, optionnel)

```python
from src.alerting import send_alerts
import pandas as pd

df = pd.read_csv("data/vulnerabilites_anssi.csv")

subscribers = [
    {"name": "Alice", "email": "alice@example.com", "produits": ["Apache HTTP Server"]},
]

# Mode dry-run (affichage uniquement, par défaut)
send_alerts(df, subscribers)

# Envoi réel (nécessite un mot de passe d'application Gmail)
# send_alerts(df, subscribers, send=True, from_email="...", password="...")
```

Une alerte est générée pour un abonné dès qu'une vulnérabilité critique
(CVSS ≥ 9 ou EPSS ≥ 0.5) touche un des produits qu'il suit.

## Sources de données

- Flux RSS ANSSI : `https://www.cert.ssi.gouv.fr/avis/feed/` et `https://www.cert.ssi.gouv.fr/alerte/feed/`
- JSON détaillé d'un bulletin : `<lien_du_bulletin>/json/`
- API CVE MITRE : `https://cveawg.mitre.org/api/cve/{cve_id}`
- API EPSS FIRST : `https://api.first.org/data/v1/epss?cve={cve_id}`

## Équipe

| Prénom | Nom | Participation |
|-----|--------|----------------|
| Baptiste | DANDÉ | 33 % |
| Keryan | CHAMPION | 34 % |
| Nathan | HUMEAU | 33 % |

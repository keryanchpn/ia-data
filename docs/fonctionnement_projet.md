# Fonctionnement detaille du projet

## Vue d'ensemble

Le projet construit un pipeline Data/IA autour des bulletins de securite ANSSI/CERT-FR. Il recupere les avis et alertes publies par l'ANSSI, extrait les CVE mentionnees, enrichit ces CVE avec des donnees MITRE et FIRST EPSS, consolide tout dans un CSV, puis exploite ce CSV dans un notebook pour faire des visualisations et du Machine Learning.

Le flux global est :

```text
Flux RSS ANSSI
    -> Bulletins avis/alertes
        -> JSON detaille ANSSI
            -> Extraction des CVE
                -> Enrichissement MITRE + EPSS
                    -> DataFrame pandas
                        -> CSV consolide
                            -> Notebook d'analyse + ML
                            -> Alertes personnalisees
```

## 1. Extraction des bulletins ANSSI

Le fichier `src/rss_extraction.py` lit deux flux RSS :

- `https://www.cert.ssi.gouv.fr/avis/feed/`
- `https://www.cert.ssi.gouv.fr/alerte/feed/`

La fonction principale est `extract_all_bulletins()`.

Elle appelle :

```python
extract_bulletins("avis")
extract_bulletins("alerte")
```

Pour chaque entree RSS, le code recupere :

- `id_anssi` : identifiant du bulletin, extrait depuis l'URL ;
- `titre` ;
- `type_bulletin` : `Avis` ou `Alerte` ;
- `date_publication` ;
- `description` ;
- `lien`.

A ce stade, on a seulement les metadonnees du bulletin. Les CVE ne sont pas encore extraites.

## 2. Recuperation du JSON ANSSI et extraction des CVE

Le fichier `src/cve_extraction.py` prend le lien d'un bulletin ANSSI et recupere son JSON detaille.

Exemple :

```text
https://www.cert.ssi.gouv.fr/avis/CERTFR-2026-AVI-0632/
```

devient :

```text
https://www.cert.ssi.gouv.fr/avis/CERTFR-2026-AVI-0632/json/
```

La fonction `extract_cves_from_bulletin()` fait deux choses :

1. Elle lit la cle `cves` du JSON ANSSI si elle existe.
2. Elle applique aussi une regex `CVE-\d{4}-\d{4,7}` sur tout le JSON pour retrouver d'eventuelles CVE citees ailleurs.

Ensuite, elle fusionne les deux sources, supprime les doublons, trie la liste et retourne les identifiants CVE.

## 3. Source locale fallback

Le fichier `src/fallback_data.py` permet de faire tourner le pipeline entièrement sans appels réseau, en lisant des fichiers JSON pré-téléchargés stockés dans `data_fallback/`.

Structure attendue :

```text
data_fallback/
├── data/
│   ├── Avis/       # JSON des bulletins avis ANSSI
│   ├── alertes/    # JSON des bulletins alertes ANSSI
│   ├── mitre/      # réponses MITRE par CVE
│   └── first/      # réponses FIRST EPSS par CVE
```

Les deux fonctions principales sont :

- `read_fallback_json(namespace, key)` : lit un fichier JSON unique par namespace et identifiant.
- `iter_fallback_json(namespace)` : itère sur tous les fichiers d'un namespace.

Le lecteur accepte les noms de fichiers avec ou sans extension `.json`, et cherche dans plusieurs variantes de casse du dossier.

Pour activer ce mode depuis la ligne de commande :

```bash
python3 src/consolidation.py --data-source fallback --fallback-root data_fallback
```

Tous les modules (`rss_extraction`, `cve_extraction`, `cve_enrichment`) acceptent le paramètre `data_source="fallback"` et délèguent alors à `fallback_data` au lieu d'appeler les API externes.

## 4. Systeme de cache

Le fichier `src/cache_utils.py` gere le cache local JSON.

Le cache est stocke ici :

```text
data/cache/
├── anssi/
├── mitre/
└── epss/
```

Son role est d'eviter de refaire les memes appels reseau a chaque execution.

Fonctionnement :

1. Le code veut recuperer une reponse JSON.
2. Il verifie si un fichier existe deja dans `data/cache/...`.
3. Si oui, il le lit localement.
4. Sinon, il appelle l'API externe.
5. Si l'appel reussit, il sauvegarde la reponse JSON dans le cache.
6. Si l'appel reseau echoue mais qu'un cache existe deja, il utilise ce cache comme secours.

Les parametres disponibles sont :

```python
use_cache=True
refresh_cache=False
```

- `use_cache=True` : comportement normal, lit et ecrit le cache.
- `refresh_cache=True` : force un nouvel appel API et remplace le cache.
- `use_cache=False` : desactive le cache.

Le cache est utilise pour :

- les JSON detailles ANSSI ;
- les reponses MITRE ;
- les reponses EPSS.

Le flux RSS lui-meme reste interroge directement pour detecter les bulletins disponibles.

## 5. Enrichissement MITRE et EPSS

Le fichier `src/cve_enrichment.py` enrichit chaque CVE.

Pour MITRE, la fonction `fetch_mitre_info(cve_id)` recupere :

- description de la vulnerabilite ;
- score CVSS ;
- severite CVSS ;
- CWE ;
- description CWE ;
- editeur/vendor ;
- produit affecte ;
- versions affectees.

Le code gere plusieurs versions possibles de CVSS :

```python
cvssV4_0
cvssV3_1
cvssV3_0
cvssV2_0
```

Pour FIRST EPSS, la fonction `fetch_epss_score(cve_id)` recupere le score EPSS, c'est-a-dire la probabilite d'exploitation d'une vulnerabilite.

La fonction `enrich_cve(cve_id)` combine les deux :

```python
info = fetch_mitre_info(cve_id)
info["epss_score"] = fetch_epss_score(cve_id)
```

Elle retourne un dictionnaire complet pour une CVE.

## 6. Consolidation dans un DataFrame et CSV

Le fichier `src/consolidation.py` assemble tout.

La fonction centrale est `build_dataframe()`.

Elle recoit une liste de bulletins, puis pour chaque bulletin :

1. extrait les CVE ;
2. enrichit chaque CVE ;
3. recupere les produits affectes ;
4. cree une ou plusieurs lignes dans le DataFrame.

Important : une ligne correspond a un couple :

```text
bulletin ANSSI + CVE + produit affecte
```

Donc si un bulletin contient plusieurs CVE, ou si une CVE touche plusieurs produits, le bulletin sera repete sur plusieurs lignes.

Pour éviter de tout perdre en cas d'interruption réseau (le pipeline peut durer plusieurs dizaines de minutes), `write_consolidated_csv()` écrit d'abord dans un fichier temporaire `.vulnerabilites_anssi.csv.tmp` avec un flush ligne par ligne. Une fois le traitement terminé, ce fichier remplace le CSV final et le `.tmp` est supprimé.

Les colonnes generees sont :

```text
id_anssi
titre_anssi
type_bulletin
date_publication
cve
cvss_score
base_severity
cwe
cwe_desc
epss_score
lien_anssi
description
editeur
produit
versions_affectees
```

Quand on lance :

```bash
cd src
python3 consolidation.py
```

le script ecrit le fichier :

```text
data/vulnerabilites_anssi.csv
```

Le chemin est calcule depuis la racine du projet, donc il reste stable meme si on lance le script depuis un autre dossier.

## 7. Analyse et Machine Learning

Le notebook `notebook/analyse_anssi.ipynb` charge le CSV consolide :

```python
df = pd.read_csv("../data/vulnerabilites_anssi.csv", parse_dates=["date_publication"])
```

Avant les analyses, deux sous-ensembles filtrés sont construits :

- `df_cvss` : lignes où `cvss_score` est renseigné (49 % du corpus — 51 % des CVE n'ont pas de score CVSS dans MITRE).
- Les visualisations CWE et le modèle supervisé excluent les lignes où `cwe == "Non disponible"` (63,5 % du corpus) pour ne pas polluer les analyses avec une catégorie fictive.

Il fait ensuite :

- exploration du DataFrame et analyse des valeurs manquantes ;
- repartition des avis et alertes ;
- distribution des scores CVSS (sur `df_cvss`) ;
- distribution des scores EPSS en double vue : échelle linéaire + échelle logarithmique (log10) pour révéler la structure near-zero de la distribution ;
- top éditeurs et produits affectés ;
- répartition des CWE (CWE renseignés uniquement) ;
- corrélation CVSS/EPSS et nuage de points (sur `df_cvss`) ;
- évolution temporelle cumulative des bulletins.

La partie Machine Learning contient deux approches :

- non supervisé : clustering KMeans sur `cvss_score` et `epss_score`, nombre de clusters choisi par score de silhouette ;
- supervisé : RandomForest pour prédire la sévérité à partir de l'EPSS et du CWE (lignes avec CWE valide uniquement).

Le modele non supervise cherche a regrouper les vulnerabilites selon leur profil de risque. Le modele supervise tente de predire la categorie de severite CVSS.

## 8. Alertes personnalisees

Le fichier `src/alerting.py` sert a generer des alertes pour des abonnes.

Un abonne est represente comme ceci :

```python
{
    "name": "Alice",
    "email": "alice@example.com",
    "produits": ["Apache HTTP Server"]
}
```

Les seuils de criticité sont définis comme constantes dans `alerting.py` :

```python
CVSS_CRITIQUE_SEUIL = 9.0
EPSS_ALERTE_SEUIL = 0.5
```

La fonction `filter_alerts_for_subscriber()` garde les lignes qui respectent deux conditions :

1. le produit est suivi par l'abonne ;
2. la vulnerabilite est critique selon au moins un critere :
   - `cvss_score >= CVSS_CRITIQUE_SEUIL`
   - ou `epss_score >= EPSS_ALERTE_SEUIL`

Ensuite, `build_alert_message()` construit :

- le sujet du mail ;
- le corps du mail ;
- la liste des CVE concernees ;
- le produit ;
- l'editeur ;
- le CVSS ;
- l'EPSS ;
- le lien ANSSI.

Par defaut, `send_alerts()` fonctionne en dry-run : il affiche le message sans envoyer d'email. L'envoi reel SMTP Gmail est possible avec `send=True`, mais il faut fournir un email et un mot de passe d'application.

## 9. Fichiers importants

- `README.md` : explique installation, execution et structure.
- `src/rss_extraction.py` : extraction RSS ANSSI.
- `src/cve_extraction.py` : recuperation JSON ANSSI et extraction CVE.
- `src/cve_enrichment.py` : enrichissement MITRE et EPSS.
- `src/consolidation.py` : pipeline principal vers CSV.
- `src/cache_utils.py` : cache JSON local.
- `src/fallback_data.py` : lecture des données locales hors-ligne.
- `src/alerting.py` : alertes personnalisees.
- `notebook/analyse_anssi.ipynb` : analyse, visualisation et ML.
- `data/vulnerabilites_anssi.csv` : donnees consolidees.

## Resume

Le projet fonctionne comme un pipeline de veille cyber. Il transforme les bulletins ANSSI en donnees structurees, enrichies, analysables, visualisables et exploitables pour generer des alertes.

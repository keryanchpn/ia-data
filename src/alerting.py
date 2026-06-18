"""Génération d'alertes personnalisées et envoi de notifications email
pour les vulnérabilités critiques affectant des produits suivis par un
utilisateur (abonné).

L'envoi d'email est optionnel (cf. sujet) : send_alerts() fonctionne par
défaut en mode dry-run (affichage uniquement), il suffit de passer
send=True et des identifiants SMTP valides pour activer l'envoi réel.
"""
import smtplib
from email.mime.text import MIMEText

CVSS_CRITIQUE_SEUIL = 9.0
EPSS_ALERTE_SEUIL = 0.5


def filter_alerts_for_subscriber(df, produits_suivis, cvss_seuil=CVSS_CRITIQUE_SEUIL,
                                  epss_seuil=EPSS_ALERTE_SEUIL):
    """Filtre le DataFrame consolidé pour ne garder que les vulnérabilités
    critiques (CVSS élevé OU EPSS élevé) touchant les produits suivis par
    un abonné donné."""
    mask_produit = df["produit"].str.lower().isin([p.lower() for p in produits_suivis])
    mask_risque = (df["cvss_score"] >= cvss_seuil) | (df["epss_score"] >= epss_seuil)
    return df[mask_produit & mask_risque]


def build_alert_message(subscriber_name, alerts_df):
    """Construit le sujet et le corps de l'email d'alerte à partir des
    lignes du DataFrame correspondant aux vulnérabilités détectées."""
    nb = len(alerts_df)
    produits = ", ".join(sorted(alerts_df["produit"].dropna().unique()))
    subject = f"[Alerte ANSSI] {nb} vulnérabilité(s) critique(s) détectée(s) sur vos produits"

    lines = [
        f"Bonjour {subscriber_name},",
        "",
        f"{nb} vulnérabilité(s) critique(s) a/ont été détectée(s) sur les produits suivants : {produits}.",
        "",
    ]
    for _, row in alerts_df.iterrows():
        lines.append(
            f"- {row['cve']} | {row['produit']} ({row['editeur']}) | "
            f"CVSS: {row['cvss_score']} ({row['base_severity']}) | "
            f"EPSS: {row['epss_score']} | Bulletin: {row['lien_anssi']}"
        )
    lines += ["", "Merci de mettre à jour vos systèmes dès que possible.", "-- Alerte générée automatiquement"]
    return subject, "\n".join(lines)


def send_email(to_email, subject, body, from_email=None, password=None):
    """Envoie un email via SMTP Gmail. Nécessite un mot de passe d'application."""
    from_email = from_email or "votre_email@gmail.com"
    msg = MIMEText(body)
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()


def send_alerts(df, subscribers, send=False, from_email=None, password=None):
    """Génère les alertes pour chaque abonné et les envoie (ou les affiche
    en mode dry-run si send=False).

    subscribers: liste de dicts {"name": str, "email": str, "produits": [str]}
    """
    for sub in subscribers:
        alerts = filter_alerts_for_subscriber(df, sub["produits"])
        if alerts.empty:
            continue

        subject, body = build_alert_message(sub["name"], alerts)

        if send:
            send_email(sub["email"], subject, body, from_email=from_email, password=password)
            print(f"Email envoyé à {sub['email']}")
        else:
            print(f"--- [DRY-RUN] Alerte pour {sub['email']} ---")
            print("Sujet:", subject)
            print(body)
            print("-" * 40)

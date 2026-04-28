"""
Nettoyage pré-sentiment des avis Booking.

Deux problèmes identifiés après analyse des résultats BERT :
1. Métadonnées Booking en tête de texte perturbent le modèle
   ("Chalet 2 Chambres 3 nuits · avril 2026 Commentaire envoyé le...")
2. Avis sans texte ("Ce client n'a pas laissé de commentaire")
   classés systématiquement 1 étoile par BERT

Ce script produit une colonne `texte_sentiment` nettoyée,
utilisée uniquement pour l'analyse de sentiment.

Usage :
    python processing/clean_for_sentiment.py
    puis relancer : python ml/sentiment_analysis.py
"""

import re
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH    = PROJECT_ROOT / "data" / "processed" / "huttopia_reviews_master.csv"

# Phrases à exclure — avis sans contenu réel
EMPTY_PATTERNS = [
    r"ce client n'a pas laissé de commentaire",
    r"this reviewer did not leave a comment",
    r"voir la traduction",
    r"see the translation",
]

# Métadonnées Booking à supprimer en tête de texte
BOOKING_METADATA = re.compile(
    r"^.*?(?:"
    r"commentaire envoyé le \d+\S*\s+\w+\s+\d{4}"  # "Commentaire envoyé le 8 avril 2026"
    r"|avec une note de \d+[,.]?\d*"                # "Avec une note de 8,0"
    r")\s*",
    re.IGNORECASE | re.DOTALL,
)

# Supprime les préfixes de type hébergement
# "Chalet 2 Chambres 3 nuits · mars 2026 Voyageur individuel"
BOOKING_PREFIX = re.compile(
    r"^(?:chalet|tente|roulotte|mobil.?home|emplacement|lodge|yourte|cabane)"
    r".*?(?:\d+\s*nuits?|\d+\s*nights?)"
    r".*?(?:\d{4})\s*",
    re.IGNORECASE,
)


def clean_booking_text(text: str) -> str:
    """Nettoie un texte Booking pour l'analyse de sentiment."""
    # Supprime le préfixe hébergement + durée + date
    text = BOOKING_PREFIX.sub("", text).strip()
    # Supprime la ligne "Commentaire envoyé le..." et "Avec une note de..."
    text = BOOKING_METADATA.sub("", text).strip()
    # Supprime "Voyageur individuel" résiduel
    text = re.sub(r"^voyageur individuel\s*", "", text, flags=re.IGNORECASE).strip()
    return text


def is_empty_review(text: str) -> bool:
    """Retourne True si l'avis ne contient pas de contenu analysable."""
    text_lower = text.lower().strip()
    for pattern in EMPTY_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    # Texte trop court après nettoyage
    return len(text_lower) < 15


def prepare_sentiment_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crée la colonne `texte_sentiment` optimisée pour BERT.
    Les avis sans contenu reçoivent NaN — exclus de l'analyse.
    """
    df["texte_sentiment"] = df["texte_propre"].copy()

    # Nettoyage spécifique Booking
    mask_booking = df["source"] == "Booking"
    df.loc[mask_booking, "texte_sentiment"] = (
        df.loc[mask_booking, "texte_sentiment"]
        .astype(str)
        .apply(clean_booking_text)
    )

    # Marque les avis vides comme NaN
    df["texte_sentiment"] = df["texte_sentiment"].apply(
        lambda x: None if is_empty_review(str(x)) else str(x)
    )

    # Stats
    total    = len(df)
    vides    = df["texte_sentiment"].isna().sum()
    booking  = mask_booking.sum()
    b_vides  = df[mask_booking]["texte_sentiment"].isna().sum()

    print(f"✅ Nettoyage terminé :")
    print(f"   {total - vides}/{total} avis avec contenu analysable")
    print(f"   {vides} avis exclus (sans contenu)")
    print(f"   Booking : {b_vides}/{booking} avis exclus")

    # Aperçu des textes nettoyés
    print("\n   Aperçu Booking avant/après nettoyage (3 exemples) :")
    sample = df[mask_booking & df["texte_sentiment"].notna()].head(3)
    for _, row in sample.iterrows():
        print(f"   AVANT : {row['texte_propre'][:100]}")
        print(f"   APRÈS : {row['texte_sentiment'][:100]}")
        print()

    return df


if __name__ == "__main__":
    print(f"📂 Chargement de {DATA_PATH.name}...")
    df = pd.read_csv(DATA_PATH)
    print(f"   {len(df)} avis chargés\n")

    df = prepare_sentiment_text(df)

    df.to_csv(DATA_PATH, index=False, encoding="utf-8-sig")
    print(f"💾 Sauvegardé → {DATA_PATH}")
    print("\nRelance maintenant : python ml/sentiment_analysis.py")

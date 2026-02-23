"""
Nettoyage et prétraitement des avis collectés.

Usage:
    python clean_reviews.py
"""

import pandas as pd
import re
from langdetect import detect, LangDetectException


def clean_text(text):
    """
    Nettoie un texte d'avis client.
    
    Args:
        text (str): Texte brut
        
    Returns:
        str: Texte nettoyé
    """
    
    if pd.isna(text) or text == "":
        return ""
    
    # TODO Phase 3: Implémenter le nettoyage
    # - Supprimer les balises HTML
    # - Supprimer les caractères spéciaux
    # - Normaliser les espaces
    # - Gérer les emojis (garder ou supprimer selon les tests)
    
    text = str(text).strip()
    
    return text


def detect_language(text):
    """
    Détecte la langue d'un texte.
    
    Args:
        text (str): Texte à analyser
        
    Returns:
        str: Code langue (fr, en, nl, es, etc.) ou 'unknown'
    """
    
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def normalize_rating(rating, source):
    """
    Normalise une note sur l'échelle /5.
    
    Args:
        rating (float): Note brute
        source (str): Source de l'avis (google, trustpilot, booking)
        
    Returns:
        float: Note normalisée sur /5
    """
    
    # TODO Phase 3: Gérer les différentes échelles
    # - Google: déjà sur /5
    # - Trustpilot: déjà sur /5
    # - Booking: sur /10 → diviser par 2
    
    if source == "booking":
        return rating / 2.0
    
    return rating


def clean_reviews(input_path, output_path):
    """
    Pipeline complet de nettoyage.
    
    Args:
        input_path (str): Chemin du CSV brut
        output_path (str): Chemin du CSV nettoyé
    """
    
    print(f"Chargement de {input_path}...")
    df = pd.read_csv(input_path)
    
    print(f"Nombre d'avis bruts: {len(df)}")
    
    # TODO Phase 3: Appliquer les transformations
    # 1. Nettoyer les textes
    # 2. Détecter les langues
    # 3. Filtrer FR + EN
    # 4. Normaliser les notes
    # 5. Dédupliquer
    
    print(f"Nombre d'avis nettoyés: {len(df)}")
    
    df.to_csv(output_path, index=False)
    print(f"Sauvegardé dans {output_path}")
    
    return df


if __name__ == "__main__":
    # Test sur un fichier exemple
    # clean_reviews("../data/raw/combined_raw.csv", "../data/processed/reviews_clean.csv")
    pass

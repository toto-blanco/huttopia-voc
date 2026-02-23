"""
Scraper pour Trustpilot - collecte des avis Huttopia.

Usage:
    python trustpilot_scraper.py
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random


def scrape_trustpilot(brand="Huttopia", max_pages=5):
    """
    Collecte les avis d'une marque sur Trustpilot.
    
    Args:
        brand (str): Nom de la marque (Huttopia, Homair, etc.)
        max_pages (int): Nombre maximum de pages à scraper
        
    Returns:
        pd.DataFrame: DataFrame avec colonnes [id, brand, source, date, note_brute, texte, langue]
    """
    
    # TODO Phase 2: Implémenter le scraping
    # URL base: https://fr.trustpilot.com/review/www.huttopia.com
    
    reviews = []
    
    # Headers pour éviter le blocage
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print(f"Collecte des avis {brand} sur Trustpilot...")
    
    # TODO: Boucle sur les pages
    # TODO: Parser les avis (note, texte, date)
    # TODO: Gérer les erreurs 403
    
    return pd.DataFrame(reviews)


if __name__ == "__main__":
    # Test rapide
    df = scrape_trustpilot(brand="Huttopia", max_pages=1)
    print(f"Collecté: {len(df)} avis")
    
    if len(df) > 0:
        df.to_csv("../data/raw/trustpilot_raw.csv", index=False)
        print("Sauvegardé dans data/raw/trustpilot_raw.csv")

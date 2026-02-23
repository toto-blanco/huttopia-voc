"""
Scraper pour Google Places API - collecte des avis Google Maps.

Usage:
    python google_scraper.py
    
Nécessite: GOOGLE_PLACES_API_KEY dans .env
"""

import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


def scrape_google_places(brand="Huttopia", place_ids=None):
    """
    Collecte les avis Google Maps via l'API Places.
    
    Args:
        brand (str): Nom de la marque
        place_ids (list): Liste des Place IDs à collecter
        
    Returns:
        pd.DataFrame: DataFrame avec colonnes [id, brand, source, date, note_brute, texte, langue]
    """
    
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    
    if not api_key:
        print("⚠️ GOOGLE_PLACES_API_KEY non trouvée dans .env")
        return pd.DataFrame()
    
    reviews = []
    
    # TODO Phase 2: Implémenter l'appel à l'API
    # URL: https://maps.googleapis.com/maps/api/place/details/json
    
    print(f"Collecte des avis {brand} sur Google Places...")
    
    # TODO: Boucle sur les place_ids
    # TODO: Parser les reviews de la réponse JSON
    # TODO: Gérer la pagination (next_page_token)
    
    return pd.DataFrame(reviews)


def find_place_ids(query="Huttopia France"):
    """
    Trouve les Place IDs correspondant à une recherche.
    
    Args:
        query (str): Requête de recherche
        
    Returns:
        list: Liste des Place IDs trouvés
    """
    
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    
    if not api_key:
        return []
    
    # TODO: Implémenter la recherche de places
    # URL: https://maps.googleapis.com/maps/api/place/textsearch/json
    
    return []


if __name__ == "__main__":
    # Test rapide
    df = scrape_google_places(brand="Huttopia")
    print(f"Collecté: {len(df)} avis")
    
    if len(df) > 0:
        df.to_csv("../data/raw/google_raw.csv", index=False)
        print("Sauvegardé dans data/raw/google_raw.csv")

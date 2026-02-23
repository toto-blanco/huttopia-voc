import requests
import pandas as pd
from datetime import datetime
import os
import time
from dotenv import load_dotenv

load_dotenv()

def find_place_ids(query="Huttopia France"):
    """Trouve les établissements Huttopia et leurs Place IDs."""
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    params = {
        'query': query,
        'key': api_key
    }
    
    print(f"🔍 Recherche des établissements pour : {query}...")
    response = requests.get(url, params=params)
    results = response.json().get('results', [])
    
    places = []
    for place in results:
        places.append({
            'name': place.get('name'),
            'place_id': place.get('place_id'),
            'address': place.get('formatted_address')
        })
    
    print(f"✅ {len(places)} établissements trouvés.")
    return places

def scrape_google_places(brand="Huttopia"):
    """Collecte les avis pour chaque établissement trouvé."""
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("⚠️ GOOGLE_PLACES_API_KEY manquante.")
        return pd.DataFrame()

    places = find_place_ids(f"{brand} France")
    all_reviews = []
    
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    for place in places:
        print(f"📥 Récupération des avis pour : {place['name']}...")
        params = {
            'place_id': place['place_id'],
            'fields': 'reviews,name',
            'key': api_key,
            'language': 'fr'
        }
        
        response = requests.get(url, params=params)
        data = response.json().get('result', {})
        reviews = data.get('reviews', [])
        
        for r in reviews:
            all_reviews.append({
                'id': r.get('time'), # Google n'envoie pas d'ID unique, on utilise le timestamp
                'brand': brand,
                'nom_etablissement': place['name'], # Pour tes analyses par site !
                'source': 'Google',
                'date': datetime.fromtimestamp(r.get('time')).strftime('%Y-%m-%d'),
                'note_brute': r.get('rating'),
                'texte': r.get('text'),
                'langue': r.get('language', 'fr')
            })
        
        # Petit délai pour respecter les quotas
        time.sleep(0.2)

    return pd.DataFrame(all_reviews)

if __name__ == "__main__":
    df = scrape_google_places(brand="Huttopia")
    
    if not df.empty:
        # On s'assure que le dossier existe
        os.makedirs("../data/raw", exist_ok=True)
        output_file = "../data/raw/google_raw.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n🚀 Mission accomplie : {len(df)} avis Google collectés et sauvegardés !")
    else:
        print("❌ Aucun avis trouvé. Vérifie ta clé API ou tes quotas.")
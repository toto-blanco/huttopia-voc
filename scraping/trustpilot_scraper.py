"""
Scraper pour Trustpilot - collecte des avis Huttopia & Concurrents.
Version optimisée basée sur le diagnostic HTML 2026.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random
import re
import hashlib
import os

def generate_review_id(brand, source, text, date):
    """Génère un ID unique pour éviter les doublons lors des collectes successives."""
    unique_string = f"{brand}_{source}_{text[:100]}_{date}"
    return hashlib.md5(unique_string.encode()).hexdigest()[:12]

def scrape_trustpilot_page(url, brand="Huttopia"):
    """Scrape une page Trustpilot avec les sélecteurs CSS identifiés."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"⚠️ Status {response.status_code} pour {url}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        reviews = []
        
        # Identification des articles
        articles = soup.find_all('article')
        
        for article in articles:
            try:
                # 1. Extraction de la note (via l'attribut data-service-review-rating)
                rating_elem = article.find(attrs={'data-service-review-rating': True})
                rating = rating_elem.get('data-service-review-rating') if rating_elem else None
                
                # 2. Extraction du texte (via la classe dynamique identifiée)
                # On utilise une fonction lambda pour matcher la classe commençant par 'styles_reviewContent'
                text_elem = article.find('div', class_=lambda x: x and 'styles_reviewContent' in x)
                text = text_elem.get_text(separator=" ", strip=True) if text_elem else ""
                
                # 3. Extraction de la date ISO
                time_elem = article.find('time')
                if time_elem and time_elem.get('datetime'):
                    date_full = time_elem.get('datetime')
                    date = date_full.split('T')[0] # Format YYYY-MM-DD
                else:
                    date = datetime.now().strftime('%Y-%m-%d')
                
                # Validation minimale pour la qualité de la donnée
                if text and len(text) > 10:
                    reviews.append({
                        'id': generate_review_id(brand, 'trustpilot', text, str(date)),
                        'brand': brand,
                        'source': 'trustpilot',
                        'date': date,
                        'note_brute': float(rating) if rating else None,
                        'texte': text,
                        'langue': None
                    })
                    
            except Exception as e:
                continue
        
        return reviews
        
    except Exception as e:
        print(f"❌ Erreur réseau sur {url}: {e}")
        return []

def scrape_trustpilot(brand="Huttopia", max_pages=5):
    """Boucle de pagination pour une marque donnée."""
    brand_urls = {
        "Huttopia": "https://fr.trustpilot.com/review/www.huttopia.com",
        "Homair": "https://fr.trustpilot.com/review/www.homair.com",
        "Sandaya": "https://fr.trustpilot.com/review/www.sandaya.fr",
    }
    
    base_url = brand_urls.get(brand)
    if not base_url:
        return pd.DataFrame()
    
    print(f"\n🚀 Lancement collecte {brand}...")
    all_reviews = []
    
    for page_num in range(1, max_pages + 1):
        url = base_url if page_num == 1 else f"{base_url}?page={page_num}"
        print(f"  📄 Page {page_num}/{max_pages}")
        
        reviews = scrape_trustpilot_page(url, brand)
        if not reviews:
            break
            
        all_reviews.extend(reviews)
        time.sleep(random.uniform(2, 4)) # Sécurité anti-bot
        
    return pd.DataFrame(all_reviews)

def main():
    # Définition du chemin de sortie relatif à la racine du projet
    # On monte d'un cran car le script est dans scraping/
    current_dir = os.path.dirname(__file__)
    output_dir = os.path.join(current_dir, "..", "data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    
    # Exécution pour Huttopia (Phase V1)
    brand = "Huttopia"
    df = scrape_trustpilot(brand=brand, max_pages=15) # ~300 avis
    
    if not df.empty:
        # Suppression des doublons de sécurité
        df = df.drop_duplicates(subset=['id'])
        
        file_path = os.path.join(output_dir, f"trustpilot_{brand.lower()}_raw.csv")
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        print(f"\n✅ TERMINÉ : {len(df)} avis collectés pour {brand}.")
        print(f"📂 Fichier disponible : {file_path}")
    else:
        print("❌ Échec de la collecte.")

if __name__ == "__main__":
    main()
"""
Scraper pour Booking.com - Collecte des avis Huttopia.
Optimisé pour Chromium sous Linux/Mac.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import hashlib
from datetime import datetime

class BookingScraper:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.driver = None

    def start(self):
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def generate_id(self, text, date):
        unique_str = f"booking_{text[:50]}_{date}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:12]

    def scrape_camping(self, url, brand="Huttopia"):
        print(f"🌐 Analyse de l'établissement : {url.split('/')[-1]}")
        
        # On force l'onglet des avis
        review_url = url if "tab=reviews" in url else url + "?tab=reviews"
        self.driver.get(review_url)
        
        time.sleep(5) # Temps de chargement du JS
        
        all_reviews = []
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # Sélecteurs data-testid (plus stables que les classes CSS)
        cards = soup.find_all('div', {'data-testid': 'review-card'})
        
        for card in cards:
            try:
                # Note sur 10 -> conversion sur 5
                score_tag = card.find('div', {'data-testid': 'review-score'})
                score_val = score_tag.get_text(strip=True).split()[-1].replace(',', '.') if score_tag else "10"
                note_5 = float(score_val) / 2
                
                # Texte (concaténation titre + corps)
                text_tag = card.find('div', {'data-testid': 'review-text'})
                text = text_tag.get_text(separator=" ", strip=True) if text_tag else ""
                
                # Date
                date_tag = card.find('div', class_=lambda x: x and 'review-date' in x)
                date_str = date_tag.get_text(strip=True) if date_tag else datetime.now().strftime("%Y-%m-%d")

                if len(text) > 10:
                    all_reviews.append({
                        'id': self.generate_id(text, date_str),
                        'brand': brand,
                        'source': 'Booking',
                        'date': date_str,
                        'note_brute': note_5,
                        'texte': text,
                        'langue': None
                    })
            except Exception as e:
                continue
                
        return all_reviews

    def stop(self):
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    # Liste d'exemples de campings Huttopia
    urls = [
        "https://www.booking.com/hotel/fr/huttopia-versailles.fr.html",
        "https://www.booking.com/hotel/fr/huttopia-dieulefit.fr.html"
    ]
    
    scraper = BookingScraper()
    scraper.start()
    
    results = []
    for url in urls:
        results.extend(scraper.scrape_camping(url))
        time.sleep(random.uniform(3, 6)) # Pause anti-bot
        
    scraper.stop()
    
    # Sauvegarde
    if results:
        df = pd.DataFrame(results)
        # On remonte d'un dossier pour aller dans data/raw
        out_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
        os.makedirs(out_path, exist_ok=True)
        
        file_name = f"{out_path}/booking_huttopia_raw.csv"
        df.to_csv(file_name, index=False, encoding='utf-8')
        print(f"✅ Succès : {len(df)} avis enregistrés dans {file_name}")
    else:
        print("❌ Aucun avis trouvé. Vérifiez les sélecteurs ou la connexion.")
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup  # <--- IL MANQUAIT CETTE LIGNE !
import pandas as pd
import time
import os
import random
from config_sites import CONFIG

class TripAdvisorScraper:
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

    def scrape_url(self, url, brand):
        print(f"🔎 TripAdvisor - Accès à : {url[:60]}...")
        self.driver.get(url)
        time.sleep(random.uniform(5, 8)) # Pause plus longue et aléatoire
        
        # SÉCURITÉ : On vérifie si on est bloqué
        if "Access Denied" in self.driver.page_source or "captcha" in self.driver.page_source.lower():
            print("⚠️ Blocage détecté (Captcha ou Access Denied).")
            return []

        results = []
        try:
            # Sélecteur ultra-large : on cherche tous les blocs qui contiennent 'review'
            # TripAdvisor change souvent ses classes, donc on cherche par attribut partiel
            cards = self.driver.find_elements(By.XPATH, "//div[contains(@data-automation, 'reviewCard')]")
            
            if not cards:
                # Tentative B : sélecteur de secours
                cards = self.driver.find_elements(By.CSS_SELECTOR, "div.ui_column.is-9")

            print(f"   📊 {len(cards)} avis potentiels détectés.")

            for card in cards:
                try:
                    # On utilise .text pour tout récupérer d'un coup comme sur Booking
                    raw_text = card.text
                    if len(raw_text) > 50: # On ignore les blocs vides ou trop courts
                        results.append({
                            "brand": brand,
                            "source": "TripAdvisor",
                            "date": time.strftime("%Y-%m-%d"),
                            "note_brute": None, # On extraira la note au nettoyage
                            "texte": raw_text.replace('\n', ' ')
                        })
                except:
                    continue
        except Exception as e:
            print(f"   ❌ Erreur d'extraction : {e}")
            
        return results

    def scrape_brand(self, brand):
        """Boucle sur toutes les URLs TripAdvisor de la marque"""
        from config_sites import CONFIG
        urls = CONFIG[brand].get("tripadvisor_urls", [])
        all_brand_reviews = []
        
        for url in urls:
            print(f"🚀 TripAdvisor - Tentative sur : {url[:60]}...")
            reviews = self.scrape_url(url, brand)
            if reviews:
                all_brand_reviews.extend(reviews)
            time.sleep(random.uniform(5, 8)) # Sécurité anti-bot
            
        return pd.DataFrame(all_brand_reviews)

if __name__ == "__main__":
    scraper = TripAdvisorScraper()
    # Maintenant scrape_brand existe et va appeler scrape_url pour chaque lien
    df = scraper.scrape_brand("Huttopia")
    scraper.driver.quit()
    
    if not df.empty:
        os.makedirs("../data/raw", exist_ok=True)
        df.to_csv("../data/raw/tripadvisor_huttopia_raw.csv", index=False, encoding='utf-8-sig')
        print(f"✅ Terminé : {len(df)} avis TripAdvisor collectés.")
    else:
        print("❌ Toujours aucun avis récupéré sur TripAdvisor.")
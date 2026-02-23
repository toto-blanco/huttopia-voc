from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re
from config_sites import CONFIG

class BookingScraper:
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # On force le chemin si Anaconda est perdu
        if os.path.exists("/usr/bin/google-chrome"):
            options.binary_location = "/usr/bin/google-chrome"
        elif os.path.exists("/usr/bin/chromium-browser"):
            options.binary_location = "/usr/bin/chromium-browser"

        # Le "Service" permet de lier le driver au binaire Chrome trouvé
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation du Driver : {e}")
            # Fallback manuel au cas où
            self.driver = webdriver.Chrome(options=options)

    def extract_site_name(self, url):
        """Extrait un nom lisible à partir de l'URL Booking"""
        # Exemple: .../hotel/fr/huttopia-versailles.fr.html -> Versailles
        match = re.search(r'huttopia-([^.]+)', url)
        if match:
            name = match.group(1).replace('-', '_').capitalize()
            return name
        return "Inconnu"

    def scrape_brand(self, brand):
        urls = CONFIG[brand]["booking_urls"]
        raw_data_dir = "../data/raw"
        os.makedirs(raw_data_dir, exist_ok=True)
        
        all_data = []

        for url in urls:
            site_name = self.extract_site_name(url)
            print(f"🔎 Booking - Analyse de {site_name} : {url[:50]}...")
            
            self.driver.get(url)
            time.sleep(5) 
            
            site_reviews = []
            try:
                # Detection des cards d'avis
                cards = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="review-card"]')
                print(f"   📊 {len(cards)} avis détectés pour {site_name}")

                for card in cards:
                    try:
                        # 1. Note
                        try:
                            score = card.find_element(By.CSS_SELECTOR, 'div[data-testid="review-score"] [class*="b5cd09854d"]').text
                        except:
                            try:
                                score = card.find_element(By.CSS_SELECTOR, 'div[data-testid="review-score"]').text
                            except:
                                score = "N/A"

                        # 2. Texte (on cherche le corps du commentaire)
                        try:
                            # On cible spécifiquement la partie textuelle de l'avis
                            review_text_element = card.find_element(By.CSS_SELECTOR, 'div[data-testid="review-text"]')
                            texte_final = review_text_element.text.replace('\n', ' ')
                        except:
                            # Fallback sur le texte global si la div spécifique manque
                            full_text = card.text
                            lines = [l.strip() for l in full_text.split('\n') if len(l.strip()) > 15]
                            texte_final = " ".join(lines)

                        data_line = {
                            "brand": brand,
                            "nom_etablissement": site_name, # <-- NOUVEAU
                            "source": "Booking",
                            "note_brute": score,
                            "texte": texte_final
                        }
                        site_reviews.append(data_line)
                        all_data.append(data_line)
                    except:
                        continue
                
                # Sauvegarde d'un fichier PAR SITE (comme pour Google)
                if site_reviews:
                    df_site = pd.DataFrame(site_reviews)
                    file_name = f"booking_{site_name.lower()}_raw.csv"
                    df_site.to_csv(os.path.join(raw_data_dir, file_name), index=False, encoding='utf-8-sig')
                    print(f"   💾 Fichier créé : {file_name}")

            except Exception as e:
                print(f"   ⚠️ Erreur sur {site_name}: {e}")
            
        return pd.DataFrame(all_data)

if __name__ == "__main__":
    scraper = BookingScraper()
    df_total = scraper.scrape_brand("Huttopia")
    scraper.driver.quit()
    print(f"🏁 FINI. Total consolidé : {len(df_total)} avis Booking extraits.")
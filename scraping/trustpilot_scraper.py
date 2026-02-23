from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import random
from config_sites import CONFIG

class TrustpilotScraperSelenium:
    def __init__(self, brand):
        self.brand = brand
        self.base_url = CONFIG[brand]["trustpilot_url"].split('?')[0].rstrip('/')
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

    def scrape(self, max_pages=3):
        all_reviews = []
        
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}?page={page}&sort=recency"
            print(f"🔎 Selenium - Ouverture Page {page}...")
            
            self.driver.get(url)
            time.sleep(random.uniform(4, 6)) # On laisse le JS s'exécuter
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            articles = soup.find_all('article')
            
            if not articles:
                print("⏹️ Aucun avis détecté sur cette page.")
                break
                
            print(f"✅ {len(articles)} avis trouvés.")
            
            for art in articles:
                # Sélecteurs basés sur les attributs data-testid de Trustpilot
                rating_tag = art.find('div', attrs={'data-service-review-rating': True})
                text_tag = art.find('p', attrs={'data-review-content-typography': True})
                date_tag = art.find('time')
                
                if text_tag:
                    all_reviews.append({
                        "brand": self.brand,
                        "source": "Trustpilot",
                        "date": date_tag['datetime'].split('T')[0] if date_tag else None,
                        "note_brute": rating_tag.get('data-service-review-rating') if rating_tag else None,
                        "texte": text_tag.get_text(strip=True)
                    })
            
            if len(articles) < 10: # Si la page est presque vide, on a fini
                break
                
        self.driver.quit()
        return pd.DataFrame(all_reviews)

if __name__ == "__main__":
    scraper = TrustpilotScraperSelenium("Huttopia")
    df = scraper.scrape(max_pages=3)
    
    if not df.empty:
        os.makedirs("../data/raw", exist_ok=True)
        df.to_csv("../data/raw/trustpilot_huttopia_raw.csv", index=False)
        print(f"🎉 VICTOIRE : {len(df)} avis collectés au total.")
    else:
        print("❌ Toujours rien. Le site est peut-être en train de te bloquer ton IP.")
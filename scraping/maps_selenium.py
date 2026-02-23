import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class GoogleMapsScraper:
    def __init__(self, headless=False):
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        
        # Optimisations Linux & Anti-détection
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--lang=fr")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        self.wait = WebDriverWait(self.driver, 20)

    def scrape_site(self, name, query, max_reviews=100):
        search_url = f"https://www.google.fr/maps/search/{query.replace(' ', '+')}"
        print(f"\n🚀 Destination : {name}")
        self.driver.get(search_url)
        
        # 1. Gestion des cookies
        try:
            time.sleep(3)
            btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Tout accepter')]")
            btn.click()
            print("✅ Cookies acceptés")
        except:
            pass

        reviews_data = []
        try:
            # 2. Ouverture de l'onglet Avis
            time.sleep(4)
            selectors = [
                "//button[contains(@aria-label, 'Avis de')]",
                "//button[contains(., 'Avis')]",
                "//span[contains(text(), 'Avis')]/ancestor::button"
            ]
            
            for sel in selectors:
                try:
                    target = self.driver.find_element(By.XPATH, sel)
                    self.driver.execute_script("arguments[0].click();", target)
                    print(f"✅ Onglet Avis cliqué")
                    break
                except: continue

            # 3. Identification de la zone de scroll
            print("⏳ Attente du chargement de la liste d'avis...")
            scrollable_div = None
            for _ in range(5):
                try:
                    time.sleep(2)
                    scrollable_div = self.driver.find_element(By.CSS_SELECTOR, "div.m678Wc, div.DxyBCb, div[role='main']")
                    if scrollable_div:
                        print("✅ Zone de scroll identifiée")
                        break
                except:
                    continue

            if not scrollable_div:
                scrollable_div = self.driver.switch_to.active_element

            # 4. Scrolling dynamique (Version Autonome)
            final_elements = []
            loaded = 0
            
            # --- FORCE LE FOCUS ---
            try:
                # On clique au milieu de la zone de scroll pour donner le focus à Chrome
                self.driver.execute_script("arguments[0].click();", scrollable_div)
                print("🖱️ Focus forcé sur la zone d'avis")
            except: pass

            for i in range(30): # Un peu plus d'itérations pour atteindre 100
                try:
                    # Méthode 1 : Scroll par JavaScript
                    self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                    
                    # Méthode 2 : Simulation de touche (plus "humaine" pour Google)
                    from selenium.webdriver.common.keys import Keys
                    scrollable_div.send_keys(Keys.PAGE_DOWN)
                    
                    time.sleep(2) # Laisse le temps au contenu de charger
                    
                    final_elements = self.driver.find_elements(By.XPATH, "//div[@data-review-id]")
                    
                    # Si ça ne charge plus, on tente un "secouage" de scroll
                    if len(final_elements) == loaded:
                        self.driver.execute_script('arguments[0].scrollTop -= 500', scrollable_div)
                        time.sleep(0.5)
                        self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                    
                    loaded = len(final_elements)
                    print(f"   📥 Avis détectés : {loaded}/{max_reviews}", end="\r")
                    
                    if loaded >= max_reviews: 
                        print(f"\n✅ Objectif atteint : {loaded} avis détectés.")
                        break
                except Exception as e:
                    # En cas de perte de l'élément, on le ré-identifie
                    scrollable_div = self.driver.find_element(By.CSS_SELECTOR, "div.m678Wc, div.DxyBCb")

            # 5. Extraction par "Moissonnage" + Recherche de Note Profonde
            print(f"\n✨ Extraction de {len(final_elements)} avis...")
            seen_texts = set()
            
            for el in final_elements:
                if len(reviews_data) >= max_reviews: break
                
                try:
                    # 1. Déplier le texte "Plus"
                    try:
                        more_btn = el.find_element(By.XPATH, ".//button[contains(., 'Plus')]")
                        self.driver.execute_script("arguments[0].click();", more_btn)
                    except: pass

                    # 2. NOTE : Méthode par classes CSS connues + secours
                    stars = "N/A"
                    try:
                        # Test 1 : La classe classique pour les étoiles (souvent kvH3ed)
                        # On cherche l'élément qui contient l'attribut de notation
                        star_elements = el.find_elements(By.CSS_SELECTOR, ".kvH3ed, .ui_bubble_rating, [class*='rating']")
                        for s_el in star_elements:
                            label = s_el.get_attribute("aria-label") or s_el.text
                            match = re.search(r'\d', label)
                            if match:
                                stars = match.group()
                                break
                        
                        # Test 2 : Si N/A, on cherche une image avec un alt text (parfois utilisé en fallback)
                        if stars == "N/A":
                            img_star = el.find_element(By.XPATH, ".//img[contains(@src, 'rating')]")
                            alt = img_star.get_attribute("alt")
                            stars = re.search(r'\d', alt).group()
                    except:
                        # Test 3 : Recherche désespérée - On prend le premier chiffre isolé < 6 
                        # trouvé dans les 10 premières balises span (souvent la note est là)
                        try:
                            spans = el.find_elements(By.TAG_NAME, "span")[:10]
                            for s in spans:
                                if s.text.isdigit() and 0 < int(s.text) <= 5:
                                    stars = s.text
                                    break
                        except: pass

                    # 3. TEXTE : Moissonnage (déjà fonctionnel chez toi)
                    potential_texts = el.find_elements(By.TAG_NAME, "span")
                    text_content = [t.text.strip() for t in potential_texts if len(t.text.strip()) > 20]
                    
                    if not text_content:
                        potential_texts = el.find_elements(By.TAG_NAME, "div")
                        text_content = [t.text.strip() for t in potential_texts if len(t.text.strip()) > 20]

                    if text_content:
                        text = max(text_content, key=len).replace('\n', ' ')
                        
                        if text not in seen_texts:
                            seen_texts.add(text)
                            reviews_data.append({
                                "brand": "Huttopia",
                                "nom_etablissement": name,
                                "source": "Google Maps",
                                "note_brute": stars,
                                "texte": text
                            })
                            print(f"✅ Ok : {stars}⭐ - {text[:45]}...")
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"❌ Erreur critique : {e}")
        
        return pd.DataFrame(reviews_data)

if __name__ == "__main__":
    # CONFIGURATION DES CHEMINS PROJET
    BASE_DIR = "/home/toto/Documents/Personnel/Candidatures 2026/huttopia/projet_entretien/huttopia-voc"
    RAW_DATA_PATH = os.path.join(BASE_DIR, "data/raw")
    
    if not os.path.exists(RAW_DATA_PATH):
        os.makedirs(RAW_DATA_PATH)

    huttopia_sites = {
        "Versailles": "Huttopia Versailles",
        "Rambouillet": "Huttopia Rambouillet",
        "Sarlat": "Huttopia Sarlat",
        "Gorges_du_Verdon": "Huttopia Gorges du Verdon",
        "Dieulefit": "Huttopia Dieulefit",
        "Noirmoutier": "Huttopia Noirmoutier",
        "Arcachon": "Huttopia Arcachon",
        "Font_Romeu": "Huttopia Font Romeu",
        "Sud_Ardeche": "Huttopia Sud Ardèche",
        "Lac_Serre_Poncon": "Huttopia Lac de Serre-Ponçon"
    }

    scraper = GoogleMapsScraper(headless=False)
    
    for name, query in huttopia_sites.items():
        df = scraper.scrape_site(name, query, max_reviews=100)
        if not df.empty:
            file_path = os.path.join(RAW_DATA_PATH, f"google_{name.lower()}_raw.csv")
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"💾 Sauvegardé : {name} ({len(df)} avis uniques)")
        else:
            print(f"⚠️ Aucun avis extrait pour {name}")

    scraper.driver.quit()
    print(f"\n🏁 Mission terminée. Tous les fichiers sont dans : {RAW_DATA_PATH}")
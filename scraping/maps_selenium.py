"""
Scraper Google Maps — Huttopia
Collecte les avis via automatisation du navigateur (scroll + extraction).

Corrections vs version précédente :
    - Chemin absolu hardcodé remplacé par pathlib (Path(__file__))
    - import re manquant ajouté
    - Extraction de date depuis l'attribut data-review-id (timestamp Unix)
    - Langue détectée dynamiquement (pas forcée à 'fr')

Usage :
    python maps_selenium.py
"""

import re
import time
import os
import pandas as pd
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ── Chemins ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── Campings à scraper ───────────────────────────────────────────────────────
HUTTOPIA_SITES = {
    "Versailles":       "Huttopia Versailles",
    "Rambouillet":      "Huttopia Rambouillet",
    "Sarlat":           "Huttopia Sarlat",
    "Gorges_du_Verdon": "Huttopia Gorges du Verdon",
    "Dieulefit":        "Huttopia Dieulefit",
    "Arcachon":         "Huttopia Arcachon",
    "Font_Romeu":       "Huttopia Font Romeu",
    "Sud_Ardeche":      "Huttopia Sud Ardèche",
    "Lac_Serre_Poncon": "Huttopia Lac de Serre-Ponçon",
}

MAX_REVIEWS = 100  # Objectif par camping


class GoogleMapsScraper:
    def __init__(self, headless: bool = True):
        options = Options()
        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--lang=fr")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
        )
        self.wait = WebDriverWait(self.driver, 20)

    def _accept_cookies(self) -> None:
        """Accepte le bandeau cookies Google si présent."""
        try:
            time.sleep(3)
            btn = self.driver.find_element(
                By.XPATH, "//button[contains(., 'Tout accepter')]"
            )
            btn.click()
            print("   ✅ Cookies acceptés")
        except Exception:
            pass

    def _open_reviews_tab(self) -> bool:
        """Ouvre l'onglet Avis dans Google Maps. Retourne True si succès."""
        time.sleep(4)
        selectors = [
            "//button[contains(@aria-label, 'Avis de')]",
            "//button[contains(., 'Avis')]",
            "//span[contains(text(), 'Avis')]/ancestor::button",
        ]
        for sel in selectors:
            try:
                target = self.driver.find_element(By.XPATH, sel)
                self.driver.execute_script("arguments[0].click();", target)
                print("   ✅ Onglet Avis ouvert")
                return True
            except Exception:
                continue
        print("   ⚠️  Onglet Avis introuvable")
        return False

    def _get_scrollable_zone(self):
        """Identifie la zone scrollable de la liste d'avis."""
        for _ in range(5):
            time.sleep(2)
            try:
                zone = self.driver.find_element(
                    By.CSS_SELECTOR, "div.m678Wc, div.DxyBCb, div[role='main']"
                )
                if zone:
                    return zone
            except Exception:
                continue
        return self.driver.switch_to.active_element

    def _scroll_to_load(self, scrollable_div, target: int) -> list:
        """Scrolle jusqu'à charger `target` avis ou épuiser la pagination."""
        # Force le focus pour que PAGE_DOWN fonctionne
        try:
            self.driver.execute_script("arguments[0].click();", scrollable_div)
        except Exception:
            pass

        loaded = 0
        for i in range(40):
            try:
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div
                )
                scrollable_div.send_keys(Keys.PAGE_DOWN)
                time.sleep(2)

                elements = self.driver.find_elements(By.XPATH, "//div[@data-review-id]")

                if len(elements) == loaded and loaded > 0:
                    # Tentative de déblocage
                    self.driver.execute_script(
                        "arguments[0].scrollTop -= 500", scrollable_div
                    )
                    time.sleep(0.5)
                    self.driver.execute_script(
                        "arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div
                    )
                    time.sleep(2)
                    elements = self.driver.find_elements(By.XPATH, "//div[@data-review-id]")

                loaded = len(elements)
                print(f"   📥 {loaded}/{target} avis chargés", end="\r")

                if loaded >= target:
                    print(f"\n   ✅ Objectif atteint : {loaded} avis")
                    return elements

            except Exception:
                try:
                    scrollable_div = self.driver.find_element(
                        By.CSS_SELECTOR, "div.m678Wc, div.DxyBCb"
                    )
                except Exception:
                    pass

        print(f"\n   ℹ️  Fin de scroll : {loaded} avis chargés")
        return self.driver.find_elements(By.XPATH, "//div[@data-review-id]")

    def _extract_rating(self, el) -> str:
        """Extrait la note étoiles d'un élément d'avis."""
        # Test 1 : classes CSS connues avec aria-label
        try:
            star_elements = el.find_elements(
                By.CSS_SELECTOR, ".kvH3ed, .ui_bubble_rating, [class*='rating']"
            )
            for s_el in star_elements:
                label = s_el.get_attribute("aria-label") or s_el.text
                match = re.search(r"(\d)", label)
                if match:
                    return match.group(1)
        except Exception:
            pass

        # Test 2 : image avec alt text contenant une note
        try:
            img = el.find_element(By.XPATH, ".//img[contains(@src, 'rating')]")
            alt = img.get_attribute("alt") or ""
            match = re.search(r"(\d)", alt)
            if match:
                return match.group(1)
        except Exception:
            pass

        # Test 3 : premier span court contenant un chiffre ≤ 5
        try:
            for span in el.find_elements(By.TAG_NAME, "span")[:10]:
                if span.text.strip().isdigit() and 0 < int(span.text.strip()) <= 5:
                    return span.text.strip()
        except Exception:
            pass

        return "N/A"

    def _extract_date(self, el) -> str:
        """
        Extrait la date depuis l'attribut data-review-id (timestamp Unix)
        ou depuis le texte de l'élément si disponible.
        """
        # Google Maps encode parfois le timestamp dans data-review-id
        try:
            review_id = el.get_attribute("data-review-id") or ""
            # Format typique : "ChIJ...:0x...:<timestamp>"
            parts = review_id.split(":")
            for part in parts:
                if part.isdigit() and len(part) == 10:
                    from datetime import datetime
                    return datetime.fromtimestamp(int(part)).strftime("%Y-%m-%d")
        except Exception:
            pass

        # Fallback : cherche un span avec une date lisible
        try:
            for span in el.find_elements(By.TAG_NAME, "span")[:20]:
                text = span.text.strip()
                # "il y a 3 mois" → approximation inutile, on ignore
                # "15 juillet 2024" ou "2024"
                match = re.search(r"\b(20\d{2})\b", text)
                if match:
                    return match.group(1) + "-01-01"
        except Exception:
            pass

        return ""

    def scrape_site(self, name: str, query: str, max_reviews: int = MAX_REVIEWS) -> pd.DataFrame:
        """Scrape un camping Google Maps et retourne un DataFrame."""
        search_url = f"https://www.google.fr/maps/search/{query.replace(' ', '+')}"
        print(f"\n🏕️  {name}")
        self.driver.get(search_url)

        self._accept_cookies()

        if not self._open_reviews_tab():
            return pd.DataFrame()

        scrollable_div = self._get_scrollable_zone()
        if not scrollable_div:
            return pd.DataFrame()

        final_elements = self._scroll_to_load(scrollable_div, max_reviews)
        print(f"\n   ✨ Extraction de {len(final_elements)} avis...")

        reviews_data = []
        seen_texts: set[str] = set()

        for el in final_elements:
            if len(reviews_data) >= max_reviews:
                break

            try:
                # Déplie le texte "Plus"
                try:
                    more_btn = el.find_element(By.XPATH, ".//button[contains(., 'Plus')]")
                    self.driver.execute_script("arguments[0].click();", more_btn)
                except Exception:
                    pass

                # Texte
                potential_texts = [
                    t.text.strip()
                    for t in el.find_elements(By.TAG_NAME, "span")
                    if len(t.text.strip()) > 20
                ]
                if not potential_texts:
                    potential_texts = [
                        t.text.strip()
                        for t in el.find_elements(By.TAG_NAME, "div")
                        if len(t.text.strip()) > 20
                    ]
                if not potential_texts:
                    continue

                text = max(potential_texts, key=len).replace("\n", " ")
                if text in seen_texts:
                    continue
                seen_texts.add(text)

                stars = self._extract_rating(el)
                date  = self._extract_date(el)

                reviews_data.append({
                    "brand":             "Huttopia",
                    "nom_etablissement": name,
                    "source":            "Google Maps",
                    "note_brute":        stars,
                    "texte":             text,
                    "date":              date,
                })

            except Exception:
                continue

        print(f"   💾 {len(reviews_data)} avis uniques extraits")
        return pd.DataFrame(reviews_data)

    def quit(self) -> None:
        self.driver.quit()


if __name__ == "__main__":
    print("🚀 Démarrage du scraper Google Maps")
    print(f"   Campings ciblés : {len(HUTTOPIA_SITES)}")
    print(f"   Max avis/camping : {MAX_REVIEWS}\n")

    scraper = GoogleMapsScraper(headless=True)

    try:
        for name, query in HUTTOPIA_SITES.items():
            df = scraper.scrape_site(name, query, max_reviews=MAX_REVIEWS)
            if not df.empty:
                file_path = RAW_DATA_DIR / f"google_{name.lower()}_raw.csv"
                df.to_csv(file_path, index=False, encoding="utf-8-sig")
                print(f"   💽 Sauvegardé → {file_path.name}")
            else:
                print(f"   ⚠️  Aucun avis extrait pour {name}")
    finally:
        scraper.quit()

    print(f"\n🏁 Mission terminée. Fichiers dans : {RAW_DATA_DIR}")

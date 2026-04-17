"""
Scraper Booking.com — Huttopia
Collecte les avis avec pagination (jusqu'à MAX_REVIEWS_PER_SITE avis par camping).

Améliorations vs version précédente :
    - Pagination : charge toutes les pages disponibles
    - Extraction de la date depuis le texte brut de la card
    - Chemins relatifs via pathlib (fonctionne peu importe le répertoire de lancement)
    - Gestion d'erreurs robuste sans crash silencieux

Usage :
    python booking_scraper.py
"""

import re
import time
import random
import os
import pandas as pd
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ── Chemins ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── Config ───────────────────────────────────────────────────────────────────
MAX_REVIEWS_PER_SITE = 50    # Plafond par camping
REVIEWS_PER_PAGE     = 10    # Booking affiche ~10 avis par page
MAX_PAGES            = MAX_REVIEWS_PER_SITE // REVIEWS_PER_PAGE
DELAY_PAGE           = (3.0, 6.0)  # (min, max) secondes entre les pages
DELAY_SITE           = (5.0, 9.0)  # (min, max) secondes entre les campings

BOOKING_URLS = {
    "Versailles":      "https://www.booking.com/hotel/fr/huttopia-versailles.fr.html#tab-reviews",
    "Dieulefit":       "https://www.booking.com/hotel/fr/huttopia-dieulefit.fr.html#tab-reviews",
    "Sarlat":          "https://www.booking.com/hotel/fr/huttopia-sarlat.fr.html#tab-reviews",
    "Gorges_du_Verdon":"https://www.booking.com/hotel/fr/huttopia-gorges-du-verdon.fr.html#tab-reviews",
    "Le_Moulin":       "https://www.booking.com/hotel/fr/huttopia-le-moulin.fr.html#tab-reviews",
    "Rambouillet":     "https://www.booking.com/hotel/fr/huttopia-rambouillet.fr.html#tab-reviews",
    "Arcachon":        "https://www.booking.com/hotel/fr/huttopia-arcachon.fr.html#tab-reviews",
    "Font_Romeu":      "https://www.booking.com/hotel/fr/huttopia-font-romeu.fr.html#tab-reviews",
    "Sud_Ardeche":     "https://www.booking.com/hotel/fr/village-huttopia-sud-ardeche.fr.html#tab-reviews",
    "Lac_Serre_Poncon":"https://www.booking.com/hotel/fr/camping-le-lac-serre-poncon.fr.html#tab-reviews",
}

# Mois français → numéro (pour parser les dates)
MOIS_FR = {
    "janvier": "01", "février": "02", "mars": "03", "avril": "04",
    "mai": "05", "juin": "06", "juillet": "07", "août": "08",
    "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12",
}


def _build_driver() -> webdriver.Chrome:
    """Initialise Chrome en mode headless avec options anti-détection minimales."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def _extract_date(raw_text: str) -> str:
    """
    Extrait une date depuis le texte brut d'une card Booking.

    Formats attendus :
        "Commentaire envoyé le 5 juillet 2024"
        "juillet 2024"
        "7 nuits · juillet 2024"
    """
    # Pattern avec jour explicite : "5 juillet 2024"
    match = re.search(
        r"(\d{1,2})\s+(" + "|".join(MOIS_FR.keys()) + r")\s+(\d{4})",
        raw_text,
        re.IGNORECASE,
    )
    if match:
        day   = match.group(1).zfill(2)
        month = MOIS_FR[match.group(2).lower()]
        year  = match.group(3)
        return f"{year}-{month}-{day}"

    # Pattern sans jour : "juillet 2024" → premier du mois
    match = re.search(
        r"(" + "|".join(MOIS_FR.keys()) + r")\s+(\d{4})",
        raw_text,
        re.IGNORECASE,
    )
    if match:
        month = MOIS_FR[match.group(1).lower()]
        year  = match.group(2)
        return f"{year}-{month}-01"

    return ""


def _extract_note(card, driver: webdriver.Chrome) -> str:
    """Extrait la note numérique d'une card Booking."""
    selectors = [
        'div[data-testid="review-score"] [class*="b5cd09854d"]',
        'div[data-testid="review-score"]',
        '[class*="bui-review-score__badge"]',
    ]
    for sel in selectors:
        try:
            el = card.find_element(By.CSS_SELECTOR, sel)
            text = el.text.strip()
            if text:
                return text
        except Exception:
            continue
    return "N/A"


def _click_next_page(driver: webdriver.Chrome, wait: WebDriverWait) -> bool:
    """
    Clique sur le bouton 'Page suivante' de la section avis.
    Retourne True si le clic a réussi, False si plus de page suivante.
    """
    next_selectors = [
        'button[aria-label*="page suivante"]',
        'button[aria-label*="next"]',
        '[data-testid="review-next-page-button"]',
        'button[class*="pagenext"]',
    ]
    for sel in next_selectors:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
            driver.execute_script("arguments[0].click();", btn)
            return True
        except Exception:
            continue
    return False


def scrape_site(name: str, url: str, driver: webdriver.Chrome) -> list[dict]:
    """Scrape un camping Booking sur plusieurs pages."""
    wait     = WebDriverWait(driver, 15)
    reviews  = []
    seen     : set[str] = set()

    print(f"\n🏕️  {name}")
    driver.get(url)
    time.sleep(random.uniform(4, 6))

    # Scroll vers l'onglet avis pour déclencher le chargement lazy
    try:
        reviews_tab = driver.find_element(By.CSS_SELECTOR, '[data-tab="reviews"]')
        driver.execute_script("arguments[0].scrollIntoView();", reviews_tab)
        time.sleep(2)
    except Exception:
        pass

    for page in range(1, MAX_PAGES + 1):
        cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="review-card"]')
        print(f"   📄 Page {page} — {len(cards)} cards détectées")

        page_new = 0
        for card in cards:
            try:
                raw_text = card.text.strip()
                if len(raw_text) < 20:
                    continue

                # Texte principal de l'avis (on retire les métadonnées)
                try:
                    review_div = card.find_element(By.CSS_SELECTOR, 'div[data-testid="review-text"]')
                    text = review_div.text.strip().replace("\n", " ")
                except Exception:
                    lines = [l.strip() for l in raw_text.split("\n") if len(l.strip()) > 15]
                    text  = " ".join(lines)

                if not text or text in seen:
                    continue
                seen.add(text)

                note = _extract_note(card, driver)
                date = _extract_date(raw_text)

                reviews.append({
                    "brand":             "Huttopia",
                    "nom_etablissement": name,
                    "source":            "Booking",
                    "note_brute":        note,
                    "texte":             text,
                    "date":              date,
                })
                page_new += 1

            except Exception:
                continue

        print(f"   ✅ +{page_new} nouveaux avis (total : {len(reviews)})")

        if len(reviews) >= MAX_REVIEWS_PER_SITE:
            print(f"   🎯 Plafond de {MAX_REVIEWS_PER_SITE} atteint")
            break

        if page < MAX_PAGES:
            if not _click_next_page(driver, wait):
                print(f"   ℹ️  Pas de page suivante — fin de pagination")
                break
            time.sleep(random.uniform(*DELAY_PAGE))

    return reviews


def scrape_all() -> pd.DataFrame:
    """Scrape tous les campings et renvoie un DataFrame consolidé."""
    driver   = _build_driver()
    all_data : list[dict] = []

    try:
        for name, url in BOOKING_URLS.items():
            reviews = scrape_site(name, url, driver)

            if reviews:
                df_site  = pd.DataFrame(reviews)
                out_path = RAW_DATA_DIR / f"booking_{name.lower()}_raw.csv"
                df_site.to_csv(out_path, index=False, encoding="utf-8-sig")
                print(f"   💽 Sauvegardé → {out_path.name}")
                all_data.extend(reviews)

            time.sleep(random.uniform(*DELAY_SITE))
    finally:
        driver.quit()

    return pd.DataFrame(all_data)


if __name__ == "__main__":
    print("🚀 Démarrage du scraper Booking")
    print(f"   Campings ciblés : {len(BOOKING_URLS)}")
    print(f"   Max avis/camping : {MAX_REVIEWS_PER_SITE}\n")

    df = scrape_all()

    if not df.empty:
        out_path = RAW_DATA_DIR / "booking_huttopia_all_raw.csv"
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"\n🏁 Terminé — {len(df)} avis Booking collectés")
        print(f"   Fichier consolidé → {out_path}")
        print(f"\n   Répartition par camping :")
        print(df["nom_etablissement"].value_counts().to_string())
    else:
        print("\n❌ Aucun avis collecté.")

"""
Scraper Trustpilot — Huttopia
Utilise Selenium pour rendre la page (contourne le 403), puis extrait
les avis depuis le JSON-LD injecté par Trustpilot dans le HTML rendu.

Usage :
    python trustpilot_scraper.py
"""

import json
import time
import random
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ── Chemins ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── Config ───────────────────────────────────────────────────────────────────
BASE_URL  = "https://fr.trustpilot.com/review/huttopia.com"
MAX_PAGES = 5
DELAY_MIN = 3.0
DELAY_MAX = 5.0


def _build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def _extract_reviews_from_jsonld(html: str) -> list[dict]:
    """
    Parse le HTML rendu par Selenium et extrait les avis depuis
    les balises <script type='application/ld+json'>.

    Structure Trustpilot : @graph est une liste plate où les avis
    sont des éléments @type=Review directement (pas imbriqués dans LocalBusiness).
    """
    soup    = BeautifulSoup(html, "html.parser")
    reviews = []

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.get_text() or "")
        except (json.JSONDecodeError, TypeError):
            continue

        objects = data if isinstance(data, list) else [data]

        for obj in objects:
            if not isinstance(obj, dict):
                continue

            # @graph est une liste plate — on parcourt tous les éléments
            graph = obj.get("@graph", [])
            if isinstance(graph, dict):
                graph = [graph]

            for item in graph:
                if not isinstance(item, dict):
                    continue
                if item.get("@type") == "Review":
                    parsed = _parse_review(item)
                    if parsed:
                        reviews.append(parsed)

    return reviews


def _parse_review(r: dict) -> dict | None:
    """Normalise un élément @type=Review du JSON-LD Trustpilot."""
    text = r.get("reviewBody", "").strip()
    if not text:
        return None

    rating_obj = r.get("reviewRating", {})
    note       = str(rating_obj.get("ratingValue", "N/A"))
    date       = r.get("datePublished", "")[:10]
    headline   = r.get("headline", "").strip()
    lang       = r.get("inLanguage", "fr")

    return {
        "brand":             "Huttopia",
        "nom_etablissement": "Marque Globale",
        "source":            "Trustpilot",
        "note_brute":        note,
        "texte":             text,
        "date":              date,
        "headline":          headline,
        "langue":            lang,
    }


def scrape_trustpilot() -> pd.DataFrame:
    driver      = _build_driver()
    all_reviews : list[dict] = []
    seen_texts  : set[str]   = set()

    print("🔍 Trustpilot — Selenium + extraction JSON-LD")

    try:
        for page in range(1, MAX_PAGES + 1):
            url = f"{BASE_URL}?page={page}&sort=recency"
            print(f"   📄 Page {page} — {url}")

            driver.get(url)
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

            page_reviews = _extract_reviews_from_jsonld(driver.page_source)

            if not page_reviews:
                print(f"   ℹ️  Aucun avis JSON-LD page {page} — fin de pagination")
                break

            new_count = 0
            for r in page_reviews:
                if r["texte"] not in seen_texts:
                    seen_texts.add(r["texte"])
                    all_reviews.append(r)
                    new_count += 1

            print(f"   ✅ +{new_count} nouveaux avis (total : {len(all_reviews)})")

            if new_count == 0:
                break

            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    finally:
        driver.quit()

    return pd.DataFrame(all_reviews)


if __name__ == "__main__":
    df = scrape_trustpilot()

    if not df.empty:
        out_path = RAW_DATA_DIR / "trustpilot_huttopia_raw.csv"
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"\n🏁 {len(df)} avis Trustpilot collectés → {out_path}")
        print(f"   Distribution des notes : {df['note_brute'].value_counts().to_dict()}")
    else:
        print("\n❌ Aucun avis collecté.")

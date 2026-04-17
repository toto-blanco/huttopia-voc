"""
Scraper Trustpilot — Huttopia
Extrait les avis depuis le JSON-LD structuré présent dans le HTML de la page.

Avantage : pas de navigateur nécessaire, pas de Selenium, pas de Scrapling.
Trustpilot expose les avis en Schema.org (@type: Review) directement dans le HTML.

Usage :
    python trustpilot_scraper.py
"""

import json
import re
import time
import random
import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup

# ── Chemins ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── Config ───────────────────────────────────────────────────────────────────
BASE_URL   = "https://fr.trustpilot.com/review/huttopia.com"
MAX_PAGES  = 5       # Trustpilot a peu d'avis Huttopia — 5 pages suffisent
DELAY_MIN  = 2.0
DELAY_MAX  = 4.0

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _fetch_page(url: str) -> BeautifulSoup | None:
    """Récupère une page et retourne un objet BeautifulSoup."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"   ❌ Erreur HTTP : {e}")
        return None


def _extract_reviews_from_jsonld(soup: BeautifulSoup) -> list[dict]:
    """
    Extrait les avis depuis les balises <script type='application/ld+json'>.

    Trustpilot injecte un objet LocalBusiness contenant un tableau 'review'
    avec tous les avis de la page — note, texte, date, auteur.
    """
    reviews = []

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue

        # Le JSON-LD peut être un objet unique ou une liste
        objects = data if isinstance(data, list) else [data]

        for obj in objects:
            # Cas 1 : @graph contient plusieurs types
            graph = obj.get("@graph", [])
            for item in graph:
                if item.get("@type") == "LocalBusiness":
                    reviews.extend(_parse_business_reviews(item))

            # Cas 2 : l'objet racine est directement un LocalBusiness
            if obj.get("@type") == "LocalBusiness":
                reviews.extend(_parse_business_reviews(obj))

    return reviews


def _parse_business_reviews(business: dict) -> list[dict]:
    """Extrait et normalise les avis depuis un objet LocalBusiness JSON-LD."""
    parsed = []
    raw_reviews = business.get("review", [])

    for r in raw_reviews:
        if r.get("@type") != "Review":
            continue

        # Texte
        text = r.get("reviewBody", "").strip()
        if not text:
            continue

        # Note (1 à 5)
        rating_obj = r.get("reviewRating", {})
        note = str(rating_obj.get("ratingValue", "N/A"))

        # Date (ISO 8601 → YYYY-MM-DD)
        date_raw = r.get("datePublished", "")
        date = date_raw[:10] if date_raw else ""

        # Titre
        headline = r.get("headline", "").strip()

        # Langue
        lang = r.get("inLanguage", "fr")

        parsed.append({
            "brand":            "Huttopia",
            "nom_etablissement": "Marque Globale",
            "source":           "Trustpilot",
            "note_brute":       note,
            "texte":            text,
            "date":             date,
            "headline":         headline,
            "langue":           lang,
        })

    return parsed


def scrape_trustpilot() -> pd.DataFrame:
    """Scrape toutes les pages disponibles et retourne un DataFrame."""
    all_reviews: list[dict] = []
    seen_texts: set[str] = set()

    print("🔍 Trustpilot — extraction via JSON-LD")

    for page in range(1, MAX_PAGES + 1):
        url = f"{BASE_URL}?page={page}&sort=recency"
        print(f"   📄 Page {page} — {url}")

        soup = _fetch_page(url)
        if soup is None:
            break

        page_reviews = _extract_reviews_from_jsonld(soup)

        if not page_reviews:
            print(f"   ℹ️  Aucun avis JSON-LD trouvé page {page} — fin de pagination")
            break

        # Déduplication
        new_count = 0
        for r in page_reviews:
            if r["texte"] not in seen_texts:
                seen_texts.add(r["texte"])
                all_reviews.append(r)
                new_count += 1

        print(f"   ✅ +{new_count} nouveaux avis (total : {len(all_reviews)})")

        if new_count == 0:
            # Plus de nouveaux avis → on a atteint la fin
            break

        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

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
        print("   Trustpilot a peut-être changé sa structure JSON-LD.")
        print("   Inspecte le HTML brut avec : requests.get(BASE_URL).text")

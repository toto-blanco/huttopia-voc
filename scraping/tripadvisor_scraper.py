"""
Scraper TripAdvisor — Huttopia
Utilise Scrapling StealthyFetcher pour contourner la protection Cloudflare.

Dépendances :
    pip install "scrapling[fetchers]"
    scrapling install

Usage :
    python tripadvisor_scraper.py
"""

import re
import time
import random
import os
import pandas as pd
from pathlib import Path
from scrapling.fetchers import StealthyFetcher

# ── Chemins ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── Config ───────────────────────────────────────────────────────────────────
MAX_PAGES = 5          # Pages par camping (15 avis/page → ~75 avis max)
DELAY_MIN  = 3.0       # Secondes entre requêtes (min)
DELAY_MAX  = 6.0       # Secondes entre requêtes (max)

TRIPADVISOR_URLS = {
    "Versailles":       "https://www.tripadvisor.fr/Hotel_Review-g187148-d645632-Reviews-Camping_Huttopia_Versailles-Versailles_Yvelines_Ile_de_France.html",
    "Rambouillet":      "https://www.tripadvisor.fr/Hotel_Review-g1055982-d1109041-Reviews-Camping_Huttopia_Rambouillet-Rambouillet_Yvelines_Ile_de_France.html",
    "Dieulefit":        "https://www.tripadvisor.fr/Hotel_Review-g286341-d3451816-Reviews-Village_Huttopia_Dieulefit-Dieulefit_Drome_Auvergne_Rhone_Alpes.html",
    "Sarlat":           "https://www.tripadvisor.fr/Hotel_Review-g196508-d4759846-Reviews-Camping_Huttopia_Sarlat-Sarlat_la_Caneda_Dordogne_Nouvelle_Aquitaine.html",
    "Gorges_du_Verdon": "https://www.tripadvisor.fr/Hotel_Review-g677532-d2643808-Reviews-Camping_Huttopia_Gorges_du_Verdon-Castellane_Alpes_de_Haute_Provence_Provence_Alpes_Co.html",
    "Le_Moulin":        "https://www.tripadvisor.fr/Hotel_Review-g4206775-d4808574-Reviews-Camping_Huttopia_Le_Moulin-Saint_Julien_de_Peyrolas_Gard_Occitanie.html",
}


def _page_url(base_url: str, page: int) -> str:
    """Construit l'URL de pagination TripAdvisor.

    TripAdvisor pagine en insérant '-orN-' dans l'URL (N = offset).
    Page 1 → pas de suffixe, Page 2 → -or15-, Page 3 → -or30-, etc.
    """
    if page == 1:
        return base_url
    offset = (page - 1) * 15
    # Insère -orN- juste avant le dernier segment (nom du fichier .html)
    return re.sub(r"(Reviews-)", rf"\g<1>or{offset}-", base_url)


def _extract_rating(card) -> str:
    """Extrait la note d'une card d'avis TripAdvisor."""
    # Stratégie 1 : attribut aria-label sur l'élément de notation
    for selector in [
        "svg[aria-label]",
        "[class*='rating'] svg",
        "[data-automation='bubbleRatingValue']",
    ]:
        el = card.css_first(selector)
        if el:
            label = el.attrib.get("aria-label", "")
            match = re.search(r"(\d)[,.]?\d?\s*(sur|/|of|étoiles?|stars?)", label, re.I)
            if match:
                return match.group(1)

    # Stratégie 2 : cherche un chiffre seul entre 1 et 5 dans les spans courts
    for span in card.css("span"):
        text = span.text.strip()
        if text in {"1", "2", "3", "4", "5"}:
            return text

    return "N/A"


def _extract_text(card) -> str:
    """Extrait le corps textuel d'un avis, en privilégiant les éléments longs."""
    # Sélecteurs spécifiques au corps de l'avis
    for selector in [
        "[data-automation='reviewBody'] span",
        "[class*='reviewText'] span",
        "[class*='review-text'] span",
        "q span",  # TripAdvisor encapsule parfois le texte dans <q>
    ]:
        el = card.css_first(selector)
        if el and len(el.text.strip()) > 30:
            return el.text.strip().replace("\n", " ")

    # Fallback : le plus long span de la card
    candidates = [s.text.strip() for s in card.css("span") if len(s.text.strip()) > 30]
    if candidates:
        return max(candidates, key=len).replace("\n", " ")

    return ""


def _extract_date(card) -> str:
    """Extrait la date de l'avis (format YYYY-MM-DD si possible)."""
    for selector in [
        "time[datetime]",
        "[data-automation='reviewDate']",
        "[class*='date']",
    ]:
        el = card.css_first(selector)
        if el:
            dt = el.attrib.get("datetime", "") or el.text.strip()
            # Tente de normaliser au format YYYY-MM-DD
            match = re.search(r"(\d{4})-(\d{2})-(\d{2})", dt)
            if match:
                return match.group(0)
            # Format "mois YYYY" → approximation au 1er du mois
            match = re.search(r"(\w+)\s+(\d{4})", dt)
            if match:
                return f"{match.group(2)}-01-01"
    return ""


def scrape_site(name: str, base_url: str) -> list[dict]:
    """Scrape toutes les pages d'avis disponibles pour un camping donné."""
    all_reviews = []
    seen_texts: set[str] = set()

    print(f"\n🏕️  {name}")

    for page in range(1, MAX_PAGES + 1):
        url = _page_url(base_url, page)
        print(f"   📄 Page {page} — {url[:80]}...")

        try:
            response = StealthyFetcher.fetch(
                url,
                headless=True,
                network_idle=True,          # attend la fin des requêtes JS
                google_search=False,         # désactive le passage par Google
            )
        except Exception as e:
            print(f"   ❌ Erreur fetch page {page} : {e}")
            break

        # Détection de blocage
        if not response or len(response.html) < 1000:
            print(f"   ⚠️  Réponse vide ou trop courte — arrêt sur ce camping")
            break

        # Recherche des cards d'avis
        cards = response.css("[data-automation='reviewCard']")
        if not cards:
            # Sélecteur de secours (TripAdvisor modifie parfois ses attributs)
            cards = response.css("[class*='ReviewCard']")

        if not cards:
            print(f"   ℹ️  Aucune card trouvée page {page} — fin de pagination")
            break

        print(f"   ✅ {len(cards)} avis détectés")
        page_new = 0

        for card in cards:
            text = _extract_text(card)
            if not text or text in seen_texts:
                continue
            seen_texts.add(text)

            rating = _extract_rating(card)
            date   = _extract_date(card)

            all_reviews.append({
                "brand":            "Huttopia",
                "nom_etablissement": name,
                "source":           "TripAdvisor",
                "note_brute":       rating,
                "texte":            text,
                "date":             date,
            })
            page_new += 1

        print(f"   💾 +{page_new} nouveaux avis (total : {len(all_reviews)})")

        # Pause polie entre les pages
        if page < MAX_PAGES:
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    return all_reviews


def scrape_all() -> pd.DataFrame:
    """Point d'entrée principal — scrape tous les campings."""
    all_data: list[dict] = []

    for name, url in TRIPADVISOR_URLS.items():
        reviews = scrape_site(name, url)
        if reviews:
            # Sauvegarde intermédiaire par camping (sécurité en cas de crash)
            df_site = pd.DataFrame(reviews)
            out_path = RAW_DATA_DIR / f"tripadvisor_{name.lower()}_raw.csv"
            df_site.to_csv(out_path, index=False, encoding="utf-8-sig")
            print(f"   💽 Sauvegardé → {out_path.name}")
            all_data.extend(reviews)

        # Pause entre campings (plus longue pour éviter la détection)
        time.sleep(random.uniform(DELAY_MAX, DELAY_MAX + 3))

    return pd.DataFrame(all_data)


if __name__ == "__main__":
    print("🚀 Démarrage du scraper TripAdvisor (Scrapling StealthyFetcher)")
    print(f"   Campings ciblés : {len(TRIPADVISOR_URLS)}")
    print(f"   Pages max/camping : {MAX_PAGES} (~{MAX_PAGES * 15} avis max)\n")

    df = scrape_all()

    if not df.empty:
        out_path = RAW_DATA_DIR / "tripadvisor_huttopia_raw.csv"
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"\n🏁 Terminé — {len(df)} avis TripAdvisor collectés")
        print(f"   Fichier consolidé → {out_path}")
        print(f"\n   Répartition par camping :")
        print(df["nom_etablissement"].value_counts().to_string())
    else:
        print("\n❌ Aucun avis collecté.")
        print("   Vérifications suggérées :")
        print("   1. scrapling install (navigateurs Playwright installés ?)")
        print("   2. Tester une URL manuellement avec StealthyFetcher.fetch(url, headless=False)")

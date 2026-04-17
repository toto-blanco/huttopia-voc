"""
Fusion et normalisation des fichiers CSV bruts.

Lit tous les fichiers *_raw.csv depuis data/raw/, normalise les notes,
les noms d'établissements et les langues, puis produit un fichier
master consolidé dans data/processed/.

Usage :
    python data_merger.py
"""

import re
import pandas as pd
from pathlib import Path
from langdetect import detect, LangDetectException

# ── Chemins ──────────────────────────────────────────────────────────────────
PROJECT_ROOT   = Path(__file__).resolve().parent.parent
RAW_DIR        = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR  = PROJECT_ROOT / "data" / "processed"
OUTPUT_PATH    = PROCESSED_DIR / "huttopia_reviews_master.csv"

# ── Normalisation des noms d'établissements ──────────────────────────────────
# Corrige les doublons de casse et les variantes (Sud_Ardeche / Sud_ardeche)
ETABLISSEMENT_MAP = {
    "sud_ardeche":        "Sud_Ardeche",
    "gorges_du_verdon":   "Gorges_du_Verdon",
    "font_romeu":         "Font_Romeu",
    "lac_serre_poncon":   "Lac_Serre_Poncon",
    "le_moulin":          "Le_Moulin",
    "versailles":         "Versailles",
    "rambouillet":        "Rambouillet",
    "sarlat":             "Sarlat",
    "arcachon":           "Arcachon",
    "dieulefit":          "Dieulefit",
    "marque globale":     "Marque_Globale",
    "inconnu":            "Inconnu",
}


def normalize_etablissement(name: str) -> str:
    """Normalise un nom d'établissement vers la forme canonique."""
    if pd.isna(name):
        return "Inconnu"
    key = str(name).strip().lower()
    return ETABLISSEMENT_MAP.get(key, str(name).strip())


def clean_note_google(note_str, text: str = "") -> float:
    """Extrait la note Google (déjà sur /5). Fallback à 3.0 si N/A."""
    res = re.findall(r"(\d+(?:[.,]\d+)?)", str(note_str))
    if res:
        val = float(res[0].replace(",", "."))
        return min(val, 5.0)
    return 3.0


def clean_note_booking(note_str) -> float:
    """
    Normalise la note Booking sur /5.
    Booking affiche des notes sur /10 ("8,5") ou parfois directement /5.
    """
    if pd.isna(note_str):
        return 0.0
    res = re.findall(r"(\d+[.,]\d+|\d+)", str(note_str))
    if res:
        val = float(res[0].replace(",", "."))
        return round(val / 2, 2) if val > 5 else round(val, 2)
    return 0.0


def clean_note_trustpilot(note_str) -> float:
    """Note Trustpilot déjà sur /5 — extraction du chiffre."""
    res = re.findall(r"(\d)", str(note_str))
    if res:
        return float(res[0])
    return 3.0


def detect_language(text: str) -> str:
    """Détecte la langue d'un texte. Retourne 'unknown' en cas d'échec."""
    if not text or len(text.strip()) < 10:
        return "unknown"
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def process_file(file_path: Path) -> pd.DataFrame | None:
    """
    Charge et normalise un fichier CSV brut selon sa source.
    Retourne None si le fichier doit être ignoré (ex: fichier consolidé).
    """
    name = file_path.stem.lower()  # ex: "booking_versailles_raw"

    # Ignore le fichier consolidé Booking (contient tous les campings)
    if name == "booking_huttopia_all_raw":
        return None

    try:
        df = pd.read_csv(file_path, encoding="utf-8-sig")
    except Exception as e:
        print(f"   ❌ Erreur lecture {file_path.name} : {e}")
        return None

    if df.empty:
        return None

    # ── Détection de la source ────────────────────────────────────────────────
    if "google" in name:
        source = "Google Maps"
        df["note_std"] = df.apply(
            lambda r: clean_note_google(r.get("note_brute"), r.get("texte", "")), axis=1
        )
    elif "booking" in name:
        source = "Booking"
        df["note_std"] = df["note_brute"].apply(clean_note_booking)
    elif "trustpilot" in name:
        source = "Trustpilot"
        df["note_std"] = df["note_brute"].apply(clean_note_trustpilot)
        if "nom_etablissement" not in df.columns:
            df["nom_etablissement"] = "Marque_Globale"
    else:
        source = "Inconnue"
        df["note_std"] = df["note_brute"].apply(
            lambda x: float(re.findall(r"\d+", str(x))[0]) if re.findall(r"\d+", str(x)) else 3.0
        )

    df["source"] = source

    # ── Texte propre ─────────────────────────────────────────────────────────
    df["texte_propre"] = (
        df["texte"]
        .fillna("")
        .astype(str)
        .str.replace(r"\n+", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # ── Normalisation du nom d'établissement ─────────────────────────────────
    if "nom_etablissement" in df.columns:
        df["nom_etablissement"] = df["nom_etablissement"].apply(normalize_etablissement)
    else:
        df["nom_etablissement"] = "Inconnu"

    # ── Langue ───────────────────────────────────────────────────────────────
    # Si la colonne langue est absente ou vide, on détecte
    if "langue" not in df.columns or df["langue"].isna().all() or (df["langue"] == "").all():
        print(f"   🌐 Détection de langue pour {file_path.name}...")
        df["langue"] = df["texte_propre"].apply(detect_language)
    else:
        # Complète uniquement les lignes vides
        mask = df["langue"].isna() | (df["langue"] == "")
        if mask.any():
            df.loc[mask, "langue"] = df.loc[mask, "texte_propre"].apply(detect_language)

    # ── Date ─────────────────────────────────────────────────────────────────
    if "date" not in df.columns:
        df["date"] = ""

    # ── Colonnes finales ──────────────────────────────────────────────────────
    keep = ["brand", "nom_etablissement", "source", "note_brute",
            "note_std", "texte", "texte_propre", "langue", "date"]
    for col in keep:
        if col not in df.columns:
            df[col] = ""

    print(f"   ✅ {file_path.name} — {len(df)} avis ({source})")
    return df[keep]


def merge_all() -> pd.DataFrame:
    """Fusionne tous les fichiers raw et retourne le DataFrame master."""
    if not RAW_DIR.exists():
        print(f"❌ Dossier introuvable : {RAW_DIR}")
        print("   Vérifie que les scrapers ont bien tourné.")
        return pd.DataFrame()

    csv_files = sorted(RAW_DIR.glob("*_raw.csv"))
    print(f"📂 {len(csv_files)} fichiers trouvés dans {RAW_DIR}\n")

    all_dfs = []
    for f in csv_files:
        df = process_file(f)
        if df is not None and not df.empty:
            all_dfs.append(df)

    if not all_dfs:
        print("⚠️  Aucun fichier valide trouvé.")
        return pd.DataFrame()

    master = pd.concat(all_dfs, ignore_index=True)

    # ── Nettoyage global ──────────────────────────────────────────────────────
    before = len(master)

    # Supprime les lignes sans texte
    master = master[master["texte_propre"].str.len() > 10].copy()

    # Déduplication sur le texte propre
    master.drop_duplicates(subset=["texte_propre"], inplace=True)

    after = len(master)
    print(f"\n🧹 Nettoyage : {before - after} doublons/vides supprimés")

    return master


def print_summary(df: pd.DataFrame) -> None:
    """Affiche un résumé du corpus consolidé."""
    print(f"\n{'='*50}")
    print(f"📊 CORPUS FINAL : {len(df)} avis")
    print(f"{'='*50}")
    print("\nPar source :")
    print(df["source"].value_counts().to_string())
    print("\nPar établissement :")
    print(df["nom_etablissement"].value_counts().to_string())
    print("\nPar langue :")
    print(df["langue"].value_counts().to_string())
    print("\nNotes moyennes par source :")
    print(df.groupby("source")["note_std"].mean().round(2).to_string())


if __name__ == "__main__":
    print("🚀 Fusion des données brutes\n")

    master = merge_all()

    if not master.empty:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        master.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"\n💾 Fichier sauvegardé → {OUTPUT_PATH}")
        print_summary(master)
    else:
        print("❌ Fusion échouée — aucune donnée.")

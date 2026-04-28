"""
Analyse de sentiment — BERT multilingue.

Modèle : nlptown/bert-base-multilingual-uncased-sentiment
Sortie  : 1 à 5 étoiles → mappé vers Positif / Neutre / Négatif

Le modèle est entraîné sur des avis clients multilingues (FR, EN, DE, NL, ES, IT)
— cohérent avec la distribution linguistique du corpus Huttopia.

Colonnes ajoutées au DataFrame :
    - sentiment_stars  : note brute du modèle (1 à 5)
    - sentiment_score  : score de confiance (0 à 1)
    - sentiment_label  : Positif / Neutre / Négatif

Temps estimé sur CPU : ~15-20 min pour 798 avis.

Usage :
    cd huttopia-voc
    python ml/sentiment_analysis.py
"""

import sys
import time
import pandas as pd
from pathlib import Path
from transformers import pipeline

# ── Chemins ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH    = PROJECT_ROOT / "data" / "processed" / "huttopia_reviews_master.csv"

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_NAME   = "nlptown/bert-base-multilingual-uncased-sentiment"
BATCH_SIZE   = 16      # Réduis à 8 si erreur mémoire
MAX_TOKENS   = 512     # Limite BERT
TEXT_COLUMN  = "texte_sentiment"   # Colonne nettoyée par clean_for_sentiment.py
FALLBACK_COL = "texte_propre"      # Fallback si texte_sentiment absent
MIN_TEXT_LEN = 15

# Mapping étoiles → label
# 1-2 étoiles = Négatif, 3 étoiles = Neutre, 4-5 étoiles = Positif
STARS_TO_LABEL = {
    1: "Négatif",
    2: "Négatif",
    3: "Neutre",
    4: "Positif",
    5: "Positif",
}


def load_model():
    """Charge le modèle BERT. Téléchargement ~670MB au premier lancement."""
    print(f"⏳ Chargement du modèle {MODEL_NAME}...")
    print("   (Premier lancement : téléchargement ~670MB)")
    model = pipeline(
        "sentiment-analysis",
        model=MODEL_NAME,
        device=-1,      # CPU
        truncation=True,
        max_length=MAX_TOKENS,
    )
    print("✅ Modèle chargé\n")
    return model


def stars_from_label(label: str) -> int:
    """Extrait le nombre d'étoiles depuis le label du modèle ('1 star', '5 stars')."""
    try:
        return int(label.split()[0])
    except (ValueError, IndexError):
        return 3  # Fallback neutre


def analyze_batch(texts: list[str], model) -> list[dict]:
    """Analyse un batch de textes et retourne les résultats normalisés."""
    # Tronque les textes trop longs pour BERT
    truncated = [t[:1800] for t in texts]  # ~512 tokens ≈ 1800 chars en français

    try:
        results = model(truncated)
    except Exception as e:
        print(f"\n   ⚠️  Erreur batch : {e}")
        return [{"label": "3 stars", "score": 0.5}] * len(texts)

    parsed = []
    for r in results:
        stars = stars_from_label(r["label"])
        parsed.append({
            "sentiment_stars": stars,
            "sentiment_score": round(r["score"], 4),
            "sentiment_label": STARS_TO_LABEL[stars],
        })
    return parsed


def run_sentiment(df: pd.DataFrame, model) -> pd.DataFrame:
    """Applique l'analyse de sentiment sur tout le DataFrame."""
    # Utilise texte_sentiment si disponible, sinon texte_propre
    col = TEXT_COLUMN if TEXT_COLUMN in df.columns else FALLBACK_COL
    if col == FALLBACK_COL:
        print(f"   ⚠️  Colonne '{TEXT_COLUMN}' absente — utilise '{FALLBACK_COL}'")
        print("   Lance d'abord : python processing/clean_for_sentiment.py\n")

    # Exclut les avis sans contenu analysable (NaN dans texte_sentiment)
    mask_valid = df[col].notna() & (df[col].astype(str).str.len() >= MIN_TEXT_LEN)
    texts      = df.loc[mask_valid, col].astype(str).tolist()
    indices    = df.loc[mask_valid].index.tolist()
    total      = len(texts)

    print(f"🔍 Analyse de sentiment sur {total} avis ({len(df) - total} ignorés)")
    print(f"   Modèle : {MODEL_NAME}")
    print(f"   Batch size : {BATCH_SIZE}")
    print(f"   Temps estimé : {total * 1.2 / 60:.0f}-{total * 1.5 / 60:.0f} min sur CPU\n")

    # Initialise les colonnes avec proxy note_std pour les avis sans texte analysable
    def note_to_sentiment(note):
        if pd.isna(note):
            return "Neutre", 3, 0.5
        if note >= 4.0:
            return "Positif", int(min(5, round(note))), 0.6
        elif note <= 2.5:
            return "Négatif", int(max(1, round(note))), 0.6
        else:
            return "Neutre", 3, 0.5

    df["sentiment_stars"] = df["note_std"].apply(lambda x: note_to_sentiment(x)[1])
    df["sentiment_score"] = df["note_std"].apply(lambda x: note_to_sentiment(x)[2])
    df["sentiment_label"] = df["note_std"].apply(lambda x: note_to_sentiment(x)[0])

    results = []
    start   = time.time()

    for i in range(0, total, BATCH_SIZE):
        batch      = texts[i : i + BATCH_SIZE]
        batch_res  = analyze_batch(batch, model)
        results.extend(batch_res)

        done    = min(i + BATCH_SIZE, total)
        elapsed = time.time() - start
        eta     = (elapsed / done) * (total - done) if done > 0 else 0
        print(
            f"   [{done:>4}/{total}] "
            f"élapsé : {elapsed/60:.1f}min | "
            f"ETA : {eta/60:.1f}min",
            end="\r",
        )

    print(f"\n✅ Analyse terminée en {(time.time()-start)/60:.1f} min\n")

    # Remplit les colonnes
    for idx, res in zip(indices, results):
        df.at[idx, "sentiment_stars"] = res["sentiment_stars"]
        df.at[idx, "sentiment_score"] = res["sentiment_score"]
        df.at[idx, "sentiment_label"] = res["sentiment_label"]

    return df


def print_results(df: pd.DataFrame) -> None:
    """Affiche un résumé de l'analyse de sentiment."""
    print("=" * 55)
    print("📊 RÉSULTATS DE L'ANALYSE DE SENTIMENT")
    print("=" * 55)

    total = len(df)

    print("\nDistribution globale :")
    counts = df["sentiment_label"].value_counts()
    for label in ["Positif", "Neutre", "Négatif"]:
        count = counts.get(label, 0)
        bar   = "█" * int(count / total * 30)
        print(f"  {label:<10} {count:>4} avis ({count/total*100:4.1f}%)  {bar}")

    print("\nSentiment × Source :")
    pivot = pd.crosstab(df["sentiment_label"], df["source"], normalize="columns")
    print((pivot * 100).round(1).to_string())

    print("\nSentiment × Thème :")
    if "theme_label" in df.columns:
        pivot2 = pd.crosstab(df["theme_label"], df["sentiment_label"])
        pivot2["% Positif"] = (
            pivot2.get("Positif", 0) /
            pivot2.sum(axis=1) * 100
        ).round(1)
        print(pivot2.sort_values("% Positif", ascending=False).to_string())

    print("\nSentiment × Camping :")
    if "nom_etablissement" in df.columns:
        df_camp = df[~df["nom_etablissement"].isin(["Marque_Globale", "Inconnu"])]
        pivot3  = pd.crosstab(df_camp["nom_etablissement"], df_camp["sentiment_label"])
        pivot3["% Positif"] = (
            pivot3.get("Positif", 0) /
            pivot3.sum(axis=1) * 100
        ).round(1)
        print(pivot3.sort_values("% Positif", ascending=False).to_string())


if __name__ == "__main__":
    if not DATA_PATH.exists():
        print(f"❌ Fichier introuvable : {DATA_PATH}")
        print("   Lance d'abord : python processing/data_merger.py")
        sys.exit(1)

    print(f"📂 Chargement de {DATA_PATH.name}...")
    df = pd.read_csv(DATA_PATH)
    print(f"   {len(df)} avis chargés\n")

    model = load_model()
    df    = run_sentiment(df, model)

    df.to_csv(DATA_PATH, index=False, encoding="utf-8-sig")
    print(f"💾 Résultats sauvegardés → {DATA_PATH}\n")

    print_results(df)

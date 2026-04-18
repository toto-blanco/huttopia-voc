"""
Classification thématique — BART zero-shot multilingue.

Stratégie : les labels sont passés en anglais au modèle (meilleure précision
sur du texte français avec facebook/bart-large-mnli qui est un modèle anglais),
mais les résultats sont stockés avec les labels français définis dans labels.py.

Un avis peut couvrir plusieurs thèmes : on stocke le thème principal (score max)
ET les scores de tous les thèmes pour des analyses plus fines dans le dashboard.

Temps estimé sur CPU : ~20-30 min pour 798 avis.

Usage :
    python topic_classification.py
"""

import sys
import time
import pandas as pd
from pathlib import Path
from transformers import pipeline

# ── Chemins ──────────────────────────────────────────────────────────────────
PROJECT_ROOT  = Path(__file__).resolve().parent.parent
DATA_IN       = PROJECT_ROOT / "data" / "processed" / "huttopia_reviews_master.csv"
DATA_OUT      = PROJECT_ROOT / "data" / "processed" / "huttopia_reviews_master.csv"

# Ajoute config/ au path pour importer labels.py
sys.path.insert(0, str(PROJECT_ROOT / "config"))
from labels import THEMES, THEME_DISPLAY_NAMES

# ── Labels EN → FR ────────────────────────────────────────────────────────────
# On passe les labels en anglais à BART pour de meilleures performances,
# puis on mappe le résultat vers le label français canonique.
LABELS_EN_TO_FR = {
    "welcome and staff":          "accueil et personnel",
    "accommodation and comfort":  "hébergement et confort",
    "nature and environment":     "nature et environnement",
    "cleanliness and sanitation": "propreté et sanitaires",
    "food and dining":            "restauration et alimentation",
    "activities and entertainment": "activités et animations",
    "value for money":            "rapport qualité-prix",
}
LABELS_EN = list(LABELS_EN_TO_FR.keys())

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_NAME  = "facebook/bart-large-mnli"
BATCH_SIZE  = 8     # Réduis à 4 si erreur mémoire
TEXT_COLUMN = "texte_propre"
MIN_TEXT_LEN = 15   # Ignore les textes trop courts


def load_model():
    """Charge le modèle BART zero-shot. Téléchargement ~1.6GB au premier lancement."""
    print(f"⏳ Chargement du modèle {MODEL_NAME}...")
    print("   (Premier lancement : téléchargement ~1.6GB — patiente)")
    classifier = pipeline(
        "zero-shot-classification",
        model=MODEL_NAME,
        device=-1,  # CPU
    )
    print("✅ Modèle chargé\n")
    return classifier


def classify_batch(texts: list[str], classifier) -> list[dict]:
    """
    Classifie un batch de textes et retourne les scores pour chaque thème.
    Retourne une liste de dicts {theme_fr: score} par texte.
    """
    results = classifier(
        texts,
        candidate_labels=LABELS_EN,
        multi_label=True,   # Un avis peut couvrir plusieurs thèmes
        hypothesis_template="This review is about {}.",
    )

    # Normalise le résultat (single text → list of one)
    if isinstance(results, dict):
        results = [results]

    parsed = []
    for r in results:
        scores = {}
        for label_en, score in zip(r["labels"], r["scores"]):
            label_fr = LABELS_EN_TO_FR.get(label_en, label_en)
            scores[label_fr] = round(score, 4)
        parsed.append(scores)

    return parsed


def run_classification(df: pd.DataFrame, classifier) -> pd.DataFrame:
    """
    Applique la classification sur tout le DataFrame.
    Ajoute les colonnes :
        - theme_label  : thème principal (score max)
        - theme_score  : score de confiance du thème principal
        - theme_scores : dict JSON de tous les scores (pour le dashboard)
    """
    # Filtre les textes trop courts
    mask_valid = df[TEXT_COLUMN].str.len() >= MIN_TEXT_LEN
    texts      = df.loc[mask_valid, TEXT_COLUMN].tolist()
    indices    = df.loc[mask_valid].index.tolist()

    total   = len(texts)
    results = []

    print(f"🔍 Classification de {total} avis ({len(df) - total} ignorés — texte trop court)")
    print(f"   Modèle : {MODEL_NAME}")
    print(f"   Thèmes : {', '.join(THEME_DISPLAY_NAMES.values())}")
    print(f"   Batch size : {BATCH_SIZE}")
    print(f"   Temps estimé : {total * 1.5 / 60:.0f}-{total * 2 / 60:.0f} min sur CPU\n")

    start = time.time()

    for i in range(0, total, BATCH_SIZE):
        batch      = texts[i : i + BATCH_SIZE]
        batch_res  = classify_batch(batch, classifier)
        results.extend(batch_res)

        # Progression
        done    = min(i + BATCH_SIZE, total)
        elapsed = time.time() - start
        eta     = (elapsed / done) * (total - done) if done > 0 else 0
        print(
            f"   [{done:>4}/{total}] "
            f"élapsé : {elapsed/60:.1f}min | "
            f"ETA : {eta/60:.1f}min",
            end="\r",
        )

    print(f"\n✅ Classification terminée en {(time.time()-start)/60:.1f} min\n")

    # Initialise les colonnes avec des valeurs par défaut
    df["theme_label"]  = "inconnu"
    df["theme_score"]  = 0.0
    df["theme_scores"] = "{}"

    # Remplit les lignes classifiées
    for idx, scores in zip(indices, results):
        if scores:
            best_theme = max(scores, key=scores.get)
            df.at[idx, "theme_label"]  = best_theme
            df.at[idx, "theme_score"]  = scores[best_theme]
            df.at[idx, "theme_scores"] = str(scores)

    return df


def print_results(df: pd.DataFrame) -> None:
    """Affiche un résumé de la classification."""
    print("=" * 55)
    print("📊 RÉSULTATS DE LA CLASSIFICATION THÉMATIQUE")
    print("=" * 55)

    print("\nDistribution des thèmes :")
    counts = df["theme_label"].value_counts()
    total  = len(df)
    for theme, count in counts.items():
        display = THEME_DISPLAY_NAMES.get(theme, theme)
        bar     = "█" * int(count / total * 30)
        print(f"  {display:<20} {count:>4} avis ({count/total*100:4.1f}%)  {bar}")

    print("\nScore moyen de confiance par thème :")
    conf = df.groupby("theme_label")["theme_score"].mean().sort_values(ascending=False)
    for theme, score in conf.items():
        display = THEME_DISPLAY_NAMES.get(theme, theme)
        print(f"  {display:<20} {score:.3f}")

    print("\nThème × Source :")
    pivot = pd.crosstab(df["theme_label"], df["source"])
    pivot.index = [THEME_DISPLAY_NAMES.get(i, i) for i in pivot.index]
    print(pivot.to_string())


if __name__ == "__main__":
    # ── Chargement ────────────────────────────────────────────────────────────
    if not DATA_IN.exists():
        print(f"❌ Fichier introuvable : {DATA_IN}")
        print("   Lance d'abord : python processing/data_merger.py")
        sys.exit(1)

    print(f"📂 Chargement de {DATA_IN.name}...")
    df = pd.read_csv(DATA_IN)
    print(f"   {len(df)} avis chargés\n")

    # ── Classification ────────────────────────────────────────────────────────
    classifier = load_model()
    df = run_classification(df, classifier)

    # ── Sauvegarde ────────────────────────────────────────────────────────────
    df.to_csv(DATA_OUT, index=False, encoding="utf-8-sig")
    print(f"💾 Résultats sauvegardés → {DATA_OUT}\n")

    # ── Résumé ────────────────────────────────────────────────────────────────
    print_results(df)

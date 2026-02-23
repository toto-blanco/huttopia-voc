"""
Classification thématique avec BART zero-shot.

Modèle: facebook/bart-large-mnli
Labels: définis dans config/labels.py
"""

import pandas as pd
from transformers import pipeline
import sys
sys.path.append('..')
from config.labels import THEMES


def load_classification_model():
    """
    Charge le modèle BART pour la classification zero-shot.
    
    Returns:
        Pipeline: Modèle chargé
    """
    
    # TODO Phase 4: Charger le modèle
    # classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    
    return None


def classify_theme(text, model, candidate_labels=THEMES):
    """
    Classifie un texte dans l'un des thèmes définis.
    
    Args:
        text (str): Texte à classifier
        model: Pipeline de classification
        candidate_labels (list): Liste des labels possibles
        
    Returns:
        dict: {label: "accueil et personnel", score: 0.87}
    """
    
    # TODO Phase 4: Implémenter la classification
    # result = model(text[:512], candidate_labels)
    # return {"label": result["labels"][0], "score": result["scores"][0]}
    
    return {"label": "unknown", "score": 0.0}


def batch_theme_classification(df, text_column="texte_clean", batch_size=8):
    """
    Classification thématique sur un DataFrame entier.
    
    ⚠️ ATTENTION: Zero-shot est lent (~1s par avis)
    Sur 1000 avis = ~17 minutes
    
    Args:
        df (pd.DataFrame): DataFrame avec les avis
        text_column (str): Nom de la colonne texte
        batch_size (int): Taille des batchs (réduire si mémoire insuffisante)
        
    Returns:
        pd.DataFrame: DataFrame enrichi avec theme_label et theme_score
    """
    
    print("Chargement du modèle BART...")
    model = load_classification_model()
    
    if model is None:
        print("⚠️ Modèle non chargé - Phase 4 non implémentée")
        return df
    
    print(f"Classification thématique sur {len(df)} avis...")
    print(f"Thèmes: {THEMES}")
    print("⏳ Cela peut prendre 15-20 minutes pour 1000 avis...")
    
    # TODO Phase 4: Implémenter le traitement par batchs
    
    return df


def validate_classification(df, sample_size=30):
    """
    Valide manuellement la classification sur un échantillon.
    
    Args:
        df (pd.DataFrame): DataFrame avec les classifications
        sample_size (int): Nombre d'exemples à valider
        
    Returns:
        float: Précision estimée (% d'exemples corrects)
    """
    
    # TODO Phase 4: Afficher des exemples pour validation manuelle
    # sample = df.sample(sample_size)
    # for _, row in sample.iterrows():
    #     print(f"Texte: {row['texte_clean'][:100]}...")
    #     print(f"Thème prédit: {row['theme_label']} (score: {row['theme_score']:.2f})")
    #     correct = input("Correct? (y/n): ")
    
    return 0.0


if __name__ == "__main__":
    # Test
    # df = pd.read_csv("../data/processed/reviews_clean.csv")
    # df = batch_theme_classification(df)
    # accuracy = validate_classification(df, sample_size=30)
    # print(f"Précision estimée: {accuracy*100:.1f}%")
    pass

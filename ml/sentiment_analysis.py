"""
Analyse de sentiment avec BERT multilingue.

Modèle: nlptown/bert-base-multilingual-uncased-sentiment
Sortie: Note de 1 à 5 étoiles
"""

import pandas as pd
from transformers import pipeline


def load_sentiment_model():
    """
    Charge le modèle BERT pour l'analyse de sentiment.
    
    Returns:
        Pipeline: Modèle chargé
    """
    
    # TODO Phase 4: Charger le modèle
    # model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    # sentiment_pipeline = pipeline("sentiment-analysis", model=model_name)
    
    return None


def analyze_sentiment(text, model):
    """
    Analyse le sentiment d'un texte.
    
    Args:
        text (str): Texte à analyser
        model: Pipeline de sentiment
        
    Returns:
        dict: {label: "5 stars", score: 0.95}
    """
    
    # TODO Phase 4: Implémenter l'analyse
    # result = model(text[:512])  # BERT limité à 512 tokens
    
    return {"label": "unknown", "score": 0.0}


def batch_sentiment_analysis(df, text_column="texte_clean", batch_size=32):
    """
    Analyse de sentiment sur un DataFrame entier.
    
    Args:
        df (pd.DataFrame): DataFrame avec les avis
        text_column (str): Nom de la colonne texte
        batch_size (int): Taille des batchs
        
    Returns:
        pd.DataFrame: DataFrame enrichi avec sentiment_label et sentiment_score
    """
    
    print("Chargement du modèle BERT...")
    model = load_sentiment_model()
    
    if model is None:
        print("⚠️ Modèle non chargé - Phase 4 non implémentée")
        return df
    
    print(f"Analyse de sentiment sur {len(df)} avis...")
    
    # TODO Phase 4: Analyser par batchs pour optimiser
    
    return df


if __name__ == "__main__":
    # Test sur un échantillon
    # df = pd.read_csv("../data/processed/reviews_clean.csv")
    # df = batch_sentiment_analysis(df)
    # print(df[["texte_clean", "sentiment_label", "sentiment_score"]].head())
    pass

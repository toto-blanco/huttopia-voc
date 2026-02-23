import pandas as pd
from textblob import TextBlob
from textblob_fr import PatternTagger, PatternAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns

def run_comparative_analysis():
    df = pd.read_csv("../data/processed/huttopia_reviews_master.csv")
    df['texte_propre'] = df['texte'].fillna("").astype(str)

    # 1. Calcul du sentiment
    def get_score(text):
        if len(text) < 5: return 0.0
        return TextBlob(text, pos_tagger=PatternTagger(), analyzer=PatternAnalyzer()).sentiment[0]

    df['sentiment_score'] = df['texte_propre'].apply(get_score)
    
    # 2. Filtrage des sources principales pour la lisibilité
    sources_to_plot = ['Google Maps', 'Booking']
    df_filtered = df[df['source'].isin(sources_to_plot)].copy()

    # --- VISUALISATION ---
    sns.set_theme(style="whitegrid")
    # Création d'une grille : 2 lignes (une par source)
    fig, axes = plt.subplots(2, 1, figsize=(15, 12))

    for i, source in enumerate(sources_to_plot):
        data_source = df_filtered[df_filtered['source'] == source]
        
        # On trace le boxplot pour chaque source
        sns.boxplot(x='note_std', y='sentiment_score', data=data_source, ax=axes[i], palette='RdYlGn')
        
        axes[i].set_title(f"Focus {source} : Corrélation Note vs Sentiment (N={len(data_source)})", 
                          fontsize=14, fontweight='bold')
        axes[i].set_xlabel("Note Standardisée")
        axes[i].set_ylabel("Score Sentiment")
        axes[i].axhline(0, color='black', linestyle='--', alpha=0.3)

    plt.suptitle("Analyse Comparative de la Fiabilité des Avis par Plateforme", fontsize=18, y=1.02)
    plt.tight_layout()
    
    output_path = "../data/processed/comparison_sources_report.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Comparatif généré : {output_path}")
    plt.show()

if __name__ == "__main__":
    run_comparative_analysis()
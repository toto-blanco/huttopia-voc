import pandas as pd
from textblob import TextBlob
from textblob_fr import PatternTagger, PatternAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns
import os

class HuttopiaSentiment:
    def __init__(self, file_path="../data/processed/huttopia_reviews_master.csv"):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier introuvable : {file_path}")
        self.df = pd.read_csv(file_path)
        # On s'assure que le texte est traité comme du string
        self.df['texte_propre'] = self.df['texte'].fillna("").astype(str)

    def run_analysis(self):
        print("🧠 Analyse NLP focus en cours...")
        
        # 1. Calcul du score de sentiment
        def get_score(text):
            if len(text) < 5: return 0.0
            blob = TextBlob(text, pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())
            return blob.sentiment[0]

        self.df['sentiment_score'] = self.df['texte_propre'].apply(get_score)
        
        # 2. Catégorisation
        self.df['sentiment_label'] = pd.cut(self.df['sentiment_score'], 
                                            bins=[-1.1, -0.15, 0.15, 1.1], 
                                            labels=['Négatif', 'Neutre', 'Positif'])

        # --- VISUALISATION ÉPURÉE ---
        sns.set_theme(style="whitegrid")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Graphique A : Répartition des Sentiments
        # Idéal pour montrer le "climat" global des avis
        colors = ['#ff6b6b', '#ced4da', '#51cf66'] # Rouge, Gris, Vert
        dist = self.df['sentiment_label'].value_counts(normalize=True).sort_index() * 100
        sns.barplot(x=dist.index, y=dist.values, palette=colors, ax=ax1, edgecolor='0.3')
        ax1.set_title("🎭 Répartition Sémantique Globale", fontsize=14, fontweight='bold')
        ax1.set_ylabel("Pourcentage des avis (%)")
        ax1.set_ylim(0, 100)
        for i, v in enumerate(dist):
            ax1.text(i, v + 2, f"{v:.1f}%", ha='center', fontweight='bold', fontsize=12)

        # Graphique B : Cohérence Note vs Sentiment
        # C'est la preuve que ton scraping (Booking/Google/Trustpilot) est cohérent
        sns.boxplot(x='note_std', y='sentiment_score', data=self.df, ax=ax2, palette='RdYlGn')
        ax2.set_title("📈 Corrélation : Note vs Ton du message", fontsize=14, fontweight='bold')
        ax2.set_xlabel("Note Standardisée (1 à 5)")
        ax2.set_ylabel("Score de Sentiment (-1 à 1)")
        ax2.axhline(0, color='black', linestyle='--', alpha=0.3)

        plt.suptitle(f"Rapport d'Analyse Sémantique - Huttopia\n(Base consolidée : {len(self.df)} avis)", 
                     fontsize=16, fontweight='bold', y=1.05)
        
        plt.tight_layout()
        
        # Sauvegarde du rapport épuré
        output_img = "../data/processed/sentiment_focus_report.png"
        plt.savefig(output_img, dpi=300, bbox_inches='tight')
        
        # Sauvegarde des données enrichies
        self.df.to_csv("../data/processed/huttopia_final_analysis.csv", index=False)
        
        print(f"✅ Analyse terminée. Visuel sauvegardé : {output_img}")
        plt.show()

if __name__ == "__main__":
    analyzer = HuttopiaSentiment()
    analyzer.run_analysis()
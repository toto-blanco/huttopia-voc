import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
from nltk.corpus import stopwords
import nltk

# Téléchargement des ressources NLTK
nltk.download('stopwords')

def generate_perfect_wordcloud():
    file_path = "../data/processed/huttopia_reviews_master.csv"
    if not os.path.exists(file_path):
        print("❌ Fichier master introuvable.")
        return

    # 1. Chargement de TOUTES les données
    df = pd.read_csv(file_path)
    
    # 2. Préparation du texte (on combine texte brut et texte propre si besoin)
    # On s'assure de prendre toutes les sources (Google, Booking, Trustpilot)
    text = " ".join(df['texte'].fillna("").astype(str)).lower()

    # 3. Liste de Stopwords ultra-complète pour BA
    # On retire les mots qui n'apportent pas d'info sur l'expérience client
    french_stop = set(stopwords.words('french'))
    custom_stop = {
        "huttopia", "camping", "plus", "tout", "cette", "aussi", "fait", "être", 
        "bien", "très", "pas", "le", "la", "les", "des", "pour", "dans", "sur", 
        "avec", "nous", "vous", "est", "était", "étaient", "avoir", "avez", 
        "mais", "pour", "très", "donc", "avis", "séjour", "nuit", "jours", 
        "faire", "site", "endroit", "lieu", "vraiment", "peu", "trop"
    }
    french_stop.update(custom_stop)

    # 4. Création du Nuage avec des paramètres d'importance
    # 'collocations=False' évite de répéter des duos de mots inutiles
    wc = WordCloud(
        width=1200, 
        height=800, 
        background_color='white',
        stopwords=french_stop,
        colormap='viridis',
        collocations=False, 
        max_words=80
    ).generate(text)

    # 5. Affichage
    plt.figure(figsize=(15, 10))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.title(f"Analyse Thématique Consolidée (Google, Booking, Trustpilot)\nBase : {len(df)} avis", fontsize=18)
    
    # Sauvegarde pour ton rapport
    plt.savefig("../data/processed/wordcloud_business_final.png", dpi=300, bbox_inches='tight')
    plt.show()
    print("✅ Nuage de mots final généré dans /data/processed/")

if __name__ == "__main__":
    generate_perfect_wordcloud()
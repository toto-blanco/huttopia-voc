import pandas as pd
import os
import re
from textblob import TextBlob
from textblob_fr import PatternTagger, PatternAnalyzer

def clean_google_note(note_str, text_content=""):
    """Transforme la note ou calcule un score sémantique si N/A"""
    # 1. On cherche un chiffre (4 étoiles -> 4)
    res = re.findall(r"(\d+)", str(note_str))
    if res:
        return float(res[0])
    
    # 2. Si c'est N/A ou vide, on utilise le texte pour deviner la note
    if pd.isna(note_str) or "N/A" in str(note_str):
        if len(str(text_content)) > 10:
            blob = TextBlob(str(text_content), pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())
            polarity = blob.sentiment[0] # Entre -1 et 1
            # Conversion en note de 1 à 5
            return round(((polarity + 1) * 2) + 1)
    
    return 3.0 # Note neutre par défaut si vraiment rien

def clean_booking_note(note_str):
    """Transforme 'Note de 8,0' en 4.0 (ramené sur 5)"""
    if pd.isna(note_str): return 0.0
    # On cherche un chiffre avec virgule ou point
    res = re.findall(r"(\d+[\.,]\d+|\d+)", str(note_str))
    if res:
        val = float(res[0].replace(',', '.'))
        return val / 2 if val > 5 else val
    return 0.0

def merge_all_data(input_dir="../data/raw", output_path="../data/processed/huttopia_reviews_master.csv"):
    all_dfs = []
    
    if not os.path.exists(input_dir):
        print(f"❌ Erreur : Le dossier {input_dir} n'existe pas.")
        return

    print(f"📂 Lecture des fichiers dans {input_dir}...")
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            file_path = os.path.join(input_dir, filename)
            df = pd.read_csv(file_path)
            
            # --- NORMALISATION SELON LA SOURCE ---
            if "google" in filename.lower():
                print(f"✅ Traitement Google (avec fallback sémantique) : {filename}")
                # On passe le texte en plus de la note pour le calcul si N/A
                df['note_std'] = df.apply(lambda x: clean_google_note(x['note_brute'], x['texte']), axis=1)
                df['source'] = "Google Maps"
                df['langue'] = 'fr' # Important pour  script NLP
            
            elif "booking" in filename.lower():
                print(f"✅ Traitement Booking : {filename}")
                df['note_std'] = df['note_brute'].apply(clean_booking_note)
                df['source'] = "Booking"
            
            elif "trustpilot" in filename.lower():
                print(f"✅ Traitement Trustpilot : {filename}")
                # Trustpilot est déjà sur 5, on extrait juste le chiffre
                df['note_std'] = df['note_brute'].astype(str).str.extract('(\d+)').astype(float).fillna(3.0)
                df['source'] = "Trustpilot"
                # Pour Trustpilot, l'établissement est souvent global ("Huttopia Global")
                if 'nom_etablissement' not in df.columns:
                    df['nom_etablissement'] = "Marque Globale"
                    
            else:
                print(f"ℹ️ Traitement Autre : {filename}")
                # Par défaut on essaie d'extraire un chiffre
                df['note_std'] = df['note_brute'].astype(str).str.extract('(\d+)').astype(float)
                df['source'] = "Inconnue"

            # On s'assure que le texte est propre pour la suite
            df['texte_propre'] = df['texte'].fillna("").astype(str).str.replace(r'\n', ' ', regex=True)
            
            all_dfs.append(df)

    if all_dfs:
        master_df = pd.concat(all_dfs, ignore_index=True)
        
        # Nettoyage final : suppression des doublons et lignes sans texte
        master_df = master_df[master_df['texte_propre'].str.len() > 5]
        master_df.drop_duplicates(subset=['texte_propre'], inplace=True)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        master_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n🚀 FUSION TERMINÉE !")
        print(f"📊 Total des avis consolidés : {len(master_df)}")
        print(f"📍 Fichier créé : {output_path}")
    else:
        print("⚠️ Aucun fichier CSV trouvé dans le dossier raw.")

if __name__ == "__main__":
    merge_all_data()
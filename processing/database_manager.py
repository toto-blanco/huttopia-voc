import sqlite3
import pandas as pd

def save_to_sqlite(df, db_path="data/huttopia_voc.db"):
    """
    Sauvegarde le DataFrame dans SQLite. 
    L'option if_exists='append' permet d'ajouter les données des 
    différents scrapers au fur et à mesure.
    """
    conn = sqlite3.connect(db_path)
    # On s'assure que les colonnes matchent le schéma prévu en V1/V2
    df.to_sql('reviews', conn, if_exists='append', index=False)
    conn.close()
    print(f"Données sauvegardées dans {db_path}")
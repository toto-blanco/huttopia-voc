"""
Dashboard Streamlit - Voice of Customer Huttopia

Deux vues:
- Vue Commerciale: score global, tendances, alertes
- Vue Marketing: distribution thèmes, verbatims, insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.append('..')
from config.labels import THEME_DISPLAY_NAMES


# Configuration de la page
st.set_page_config(
    page_title="Huttopia Voice of Customer",
    page_icon="🏕️",
    layout="wide"
)


def load_data():
    """
    Charge les données analysées.
    
    Returns:
        pd.DataFrame: DataFrame avec toutes les analyses
    """
    
    # TODO Phase 5: Charger depuis data/processed/reviews_analyzed.csv
    # df = pd.read_csv("../data/processed/reviews_analyzed.csv")
    
    # Placeholder pour développement
    df = pd.DataFrame()
    
    return df


def vue_commerciale(df):
    """
    Affiche la vue orientée équipe Commerciale.
    """
    
    st.header("📊 Vue Commerciale")
    
    # TODO Phase 5: Implémenter les KPIs
    # - Score global (gauge)
    # - Tendance sur 12 mois
    # - Top 5 sujets problématiques
    # - Alerte par site
    
    st.info("Vue en cours de développement - Phase 5")


def vue_marketing(df):
    """
    Affiche la vue orientée équipe Marketing.
    """
    
    st.header("🎯 Vue Marketing")
    
    # TODO Phase 5: Implémenter les visualisations
    # - Distribution des thèmes (donut chart)
    # - Verbatims positifs filtrables
    # - Comparaison inter-sites
    
    st.info("Vue en cours de développement - Phase 5")


def main():
    """
    Point d'entrée principal du dashboard.
    """
    
    st.title("🏕️ Huttopia - Voice of Customer")
    st.markdown("*Analyse automatisée des avis clients | V1 - POC Business Analyst*")
    
    # Chargement des données
    df = load_data()
    
    if df.empty:
        st.warning("⚠️ Aucune donnée disponible. Exécuter d'abord les phases 2-4.")
        st.stop()
    
    # Navigation par onglets
    tab1, tab2 = st.tabs(["Vue Commerciale", "Vue Marketing"])
    
    with tab1:
        vue_commerciale(df)
    
    with tab2:
        vue_marketing(df)
    
    # Footer
    st.markdown("---")
    st.markdown("*Projet réalisé pour l'entretien Huttopia - Business Analyst Commercial & Marketing*")


if __name__ == "__main__":
    main()

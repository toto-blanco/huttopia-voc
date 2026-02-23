# 🏕️ Huttopia - Voice of Customer

> **POC Business Analyst** pour l'entretien Huttopia (Saint-Genis-les-Ollières)  
> Pipeline end-to-end d'analyse des avis clients avec NLP et dashboards décisionnels

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red.svg)](https://streamlit.io/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-yellow.svg)](https://huggingface.co/)

---

## 📋 Contexte

Les équipes Commercial & Marketing d'Huttopia sont intéressé par des dashboard sur les avis clients dispersés sur Google, Trustpilot et TripAdvisor. Ce projet démontre :

- La collecte automatisée des avis multi-sources
- L'analyse NLP (sentiment + classification thématique)
- La restitution dans des dashboards orientés décision

---

## 🎯 Objectifs

**V1 (MVP)** : Analyse des avis Huttopia uniquement  
**V2 (Roadmap)** : Benchmark concurrentiel (Homair, Sites et Paysages, Sandaya)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2 — COLLECTE                                          │
│ Trustpilot + Google Places → SQLite                         │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3 — TRAITEMENT                                        │
│ Nettoyage + détection langue + normalisation notes          │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4 — CLASSIFICATION ML                                 │
│ BERT (sentiment) + BART (thèmes zero-shot)                  │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5 — DASHBOARDS                                        │
│ Vue Commerciale + Vue Marketing (Streamlit Cloud)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Stack Technique

| Composant | Technologie |
|---|---|
| **Collecte** | BeautifulSoup, Selenium, Google Places API |
| **Stockage** | SQLite + CSV |
| **Traitement** | pandas, langdetect |
| **Sentiment** | `nlptown/bert-base-multilingual-uncased-sentiment` |
| **Classification** | `facebook/bart-large-mnli` (zero-shot) |
| **Dashboard** | Streamlit + Plotly |

---

## 📦 Installation

```bash
# Cloner le repo
git clone https://github.com/TON_USERNAME/huttopia-voc.git
cd huttopia-voc

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les clés API (optionnel)
cp .env.example .env
# Éditer .env avec votre clé Google Places
```

---

## 🚀 Usage

### Phase 2 : Collecte
```bash
cd scraping
python trustpilot_scraper.py
python google_scraper.py
```

### Phase 3 : Nettoyage
```bash
cd processing
python clean_reviews.py
```

### Phase 4 : Analyse ML
```bash
cd ml
python sentiment_analysis.py
python topic_classification.py
```

### Phase 5 : Dashboard
```bash
cd dashboard
streamlit run app.py
```

---

## 📊 Thèmes de Classification

7 labels définis dans `config/labels.py` :

1. Accueil et personnel
2. Hébergement et confort
3. Nature et environnement
4. Propreté et sanitaires
5. Restauration et alimentation
6. Activités et animations
7. Rapport qualité-prix

---

## 📈 Résultats (à compléter Phase 6)

*Screenshot du dashboard à ajouter*

**Insight principal** : *[À formuler après l'analyse]*

---

## 🗺️ Roadmap

- [x] Phase 1 : Structure projet + labels définis
- [ ] Phase 2 : Collecte ≥ 300 avis
- [ ] Phase 3 : Nettoyage + détection langue
- [ ] Phase 4 : Classification ML (≥70% précision)
- [ ] Phase 5 : Dashboard Streamlit déployé
- [ ] Phase 6 : README finalisé + insights
- [ ] V2 : Extension benchmark concurrentiel

---

## 👤 Auteur

Projet réalisé pour le poste **Business Analyst Commercial & Marketing** chez Huttopia.

---

## 📄 Licence

Ce projet est réalisé dans un cadre de candidature professionnelle.

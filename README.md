# 🏕️ Huttopia — Voice of Customer

> Analyse sémantique de 798 avis clients multi-sources pour produire des recommandations opérationnelles actionnables à destination des équipes Commercial & Marketing d'Huttopia.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red.svg)](https://streamlit.io/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-BART-yellow.svg)](https://huggingface.co/)
[![Claude](https://img.shields.io/badge/Développé_avec-Claude_Sonnet-blueviolet.svg)](https://claude.ai/)

---

## 🎯 La question centrale

> **Que disent vraiment les clients Huttopia, et que devrait-il prioriser ?**

Ce projet n'est pas une démonstration technique. C'est une réponse à une question business concrète : comment transformer des milliers d'avis dispersés sur le web en recommandations que des équipes non-data peuvent comprendre et mettre en œuvre.

---

## 🖥️ Aperçu du dashboard

**Vue Commerciale — KPIs et notes par camping**
![Vue Commerciale](docs/dashboard_commercial_1.png)
![Tableau de bord par camping](docs/dashboard_commercial_2.png)

**Vue Marketing — Thèmes et heatmap**
![Vue Marketing](docs/dashboard_marketing_1.png)
![Heatmap thèmes × camping](docs/dashboard_marketing_2.png)

**Vue Marketing — Nuage de mots et verbatims**
![Nuage de mots](docs/dashboard_marketing_3.png)
![Verbatims clients](docs/dashboard_marketing_4.png)

---



Quatre insights actionnables, issus de l'analyse de 798 avis (Booking · Google Maps · Trustpilot) :

**1. Le produit core tient ses promesses — c'est un vrai atout.**
L'hébergement (3.64/5 sur 304 avis) et le rapport qualité-prix (3.95/5 sur 133 avis) sont les thèmes les mieux perçus. Les clients qui paient le prix premium l'acceptent : 68% des avis sur le rapport qualité-prix sont positifs (≥4/5). La nature et l'environnement reviennent systématiquement dans les verbatims 5 étoiles. Le positionnement écotourisme est compris et valorisé par la clientèle.

**2. La propreté est le frein numéro un à la recommandation.**
Avec une note moyenne de 3.07/5, c'est le thème le plus mal noté — sous la moyenne globale (3.65/5) sur presque tous les campings. C'est aussi le thème le plus cité dans les avis négatifs Google Maps. Agir sur ce seul point pourrait faire remonter la note globale de 0.3 à 0.5 point sur les campings en alerte.

**3. Les activités génèrent des attentes que l'expérience ne tient pas.**
Le thème Activités concentre 18% des avis avec une note de 3.13/5 — les clients en parlent beaucoup mais sont déçus. C'est un signal de désalignement entre les attentes générées par la communication et l'expérience réelle sur site.

**4. La politique d'annulation est le principal irritant contractuel.**
Les avis négatifs sur le rapport qualité-prix (4 sur 133) viennent exclusivement de Trustpilot et ne portent pas sur le prix — ils portent sur des remboursements refusés, des conditions générales peu lisibles, et une relation client perçue comme froide en cas de litige. Le risque est sur la gestion des cas exceptionnels, pas sur la tarification.

**Points de référence internes :** Le Moulin (4.26/5) et Font Romeu (3.80/5) surperforment significativement. Leurs pratiques sur l'accueil et la gestion des hébergements méritent d'être analysées et diffusées en interne.

---

## 📊 Résultats du corpus

| Source | Avis | Note moyenne |
|---|---|---|
| Google Maps | 450 | 3.00 / 5 |
| Booking | 336 | 4.30 / 5 |
| Trustpilot | 12 | 1.25 / 5 |
| **Total** | **798** | **3.65 / 5** |

> ⚠️ L'écart entre sources reflète un biais de plateforme réel, pas une anomalie. Booking filtre des clients vérifiés post-séjour (satisfaction haute). Trustpilot attire principalement les insatisfaits (biais négatif fort). Google Maps est la source la plus représentative.

| Camping | Note moy. | Thème dominant | Statut |
|---|---|---|---|
| Le Moulin | 4.26 / 5 | Qualité/Prix | 🟢 OK |
| Font Romeu | 3.80 / 5 | Hébergement | 🟢 OK |
| Arcachon | 3.75 / 5 | Hébergement | 🟡 Attention |
| Gorges du Verdon | 3.63 / 5 | Hébergement | 🟡 Attention |
| Sarlat | 3.55 / 5 | Qualité/Prix | 🟡 Attention |
| Versailles | 3.51 / 5 | Hébergement | 🟡 Attention |
| Lac Serre-Ponçon | 3.39 / 5 | Hébergement | 🔴 Alerte |
| Dieulefit | 3.29 / 5 | Activités | 🔴 Alerte |
| Rambouillet | 3.27 / 5 | Hébergement | 🔴 Alerte |
| Sud Ardèche | 3.24 / 5 | Activités | 🔴 Alerte |

---

## 🏗️ Architecture du pipeline

```
Booking · Google Maps · Trustpilot
         │
         ▼
   [Scraping]
   Selenium + Scrapling (StealthyFetcher)
   798 avis · 10 campings · 3 sources
         │
         ▼
   [Nettoyage & fusion]
   Normalisation notes · Détection langue (langdetect)
   Déduplication · Standardisation noms établissements
         │
         ▼
   [Classification thématique]
   BART zero-shot (facebook/bart-large-mnli)
   Labels EN → mapping FR · multi_label=True
   Précision validée : ~85% (20 avis échantillon manuel)
         │
         ▼
   [Dashboard Streamlit]
   Vue Commerciale : KPIs · alertes · notes par camping
   Vue Marketing : thèmes · heatmap · nuage de mots · verbatims
```

---

## 🛠️ Stack technique

| Composant | Technologie | Choix |
|---|---|---|
| **Collecte** | Selenium, Scrapling (StealthyFetcher) | Scrapling pour contourner la protection Cloudflare (Trustpilot) |
| **Traitement** | pandas, langdetect | Détection langue sur 6 langues détectées |
| **Classification** | `facebook/bart-large-mnli` | Zero-shot, labels EN pour meilleure précision sur texte FR |
| **Dashboard** | Streamlit + Plotly | Deux vues métier distinctes (Commercial / Marketing) |

---

## 🤖 Collaboration avec Claude (Anthropic)

Ce projet a été développé en collaboration active avec **Claude Sonnet** (Anthropic).

**Ce que Claude a fait :**
La rédaction de l'ensemble des scripts Python a été déléguée à Claude : scrapers (Booking, Google Maps, Trustpilot, TripAdvisor), pipeline de nettoyage et fusion (`data_merger.py`), classification thématique (`topic_classification.py`), et dashboard Streamlit (`app.py`). Claude a également assuré le débogage itératif en temps réel (sélecteurs CSS, gestion des erreurs, chemins relatifs).

**Ce que j'ai fait :**
La direction du projet, les choix analytiques et techniques (BART zero-shot vs alternatives, taxonomie des 7 thèmes, seuils d'alerte, structure du dashboard), la validation manuelle des résultats ML, et la formulation des insights business. Chaque script produit par Claude a été testé, validé et ajusté selon les résultats réels.

**Pourquoi cette transparence ?**
Utiliser un assistant IA pour accélérer la production de code est une compétence en soi — savoir formuler le bon problème, valider les outputs, et garder la maîtrise analytique. C'est exactement ce qu'un Business Analyst fait avec une équipe data.

---

## 📦 Installation

```bash
git clone https://github.com/TON_USERNAME/huttopia-voc.git
cd huttopia-voc
pip install -r requirements.txt

# Installer les navigateurs Scrapling (pour TripAdvisor)
scrapling install
```

---

## 🚀 Lancer le pipeline

```bash
# 1. Collecte
python scraping/trustpilot_scraper.py
python scraping/booking_scraper.py
python scraping/maps_selenium.py

# 2. Fusion & nettoyage
python processing/data_merger.py

# 3. Classification thématique (~80 min sur CPU)
python ml/topic_classification.py

# 4. Dashboard
streamlit run dashboard/app.py
```

---

## 📊 Thèmes de classification

7 labels définis dans `config/labels.py`, passés en anglais au modèle BART pour de meilleures performances sur du texte français :

| Label FR | Label EN (modèle) |
|---|---|
| Accueil et personnel | Welcome and staff |
| Hébergement et confort | Accommodation and comfort |
| Nature et environnement | Nature and environment |
| Propreté et sanitaires | Cleanliness and sanitation |
| Restauration et alimentation | Food and dining |
| Activités et animations | Activities and entertainment |
| Rapport qualité-prix | Value for money |

---

## 🗺️ Roadmap

- [x] Collecte : 798 avis (Booking + Google Maps + Trustpilot)
- [x] Nettoyage, fusion, détection langue (6 langues)
- [x] Classification thématique BART (~85% précision)
- [x] Dashboard Streamlit (Vue Commerciale + Vue Marketing)
- [x] Nuage de mots par thème et tonalité
- [ ] Analyse de sentiment par thème (en cours)
- [ ] README insights finalisé après sentiment
- [ ] V2 : benchmark concurrentiel (Homair, Sandaya, Sites & Paysages)

---

## ⚠️ Limites de l'analyse

- **TripAdvisor non inclus** : protection anti-bot trop agressive en 2026, source abandonnée après tentative avec Scrapling.
- **Précision classification ~85%** : validée sur 20 avis (échantillon manuel). Le modèle sur-classe en "Hébergement" sur les avis multi-thèmes.
- **Dates manquantes** : 90% des avis Google Maps n'ont pas de date exploitable — aucune analyse temporelle possible sur cette source.
- **Trustpilot biaisé** : 11/12 avis à 1 étoile. Source utile pour les signaux d'alerte marque, non représentative de la satisfaction globale.

---

## 👤 Auteur

Projet réalisé dans le cadre d'une candidature au poste **Business Analyst Commercial & Marketing** chez Huttopia.  
Développé avec l'assistance de **Claude Sonnet** (Anthropic) pour la production des scripts.

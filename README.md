# 🏕️ Huttopia — Voice of Customer

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red.svg)](https://streamlit.io/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-BART-yellow.svg)](https://huggingface.co/)
[![Claude](https://img.shields.io/badge/Développé_avec-Claude_Sonnet-blueviolet.svg)](https://claude.ai/)

---

## Contexte business

Huttopia positionne ses campings-nature sur un segment premium avec une promesse d'expérience authentique en pleine nature. Pour une équipe Commercial & Marketing, la question n'est pas "combien d'étoiles ?" mais **"où se situe l'écart entre la promesse et l'expérience vécue, et que faire en priorité ?"**

Ce projet analyse 798 avis clients collectés sur Booking, Google Maps et Trustpilot pour répondre à cette question avec des données concrètes.

---

## Questions business

1. Le positionnement qualité/prix premium est-il perçu positivement par les clients ?
2. Quels sont les irritants principaux qui dégradent la satisfaction ?
3. Quels campings nécessitent une attention prioritaire ?

---

## 🖥️ Dashboard

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

## Insights & Recommandations

> **Note méthodologique importante**
> Les notes moyennes par thème et par camping sont calculées sur l'ensemble du corpus, dont 56% d'avis Google Maps. Or, les avis Google Maps sans note numérique explicite reçoivent une valeur par défaut de 3.0/5 dans le pipeline — ce qui tire artificiellement les moyennes vers 3.0 sans refléter une vraie évaluation. **Chaque insight ci-dessous a donc été vérifié par lecture des verbatims**, ce qui a conduit à invalider ou nuancer plusieurs conclusions que les seules notes auraient suggérées (notamment sur les Activités et les campings en alerte). Les recommandations sont fondées sur les verbatims, pas sur les notes agrégées.

### 1. ✅ Le positionnement premium est validé par les clients

**Constat :** Le rapport qualité-prix est le thème le mieux noté du corpus (3.95/5 sur 133 avis). 68% des avis sur ce thème sont positifs (≥4/5). Seulement 4 avis sur 133 (3%) sont franchement négatifs — et ils portent sur la politique d'annulation, pas sur le prix.

**Insight :** Le prix premium est accepté. Les clients qui séjournent chez Huttopia comprennent et valident le positionnement. L'hébergement (3.64/5 sur 304 avis, soit 38% du corpus) confirme que le produit core tient ses promesses. Parmi les 102 avis 5 étoiles, 25% mentionnent explicitement la nature, le calme ou l'environnement comme point fort — le positionnement écotourisme résonne chez une part significative de la clientèle la plus satisfaite.

**Recommandation :** Intégrer le Rapport Qualité/Prix comme KPI stratégique dans le reporting commercial mensuel. Seuil d'alerte à définir à 3.5/5 — toute dégradation signal une remise en cause du positionnement premium à investiguer immédiatement.

---

### 2. ⚠️ La propreté : un signal réel mais localisé

**Constat :** Propreté est le thème le moins bien noté du corpus (3.07/5 sur 73 avis). Cependant, la lecture des verbatims nuance ce chiffre — les notes à 3.00/5 sur Google Maps sont en partie un artefact technique (valeur par défaut attribuée aux avis sans note numérique).

**Ce que les verbatims révèlent réellement :**

| Camping | Signal verbatims | Problème identifié |
|---|---|---|
| Arcachon | 🔴 Négatif documenté | Odeurs nauséabondes, sanitaires mal entretenus, non chauffés en hiver |
| Rambouillet | 🟡 Mixte | Avis contradictoires — problème de consistance selon la période |
| Gorges du Verdon | 🟢 Positif | Sanitaires bien entretenus mentionnés explicitement |
| Sarlat | 🟡 Accessibilité | Sanitaires propres mais trop éloignés de certains emplacements en haute saison |

**Recommandation :** Concentrer l'attention sur Arcachon (signal négatif clair et répété) et Rambouillet (consistance variable selon la période). Pour Sarlat, la question est davantage d'optimisation de la disposition des sanitaires que de propreté.

---

### 3. ✅ Les activités sont bien perçues — le signal négatif était un artefact

**Constat initial :** La note moyenne Activités (3.13/5 sur 148 avis) semblait indiquer un problème. La lecture des verbatims invalide cette conclusion.

**Ce que les verbatims révèlent :** Sur les 4 campings avec une note Activités à 3.00/5 (Dieulefit, Rambouillet, Arcachon, Sud Ardèche), les verbatims sont **majoritairement positifs** — piscines appréciées, animations enfants citées positivement, activités outdoor valorisées. La note 3.00/5 est le fallback attribué aux avis Google Maps sans note numérique explicite, pas une évaluation négative des activités.

**Exception notable :** Le Moulin se distingue avec une note Activités de 4.17/5 — le seul camping où la note reflète une vraie évaluation positive documentée dans les verbatims.

**Recommandation :** Ce thème ne nécessite pas d'action corrective immédiate. En revanche, les verbatims positifs sur les activités sont un matériau utile pour la communication marketing — les clients valorisent l'offre existante, elle mérite d'être mieux mise en avant.

---

### 4. 🔴 Campings en alerte globale — et limites de l'analyse

Les campings suivants ont une note globale inférieure à 3.4/5. **Attention : 51 à 60 avis sur 64 dans ces campings sont à 3.0/5 par défaut (fallback Google Maps)** — les notes agrégées sont à interpréter avec précaution. Il n'y a pas d'avis franchement négatifs (≤2.5) dans le corpus pour ces campings, ce qui limite les conclusions.

| Camping | Note globale | Avis négatifs (≤2.5) | Signal verbatims |
|---|---|---|---|
| Sud Ardèche | 3.24 / 5 | 0 | Majoritairement positifs |
| Rambouillet | 3.27 / 5 | 0 | Mixte (propreté variable selon période) |
| Dieulefit | 3.29 / 5 | 0 | Majoritairement positifs |
| Lac Serre-Ponçon | 3.39 / 5 | 0 | Non vérifié |

**Ces campings méritent une surveillance** mais les données disponibles ne permettent pas de conclure à un problème structurel. Une collecte d'avis supplémentaires (notamment TripAdvisor, non accessible) serait nécessaire pour confirmer.

---

### 5. ⚠️ La politique d'annulation : signal faible mais cohérent

**Constat :** Les 4 avis négatifs sur le rapport qualité-prix (tous sur Trustpilot, 1.0/5) portent exclusivement sur la rigidité de la politique d'annulation face à des cas de force majeure — trois verbatims mentionnent explicitement une annulation refusée pour raison médicale, un quatrième signale la suppression d'un avis négatif par Huttopia.

**Nuance importante :** Trustpilot concentre 12 avis au total sur Huttopia, dont 11 à 1 étoile. La plateforme fonctionne comme un exutoire pour les clients les plus insatisfaits — elle ne reflète pas la satisfaction globale. Ces 4 avis représentent un signal faible en volume mais cohérent en contenu : ils convergent tous vers le même irritant (politique d'annulation), ce qui lui donne une certaine valeur qualitative malgré le faible effectif.

**Insight :** Le problème n'est pas le prix mais la gestion des situations exceptionnelles. Un client qui ne peut pas annuler suite à une hospitalisation et se voit refuser tout remboursement devient un détracteur actif.

**Recommandation :** À confirmer sur un corpus plus large (TripAdvisor, enquêtes internes) avant toute décision. Si confirmé, revoir la politique d'annulation pour les cas de force majeure documentés (certificat médical) — le coût d'un geste commercial ciblé est nettement inférieur au coût réputationnel d'un avis 1 étoile public.

---

## Corpus & Méthodologie

**798 avis · 10 campings · 3 sources · 6 langues détectées**

| Source | Avis | Note moyenne |
|---|---|---|
| Google Maps | 450 (56%) | 3.00 / 5 |
| Booking | 336 (42%) | 4.30 / 5 |
| Trustpilot | 12 (2%) | 1.25 / 5 |

> ⚠️ **Biais de plateforme :** l'écart entre sources est réel et attendu. Booking filtre des clients vérifiés post-séjour. Trustpilot concentre les insatisfaits. Google Maps est la source la plus représentative de la satisfaction réelle.

**Classification thématique :** BART zero-shot (`facebook/bart-large-mnli`), labels passés en anglais pour de meilleures performances sur texte français, 7 thèmes. Précision validée manuellement sur 20 avis : ~85%.

---

## Limites méthodologiques

- **Corpus partiel :** 798 avis sur 10 campings (sur 56+ sites Huttopia France). Les insights sont indicatifs, à confirmer sur un corpus élargi.
- **TripAdvisor non inclus :** protection anti-bot trop agressive, source abandonnée après tentative avec Scrapling.
- **Dates manquantes :** 90% des avis Google Maps sans date — aucune analyse temporelle possible sur cette source.
- **Notes Google Maps :** les avis sans note numérique reçoivent une valeur par défaut (3.0/5) — les moyennes Google sont à interpréter avec précaution.
- **Précision classification ~85% :** le modèle sur-classe en "Hébergement" sur les avis multi-thèmes.

---

## Stack technique

| Composant | Technologie |
|---|---|
| Collecte | Selenium, Scrapling (StealthyFetcher) |
| Traitement | pandas, langdetect |
| Classification thématique | `facebook/bart-large-mnli` (zero-shot) |
| Dashboard | Streamlit + Plotly |

```bash
# Installation
git clone https://github.com/TON_USERNAME/huttopia-voc.git
cd huttopia-voc
pip install -r requirements.txt

# Lancer le dashboard
streamlit run dashboard/app.py
```

---

## Collaboration avec Claude (Anthropic)

Ce projet a été développé en collaboration active avec **Claude Sonnet** (Anthropic).

La rédaction des scripts Python a été déléguée à Claude : scrapers, pipeline de nettoyage, classification thématique, dashboard. La direction analytique, les choix méthodologiques, la validation des résultats ML et la formulation des insights restent de ma responsabilité. Chaque script a été testé et validé sur les données réelles.

Utiliser un assistant IA pour accélérer la production de code est une compétence à part entière — savoir formuler le bon problème, valider les outputs et garder la maîtrise analytique est précisément ce qu'un Business Analyst fait avec une équipe data.

---

## Auteur

Projet réalisé dans le cadre d'une candidature au poste **Business Analyst Commercial & Marketing** chez Huttopia.

*Analyse réalisée sur données publiques (avis Booking, Google Maps, Trustpilot) dans le cadre d'une candidature. Les conclusions reflètent une analyse externe et ne constituent pas un positionnement officiel d'Huttopia.*

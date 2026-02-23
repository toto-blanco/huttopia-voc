# ✅ Phase 1 — Cadrage & Setup : TERMINÉE

## 📋 Checklist complète

### ✅ 1. Structure du repo créée
```
huttopia-voc/
├── config/
│   ├── __init__.py
│   └── labels.py              ← 7 thèmes + mots-clés
├── scraping/
│   ├── __init__.py
│   ├── trustpilot_scraper.py  ← Placeholder avec signatures
│   └── google_scraper.py      ← Placeholder avec signatures
├── processing/
│   ├── __init__.py
│   └── clean_reviews.py       ← Placeholder
├── ml/
│   ├── __init__.py
│   ├── sentiment_analysis.py  ← Placeholder BERT
│   └── topic_classification.py ← Placeholder BART
├── dashboard/
│   ├── __init__.py
│   └── app.py                 ← Structure 2 onglets
├── data/
│   ├── raw/                   ← Dans .gitignore
│   └── processed/             ← Dans .gitignore
├── notebooks/
│   └── exploration.ipynb      ← Template
├── .gitignore                 ← Protège data/ et .env
├── .env.example               ← Template clé API
├── requirements.txt           ← Dépendances V1
├── README.md                  ← Documentation projet
└── test_access.py             ← Script de test sources
```

### ✅ 2. Les 7 thèmes de classification définis

Définis dans `config/labels.py` — **NON MODIFIABLE** sans retraiter le dataset :

1. **accueil et personnel**
2. **hébergement et confort**
3. **nature et environnement**
4. **propreté et sanitaires**
5. **restauration et alimentation**
6. **activités et animations**
7. **rapport qualité-prix**

Chaque thème inclut :
- Label complet pour BART zero-shot
- Nom d'affichage court pour le dashboard
- Mots-clés indicatifs pour validation manuelle

### ✅ 3. Champ `brand` anticipé pour la V2

Le schéma de données est conçu dès la V1 avec un champ `brand` :
```python
# Colonnes du DataFrame
['id', 'brand', 'source', 'date', 'note_brute', 'texte', 'langue']
```

Cela permet d'appliquer directement la même pipeline aux concurrents en V2 sans refonte.

### ✅ 4. Git initialisé avec premier commit
```bash
Commit: e7f791d
Message: "feat: init project structure with 7 topic labels and V1/V2 architecture"
Fichiers: 18 fichiers, 1075 lignes
```

---

## 🚀 Prochaines étapes — Phase 2 : Collecte

### Actions immédiates

1. **Tester l'accès aux sources**
   ```bash
   cd huttopia-voc
   python test_access.py
   ```
   
   Attendu :
   - ✅ Trustpilot status 200 ou identifier le blocage 403
   - ✅ Google Places API accessible (si clé dispo)

2. **Créer le compte GitHub et pousser le repo**
   ```bash
   # Créer un repo sur github.com : huttopia-voc
   git remote add origin https://github.com/TON_USERNAME/huttopia-voc.git
   git push -u origin main
   ```

3. **Implémenter le scraper Trustpilot**
   - Ouvrir `scraping/trustpilot_scraper.py`
   - Compléter la fonction `scrape_trustpilot()`
   - Tester sur 1 page avant de passer au volume complet

4. **Installer les dépendances**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## 📊 Critères de passage validés

| Critère | Status | Preuve |
|---------|--------|--------|
| Repo initialisé | ✅ | Structure complète créée |
| Schéma de données défini | ✅ | `config/labels.py` avec 7 thèmes |
| Champ `brand` anticipé | ✅ | Présent dans schéma commenté |
| Git commité | ✅ | Commit e7f791d |

---

## 💡 Rappel : Architecture V1 vs V2

### Ce qui ne change PAS entre V1 et V2
- ✅ Les 7 labels thématiques
- ✅ Le schéma SQLite
- ✅ Les modèles ML (BERT + BART)
- ✅ Le pipeline de traitement

### Ce qui s'ajoute en V2
- 3 scrapers supplémentaires (Homair, Sites et Paysages, Sandaya)
- 1 onglet "Benchmark" dans le dashboard
- Radar chart comparatif

**Effort estimé V1 → V2 : ~3 jours**

---

## 🎯 Objectif Phase 2

**Critère de passage** : ≥ 300 avis Huttopia stockés avec les colonnes :
- `id`, `brand`, `source`, `date`, `note_brute`, `texte`, `langue_detectee`

**Durée estimée** : 1,5 jour

---

**Phase 1 validée le** : $(date)
**Temps réel passé** : [à remplir]
**Prêt pour Phase 2** : ✅

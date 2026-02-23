"""
Configuration des labels thématiques pour la classification NLP.

IMPORTANT : NE PAS MODIFIER ces labels sans retraiter l'intégralité du dataset.
Les mêmes labels sont utilisés en V1 (Huttopia seul) et V2 (Benchmark concurrentiel).
"""

# Labels utilisés pour la classification zero-shot (BART)
THEMES = [
    "accueil et personnel",
    "hébergement et confort",
    "nature et environnement",
    "propreté et sanitaires",
    "restauration et alimentation",
    "activités et animations",
    "rapport qualité-prix",
]

# Noms courts pour l'affichage dans le dashboard
THEME_DISPLAY_NAMES = {
    "accueil et personnel": "Accueil",
    "hébergement et confort": "Hébergement",
    "nature et environnement": "Nature",
    "propreté et sanitaires": "Propreté",
    "restauration et alimentation": "Restauration",
    "activités et animations": "Activités",
    "rapport qualité-prix": "Qualité/Prix",
}

# Mots-clés indicatifs par thème (pour validation manuelle)
THEME_KEYWORDS = {
    "accueil et personnel": ["personnel", "accueil", "équipe", "staff", "souriant", "aide", "service"],
    "hébergement et confort": ["tente", "chalet", "lodge", "cabane", "literie", "chambre", "confort"],
    "nature et environnement": ["nature", "forêt", "verdure", "cadre", "paysage", "calme", "environnement"],
    "propreté et sanitaires": ["propre", "sale", "sanitaires", "douches", "WC", "nettoyage", "hygiène"],
    "restauration et alimentation": ["restaurant", "bar", "repas", "nourriture", "épicerie", "cuisine"],
    "activités et animations": ["piscine", "activités", "animations", "enfants", "vélo", "jeux", "sport"],
    "rapport qualité-prix": ["prix", "rapport qualité", "cher", "valeur", "tarif", "coût"],
}

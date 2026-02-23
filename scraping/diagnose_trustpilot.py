"""
Script de diagnostic pour analyser la structure HTML de Trustpilot.
"""

import requests
from bs4 import BeautifulSoup

url = "https://fr.trustpilot.com/review/www.huttopia.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("Récupération de la page...")
response = requests.get(url, headers=headers, timeout=10)

if response.status_code == 200:
    print(f"✅ Status: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Sauvegarder le HTML complet
    with open('trustpilot_page.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("✅ Page sauvegardée dans trustpilot_page.html")
    
    # Analyse des articles
    articles = soup.find_all('article')
    print(f"\n📊 Nombre d'articles trouvés: {len(articles)}")
    
    if articles:
        first = articles[0]
        
        # Sauvegarder le premier article pour analyse détaillée
        with open('first_article.html', 'w', encoding='utf-8') as f:
            f.write(first.prettify())
        print("✅ Premier article sauvegardé dans first_article.html")
        
        print("\n" + "="*60)
        print("ANALYSE DU PREMIER ARTICLE")
        print("="*60)
        
        # 1. Chercher les éléments de rating
        print("\n1️⃣ Recherche de la NOTE (rating):")
        print("-" * 40)
        
        # Méthode 1: data-service-review-rating
        rating_attr = first.find(attrs={'data-service-review-rating': True})
        if rating_attr:
            print(f"✅ Attribut data-service-review-rating: {rating_attr.get('data-service-review-rating')}")
        
        # Méthode 2: class avec 'star' ou 'rating'
        for elem in first.find_all(class_=lambda x: x and ('star' in str(x).lower() or 'rating' in str(x).lower())):
            print(f"   Tag: <{elem.name}>, Classes: {elem.get('class')}")
            if elem.get('aria-label'):
                print(f"   → aria-label: {elem.get('aria-label')}")
        
        # Méthode 3: Chercher des images avec alt="X étoiles"
        imgs = first.find_all('img', alt=lambda x: x and 'étoile' in x.lower())
        for img in imgs:
            print(f"   Image alt: {img.get('alt')}")
        
        # 2. Chercher le TEXTE de l'avis
        print("\n2️⃣ Recherche du TEXTE de l'avis:")
        print("-" * 40)
        
        # Méthode 1: p avec class contenant 'review-content' ou 'text'
        for elem in first.find_all(['p', 'div'], class_=lambda x: x and ('review' in str(x).lower() or 'text' in str(x).lower() or 'content' in str(x).lower())):
            text = elem.get_text(strip=True)
            if text and len(text) > 20:
                print(f"   Tag: <{elem.name}>, Classes: {elem.get('class')}")
                print(f"   → Texte: {text[:100]}...")
        
        # 3. Chercher la DATE
        print("\n3️⃣ Recherche de la DATE:")
        print("-" * 40)
        
        # Méthode 1: balise <time>
        time_elem = first.find('time')
        if time_elem:
            print(f"✅ Balise <time>:")
            print(f"   → datetime: {time_elem.get('datetime')}")
            print(f"   → texte: {time_elem.get_text(strip=True)}")
        
        # Méthode 2: data-service-review-date
        date_attr = first.find(attrs={'data-service-review-date': True})
        if date_attr:
            print(f"✅ Attribut data-service-review-date: {date_attr.get('data-service-review-date')}")
        
        # 4. Afficher toutes les classes uniques dans l'article
        print("\n4️⃣ Toutes les classes CSS utilisées:")
        print("-" * 40)
        all_classes = set()
        for elem in first.find_all(class_=True):
            all_classes.update(elem.get('class'))
        
        for cls in sorted(all_classes):
            print(f"   - {cls}")
        
        print("\n" + "="*60)
        print("💡 RECOMMANDATION:")
        print("="*60)
        print("Ouvre les fichiers HTML sauvegardés et cherche manuellement:")
        print("1. La note (cherche '5 étoiles', 'rating', ou un nombre)")
        print("2. Le texte de l'avis (paragraphe le plus long)")
        print("3. La date (cherche une date ISO ou 'il y a X jours')")
        
    else:
        print("❌ Aucun article trouvé - la structure a peut-être changé")
        
else:
    print(f"❌ Status: {response.status_code}")
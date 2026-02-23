"""
Script de test pour vérifier l'accès aux sources de données.

À exécuter en Phase 1, puis supprimer du repo.
"""

import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()


def test_trustpilot():
    """
    Teste l'accès à Trustpilot.
    """
    
    print("\n🔍 Test Trustpilot...")
    
    url = "https://fr.trustpilot.com/review/www.huttopia.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Trustpilot accessible (status 200)")
            
            # Vérifier la présence d'avis
            soup = BeautifulSoup(response.content, 'html.parser')
            reviews = soup.find_all('article')
            print(f"   Nombre d'articles trouvés: {len(reviews)}")
            
            if len(reviews) > 0:
                print("   ✅ Structure HTML semble valide")
            else:
                print("   ⚠️ Aucun article trouvé - la structure HTML a peut-être changé")
            
        elif response.status_code == 403:
            print("❌ Trustpilot bloque les requêtes (403 Forbidden)")
            print("   Solutions:")
            print("   - Utiliser Selenium avec un vrai navigateur")
            print("   - Ajouter des délais aléatoires entre requêtes")
            print("   - Utiliser un dataset Kaggle de secours")
            
        else:
            print(f"⚠️ Status code inattendu: {response.status_code}")
        
        return response.status_code
        
    except Exception as e:
        print(f"❌ Erreur lors de la connexion: {e}")
        return None


def test_google_places():
    """
    Teste l'accès à l'API Google Places.
    """
    
    print("\n🔍 Test Google Places API...")
    
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    
    if not api_key:
        print("⚠️ GOOGLE_PLACES_API_KEY non trouvée dans .env")
        print("   Pour utiliser Google Places:")
        print("   1. Créer un projet sur console.cloud.google.com")
        print("   2. Activer Places API")
        print("   3. Créer une clé API")
        print("   4. L'ajouter dans .env")
        return None
    
    # Test simple: recherche de texte
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": "Huttopia France",
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            if data.get("status") == "OK":
                results = data.get("results", [])
                print(f"✅ Google Places API accessible")
                print(f"   Nombre de résultats: {len(results)}")
                
                if len(results) > 0:
                    print(f"   Premier résultat: {results[0].get('name')}")
                
            elif data.get("status") == "REQUEST_DENIED":
                print("❌ Requête refusée - vérifier la clé API")
                print(f"   Message: {data.get('error_message', 'N/A')}")
            else:
                print(f"⚠️ Status API: {data.get('status')}")
        else:
            print(f"❌ Status HTTP: {response.status_code}")
        
        return response.status_code
        
    except Exception as e:
        print(f"❌ Erreur lors de la connexion: {e}")
        return None


def test_tripadvisor():
    """
    Teste l'accès à TripAdvisor (optionnel Phase 2).
    """
    
    print("\n🔍 Test TripAdvisor...")
    print("⚠️ TripAdvisor bloque souvent le scraping")
    print("   Priorité basse - à tester uniquement si temps disponible")
    
    # TODO: Implémenter si besoin en Phase 2


def main():
    """
    Lance tous les tests d'accès aux sources.
    """
    
    print("=" * 60)
    print("TEST D'ACCÈS AUX SOURCES DE DONNÉES")
    print("=" * 60)
    
    # Test des sources
    trustpilot_status = test_trustpilot()
    google_status = test_google_places()
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    
    sources_ok = []
    sources_ko = []
    
    if trustpilot_status == 200:
        sources_ok.append("Trustpilot")
    elif trustpilot_status is not None:
        sources_ko.append("Trustpilot")
    
    if google_status == 200:
        sources_ok.append("Google Places")
    elif google_status is not None:
        sources_ko.append("Google Places")
    
    if sources_ok:
        print(f"✅ Sources accessibles: {', '.join(sources_ok)}")
    
    if sources_ko:
        print(f"❌ Sources bloquées: {', '.join(sources_ko)}")
    
    if not sources_ok and not sources_ko:
        print("⚠️ Aucune source testée avec succès")
    
    print("\n💡 Recommandation:")
    if len(sources_ok) >= 1:
        print("   Phase 1 validée - passer à la Phase 2 (Collecte)")
    else:
        print("   Résoudre les blocages avant de passer en Phase 2")
        print("   Solution de secours: dataset Kaggle camping/hôtel")


if __name__ == "__main__":
    main()

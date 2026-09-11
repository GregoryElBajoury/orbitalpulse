import os
import logging
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement si un fichier .env est présent
load_dotenv()

# Configuration des logs pour suivre ce que fait le script proprement
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

API_URL = os.getenv("ISS_API_URL", "https://api.wheretheiss.at/v1/satellites/25544")

def fetch_iss_position():
    """Interroge l'API publique de l'ISS et retourne les données métriques."""
    try:
        logging.info("Interrogation de l'API ISS...")
        response = requests.get(API_URL, timeout=10)
        
        # Lève une exception si le statut HTTP indique une erreur
        response.raise_for_status()
        
        data = response.json()
        
        logging.info(
            f"Données reçues - "
            f"Lat: {data.get('latitude')}, "
            f"Lon: {data.get('longitude')}, "
            f"Altitude: {data.get('altitude')} km, "
            f"Vitesse: {data.get('velocity')} km/h, "
            f"Visibilité: {data.get('visibility')}"
        )
        return data

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"Erreur HTTP rencontrée : {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Erreur de connexion réseau : {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"L'appel API a expiré (Timeout) : {timeout_err}")
    except Exception as err:
        logging.error(f"Une erreur inattendue est survenue : {err}")
    
    return None

if __name__ == "__main__":
    fetch_iss_position()
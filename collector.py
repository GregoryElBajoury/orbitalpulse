import os
import logging
import requests
import psycopg2
from dotenv import load_dotenv

# Charger les variables d'environnement si un fichier .env est présent
load_dotenv()

# Configuration des logs pour suivre ce que fait le script proprement
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

API_URL = os.getenv("ISS_API_URL", "https://api.wheretheiss.at/v1/satellites/25544")

# Paramètres de connexion PostgreSQL (avec les valeurs par défaut de ton docker-compose)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("POSTGRES_DB", "orbitalpulse")
DB_USER = os.getenv("POSTGRES_USER", "iamgroot")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "iamgroot93420")

def fetch_iss_position():
    """Interroge l'API publique de l'ISS et retourne les données métriques."""
    try:
        logging.info("Interrogation de l'API ISS...")
        response = requests.get(API_URL, timeout=10)
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

def save_to_db(data):
    """Enregistre les données de télémétrie dans la base PostgreSQL."""
    if not data:
        return

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        query = """
            INSERT INTO iss_telemetry (latitude, longitude, altitude, velocity, visibility, captured_at)
            VALUES (%s, %s, %s, %s, %s, to_timestamp(%s))
        """
        cursor.execute(query, (
            data.get('latitude'),
            data.get('longitude'),
            data.get('altitude'),
            data.get('velocity'),
            data.get('visibility'),
            data.get('timestamp')
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Données de télémétrie insérées avec succès dans PostgreSQL.")
    
    except Exception as db_err:
        logging.error(f"Erreur lors de l'insertion en base de données : {db_err}")

if __name__ == "__main__":
    telemetry_data = fetch_iss_position()
    if telemetry_data:
        save_to_db(telemetry_data)
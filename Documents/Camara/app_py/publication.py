import pandas as pd
from sqlalchemy import create_engine, distinct
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from models import Publications
# Charger les variables d’environnement (.env)
load_dotenv()

# Configuration de la connexion à la base de données
db_user = os.getenv('MYSQL_USER')
db_password = os.getenv('MYSQL_PASSWORD')
db_host = os.getenv('MYSQL_HOST', 'localhost')
db_name = os.getenv('MYSQL_DATABASE')
db_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4"

# Créer le moteur SQLAlchemy
engine = create_engine(db_uri)
Session = sessionmaker(bind=engine)

def load_publications_from_db():
    session = Session()
    try:
        print("[INFO] Connexion à la base de données...")
        
        # Requête SQLAlchemy
        query = session.query(Publications)

        
        results = query.all()
        
        publications = {}
        for row in results:
            title_key = row.nom.lower().replace(' ', '_')
            image_filename = row.fichier if row.fichier else 'default.jpg'
            image_path = os.path.join('static', 'img', image_filename)

            if not os.path.exists(image_path):
                image_filename = "default.jpg"
                if not os.path.exists(os.path.join('static', 'img', image_filename)):
                    print("[ERROR] Image par défaut 'default.jpg' également manquante !")

            publication_data = {
                'title': row.nom,
                'region': row.nom_region,
                'date': row.date_publication,
                'description': row.description,
                'year': row.date_production,
                'Nom_fichier_image': image_filename
            }
            publications[title_key] = publication_data
        return publications
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement des publications : {e}")
        return {}
    finally:
        session.close()
        print("Publication: Session de base de données fermée.")

def get_regions():
    session = Session()
    try:
        print("[INFO] Connexion à la base de données pour les régions...")
        # Requête pour obtenir les régions distinctes
        regions = [row[0] for row in session.query(distinct(Publications.nom_region)).all()]
        return regions
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement des régions : {e}")
        return []
    finally:
        session.close()
        print("[INFO] Session de base de données fermée.")
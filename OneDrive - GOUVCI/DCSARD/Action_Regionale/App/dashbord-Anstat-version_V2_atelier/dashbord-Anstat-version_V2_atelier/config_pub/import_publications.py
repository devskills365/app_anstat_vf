import pandas as pd
import pymysql
from dotenv import load_dotenv
import os

# Charger les variables d’environnement (.env)
load_dotenv()

# Configuration MySQL depuis .env
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8mb4'
}

# Conversion explicite des colonnes de date
def safe_date(val):
    try:
        val = str(val)
        if len(val) == 4 and val.isdigit():
            return pd.to_datetime(val + "-01-01")
        return pd.to_datetime(val)
    except:
        return None

def importation():
    try:
        # Lire le fichier Excel
        df = pd.read_excel('static/data/publications2.xlsx')
        df.columns = df.columns.str.strip()  # Supprimer les espaces invisibles
        print("Colonnes détectées :", df.columns.tolist())

        # Vérifier que les colonnes attendues existent
        required_columns = ['Publications', 'nom de la publication', 'Région', 'Nom_fichier_image', 
                           'Description de la publication', 'Description', 'Annee de publication', "Date d'édition"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Colonnes manquantes dans le fichier Excel : {missing_columns}")

        # Appliquer le nettoyage sur les dates
        df['Annee de publication'] = df['Annee de publication'].apply(safe_date)
        df["Date d'édition"] = df["Date d'édition"].apply(safe_date)

        # Connexion MySQL
        connection = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                for _, row in df.iterrows():
                    sql = """
                        INSERT INTO publications (
                            categorie, nom, nom_region, nom_fichier_image, description, resume,
                            date_production, date_publication, mise_a_jour
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """
                    cursor.execute(sql, (
                        row.get('Publications', ''),
                        row.get('nom de la publication', ''),
                        row.get('Région', ''),
                        row.get('Nom_fichier_image', ''),
                        row.get('Description de la publication', ''),
                        row.get('Description', ''),
                        row.get('Annee de publication', None),
                        row.get("Date d'édition", None)
                    ))
                connection.commit()
                print("[INFO] Données importées avec succès.")
        finally:
            connection.close()
            print("[INFO] Connexion à la base de données fermée.")
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'importation : {e}")
        raise

def load_publications_from_db(region=None):
    try:
        print("[INFO] Connexion à la base de données...")
        connection = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        
        with connection.cursor() as cursor:
            if region:
                query = "SELECT * FROM publications WHERE nom_region = %s"
                cursor.execute(query, (region,))
            else:
                query = "SELECT * FROM publications"
                cursor.execute(query)
            results = cursor.fetchall()
    

        publications = {}
        for row in results:
            title_key = row['nom'].lower().replace(' ', '_')
            image_filename = row.get('fichier', 'default.jpg')
            image_path = os.path.join('static', 'img', image_filename)

            if not os.path.exists(image_path):

                image_filename = "default.jpg"
                if not os.path.exists(os.path.join('static', 'img', image_filename)):
                    print("[ERROR] Image par défaut 'default.jpg' également manquante !")

            publication_data = {
                'title': row['nom'],
                'region': row['nom_region'],
                'date': row['date_publication'],
                'description': row['description'],
                'year': row['date_production'],
                'Nom_fichier_image': image_filename
            }
            publications[title_key] = publication_data

        print("[INFO] Chargement des publications terminé.")
        return publications
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement des publications : {e}")
        return {}
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()
            print("[INFO] Connexion à la base de données fermée.")

def get_regions():
    try:
        print("[INFO] Connexion à la base de données pour les régions...")
        connection = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT nom_region FROM publications")
            regions = [row['nom_region'] for row in cursor.fetchall()]

        return regions
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement des régions : {e}")
        return []
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()
            print("[INFO] Connexion à la base de données fermée.")
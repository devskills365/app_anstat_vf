import pandas as pd
from dotenv import load_dotenv
import os
import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import db, Region, IndicateurV2, V1Indicateur, Indicateur, DirectionStatistique  # Importer les modèles

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import Region, Indicateur, V1Indicateur  # Importez vos modèles SQLAlchemy ici
import config as cf
from dotenv import load_dotenv
load_dotenv()

# Utiliser les variables d'environnement pour MySQL
host = os.getenv('MYSQL_HOST')
database = os.getenv('MYSQL_DATABASE')
#database2 = os.getenv('MYSQL_DATABASE2')
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')


import os
import mysql.connector
from mysql.connector import Error

def connect_to_mysql():
    """Se connecte à une base de données MySQL en utilisant les variables d'environnement."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            database=os.getenv('MYSQL_DATABASE'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD')
        )

        if connection.is_connected():
            print("✅ Connexion réussie à la base MySQL")
            return connection

    except Error as e:
        print(f"❌ Erreur de connexion : {e}")
        return None


# Création de la session SQLAlchemy
engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}/{database}"
)
Session = sessionmaker(bind=engine)
session = Session()

# Récupérer les régions sous forme de liste
def options_regions():
    try:
        # Récupérer les noms des régions avec SQLAlchemy
        regions = session.query(Region.nom_region).order_by(Region.nom_region.asc()).all()
        return [region[0] for region in regions]  # Liste des régions
    except Exception as e:
        print(f"Erreur lors de la récupération des régions : {e}")
        return []

# Récupérer les indicateurs sous forme de liste triée
def options_indicateur():
    try:
        # Récupérer les indicateurs avec SQLAlchemy
        indicateurs = session.query(Indicateur.nom_indicateur).all()
        return sorted([indicateur[0] for indicateur in indicateurs])  # Liste triée
    except Exception as e:
        print(f"Erreur lors de la récupération des indicateurs ---: {e}")
        return []

from sqlalchemy import func
from models import IndicateurV2, db  # Importer le modèle et db depuis models.py

# Obtenir la définition d'un indicateur choisi
def definition_indicateur(indicateur_choisi):
    print('Indicateur pris:',indicateur_choisi)
    try:
        # Requête pour récupérer la définition de l'indicateur
        result = db.session.query(IndicateurV2.definitions).filter(
            func.lower(IndicateurV2.indicateur) == indicateur_choisi.lower()
        ).first()
        
        if result and result[0]:  # Vérifie si le résultat existe et n'est pas None
            return result[0]  # Retourne la définition
        else:
            return f"Définition pour l'indicateur '{indicateur_choisi}' non trouvée."
    except Exception as e:
        print(f"Erreur lors de la récupération de la définition : {e}")
        return None

# Obtenir le mode de calcul d'un indicateur choisi
def mode_calcul_indicateur(indicateur_choisi):
    try:
        # Requête pour récupérer le mode de calcul de l'indicateur
        result = db.session.query(IndicateurV2.mode_calcul).filter(
            func.lower(IndicateurV2.indicateur) == indicateur_choisi.lower()
        ).first()
        
        if result and result[0]:  # Vérifie si le résultat existe et n'est pas None
            return result[0]  # Retourne le mode de calcul
        else:
            return f"Mode de calcul pour l'indicateur '{indicateur_choisi}' non trouvé."
    except Exception as e:
        print(f"Erreur lors de la récupération du mode de calcul : {e}")
        return None

# Charger des données depuis un fichier CSV
def get_data(filepath):
    try:
        df = pd.read_csv(filepath, sep=',')
        return df
    except Exception as e:
        print(f"Erreur lors du chargement du fichier CSV : {e}")
        return pd.DataFrame()  # Retourner un DataFrame vide en cas d'erreur




from contextlib import contextmanager
from sqlalchemy.orm import Session
import pandas as pd

@contextmanager
def session_scope():
    """Fournit un gestionnaire de contexte pour la session SQLAlchemy."""
    sess = Session(engine)
    try:
        yield sess
        sess.commit()
    except:
        sess.rollback()
        raise
    finally:
        sess.close()

def obtention_data_mysql_niveauDesagr(indicateur_name, offset=0, limit=25):
    try:
        with session_scope() as session:
            # Requête pour récupérer toutes les colonnes
            query = session.query(
                V1Indicateur.Dimension,
                V1Indicateur.Modalites,
                V1Indicateur.Indicateurs,
                V1Indicateur.Annee,
                V1Indicateur.Valeur
            ).filter(V1Indicateur.Indicateurs == indicateur_name)

    

            # Conversion en DataFrame
            df = pd.read_sql(query.statement, engine)

            # Vérifier si le DataFrame est vide
            if df.empty:
                print(f"Aucune donnée trouvée pour l'indicateur '{indicateur_name}'")
                return pd.DataFrame()

            # Garder uniquement les lignes avec des Dimension distinctes
            df = df.drop_duplicates(subset=['Dimension'], keep='first')

            # Appliquer offset et limit sur le DataFrame
            df = df.iloc[offset:offset + limit]

            return df
    except Exception as e:
        print(f"Erreur lors de la récupération des données MySQL pour l'indicateur '{indicateur_name}' : {str(e)}")
        return pd.DataFrame()
def obtention_data_mysql_requete(indicateur_name, offset=0, limit=1000):
    try:
        with session_scope() as session:
            # Requête pour récupérer toutes les colonnes
            query = session.query(
                V1Indicateur.Dimension,
                V1Indicateur.Modalites,
                V1Indicateur.Indicateurs,
                V1Indicateur.Annee,
                V1Indicateur.Valeur
            ).filter(V1Indicateur.Indicateurs == indicateur_name)

            # Conversion en DataFrame
            df = pd.read_sql(query.statement, session.bind) # session.bind est nécessaire pour lire la requête

            if df.empty:
                print(f"Aucune donnée trouvée pour l'indicateur '{indicateur_name}'")
                return pd.DataFrame()

            return df
    except Exception as e:
        print(f"Erreur lors de la récupération des données MySQL pour l'indicateur '{indicateur_name}' : {str(e)}")
        return pd.DataFrame()
    

def autocompletion():
    try:
        query = session.query(
          V1Indicateur.Indicateurs
        ).distinct()
        df = pd.read_sql(query.statement, engine)
        print('issue de queries:',df)
        return df
    except Exception as e:
        print(f"Erreur lors de la récupération des données MySQL : {e}")
        return pd.DataFrame()

#.filter(V1Indicateur.Region == region_name)
# Récupérer des données depuis MySQL pour une région spécifique
def get_data_from_mysql_VR(region_name,offset=0, limit=25):
    try:
        query = session.query(
            V1Indicateur.Dimension,
            V1Indicateur.Modalites,
            V1Indicateur.Indicateurs,
            V1Indicateur.Annee,
            V1Indicateur.Valeur
        ).filter(V1Indicateur.Region == region_name).offset(offset).limit(limit)
        
        df = pd.read_sql(query.statement, engine)
        return df
    except Exception as e:
        print(f"Erreur lors de la récupération des données MySQL : {e}")
        return pd.DataFrame()

# Insérer des données depuis un fichier Excel dans la base de données
def insert_data_from_excel_optimized(file_path):
    try:
        # Lire le fichier Excel
        df = pd.read_excel(file_path)
        df.columns = ['Dimension', 'Modalites', 'Indicateurs', 'Annee', 'Valeur']
        
        # Nettoyer la colonne 'Valeur'
        # 1. Convertir en chaîne de caractères pour pouvoir appliquer les méthodes de nettoyage
        df['Valeur'] = df['Valeur'].astype(str)
        # 2. Remplacer les virgules par des points
        df['Valeur'] = df['Valeur'].str.replace(',', '.', regex=False)
        # 3. Supprimer tout caractère non numérique, à l'exception des points décimaux
        df['Valeur'] = df['Valeur'].str.replace(r'[^\d.]', '', regex=True)
        # 4. Convertir la colonne en un type numérique
        # Les valeurs vides ou non convertibles deviennent NaN
        df['Valeur'] = pd.to_numeric(df['Valeur'])
        
        # Utiliser `to_sql` pour insérer les données
        # Le moteur d'insertion gérera la conversion de NaN en NULL
        df.to_sql('V1_indicateur', con=engine, if_exists='append', index=False)
        
        print("✅ Données insérées avec succès dans la table V1_indicateur.")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion des données : {e}")

        
file_path='C:/Users/DELL/OneDrive - GOUVCI/DCSARD/Action_Regionale/App/dashbord-Anstat-version_V2_atelier/dashbord-Anstat-version_V2_atelier/static/data/indica_nat_req_ok.xlsx'

if __name__=='__main__':
    insert_data_from_excel_optimized(file_path)


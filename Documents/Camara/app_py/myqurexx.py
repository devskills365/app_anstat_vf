import os
from contextlib import contextmanager

import mysql.connector
import pandas as pd
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from mysql.connector import Error
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from models import (
    db,
    DataRequete,
    Indicateur,
    IndicateurV2,
    Region,
    V1Indicateur,
    NiveauParIndicateurs
)

import config as cf

# =========================================================
# 📦 Chargement des variables d'environnement
# =========================================================
load_dotenv()

host = os.getenv('MYSQL_HOST')
database = os.getenv('MYSQL_DATABASE')
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')

# =========================================================
# 🔌 Connexion MySQL "brute" (pour debug uniquement)
# =========================================================
def connect_to_mysql():
    """Se connecte à une base de données MySQL en utilisant les variables d'environnement."""
    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )

        if connection.is_connected():
            print("✅ Connexion réussie à la base MySQL")
            return connection

    except Error as e:
        print(f"❌ Erreur de connexion : {e}")
        return None


# =========================================================
# ⚙️ Configuration SQLAlchemy (Session indépendante de Flask)
# =========================================================
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")
Session = sessionmaker(bind=engine)
session = Session()

# =========================================================
# 🌍 Fonctions utilitaires de récupération
# =========================================================
def options_regions():
    """Retourne la liste triée des régions."""
    try:
        regions = session.query(Region.nom_region).order_by(Region.nom_region.asc()).all()
        return [region[0] for region in regions]
    except Exception as e:
        print(f"Erreur lors de la récupération des régions : {e}")
        return []


def options_indicateur():
    """Retourne la liste triée des indicateurs."""
    try:
        indicateurs = session.query(Indicateur.nom_indicateur).all()
        return sorted([indicateur[0] for indicateur in indicateurs])
    except Exception as e:
        print(f"Erreur lors de la récupération des indicateurs : {e}")
        return []


# =========================================================
# 🧠 Fonctions sur les indicateurs (définition / mode de calcul)
# =========================================================
def definition_indicateur(indicateur_choisi):
    print('Indicateur pris:', indicateur_choisi)
    try:
        result = db.session.query(IndicateurV2.definitions).filter(
            func.lower(IndicateurV2.indicateur) == indicateur_choisi.lower()
        ).first()

        if result and result[0]:
            return result[0]
        else:
            return f"Définition pour l'indicateur '{indicateur_choisi}' non trouvée."
    except Exception as e:
        print(f"Erreur lors de la récupération de la définition : {e}")
        return None


def mode_calcul_indicateur(indicateur_choisi):
    try:
        result = db.session.query(IndicateurV2.mode_calcul).filter(
            func.lower(IndicateurV2.indicateur) == indicateur_choisi.lower()
        ).first()

        if result and result[0]:
            return result[0]
        else:
            return f"Mode de calcul pour l'indicateur '{indicateur_choisi}' non trouvé."
    except Exception as e:
        print(f"Erreur lors de la récupération du mode de calcul : {e}")
        return None


# =========================================================
# 📁 Chargement CSV
# =========================================================
def get_data(filepath):
    try:
        df = pd.read_csv(filepath, sep=',')
        return df
    except Exception as e:
        print(f"Erreur lors du chargement du fichier CSV : {e}")
        return pd.DataFrame()


# =========================================================
# 💾 Gestionnaire de contexte pour les sessions SQLAlchemy
# =========================================================
@contextmanager
def session_scope():
    """Fournit un gestionnaire de contexte pour la session SQLAlchemy."""
    sess = Session()  # ✅ Corrigé ici (ne pas passer engine)
    try:
        yield sess
        sess.commit()
    except Exception:
        sess.rollback()
        raise
    finally:
        sess.close()


# =========================================================
# 📈 Récupération de données MySQL (DataRequete)
# =========================================================
def obtention_data_mysql_requete(indicateur_name):
    try:
        with session_scope() as session:
            query = (
                session.query(NiveauParIndicateurs.cle_pivot_unique)
                .filter(NiveauParIndicateurs.Indcateurs == indicateur_name)
                
            )

            df = pd.read_sql(query.statement, session.bind)

            if df.empty:
                print(f"Aucune donnée trouvée pour l'indicateur '{indicateur_name}'")
                return pd.DataFrame()

            return df

    except Exception as e:
        print(f"Erreur lors de la récupération des données MySQL pour l'indicateur '{indicateur_name}' : {str(e)}")
        return pd.DataFrame()


# =========================================================
# 🔍 Autocomplétion des indicateurs
# =========================================================
def autocompletion():
    try:
        query = session.query(V1Indicateur.Indicateurs).distinct()
        df = pd.read_sql(query.statement, engine)
        print('Issue de queries:', df)
        return df
    except Exception as e:
        print(f"Erreur lors de la récupération des données MySQL : {e}")
        return pd.DataFrame()

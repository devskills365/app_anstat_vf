import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# 1. Connexion à la base de données
try:
    host = os.getenv('MYSQL_HOST')
    database = os.getenv('MYSQL_DATABASE')
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')

    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")
    connection = engine.connect()
    print("Connexion à la base de données établie avec succès.")
except Exception as err:
    print(f"Erreur de connexion à la base de données: {err}")
    exit()

# 2. Lecture du fichier Excel
file_path = "data.xlsx"

try:
    # Charger toutes les feuilles du classeur
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names
    print(f"Feuilles trouvées dans le classeur : {sheet_names}")
except FileNotFoundError:
    print(f"Erreur : Le fichier '{file_path}' est introuvable.")
    exit()
except Exception as err:
    print(f"Erreur lors de la lecture du fichier Excel : {err}")
    exit()

# 3. Requête d'insertion
insert_query = """
    INSERT INTO v1_indicateur (Dimension, Modalites, Indicateurs, Annee, Valeur)
    VALUES (:Dimension, :Modalites, :Indicateurs, :Annee, :Valeur)
"""

# 4. Insertion des données pour chaque feuille
total_inserted_rows = 0
try:
    for sheet_name in sheet_names:
        print(f"\n--- Traitement de la feuille : {sheet_name} ---")
        df = pd.read_excel(excel_file, sheet_name=sheet_name, dtype=str)
        
        # Supprimer les lignes entièrement vides
        df.dropna(how='all', inplace=True)
        
        if df.empty:
            print(f"La feuille '{sheet_name}' est vide ou contient uniquement des lignes vides. Aucune donnée à insérer.")
            continue

        inserted_rows_sheet = 0
        for i, row in df.iterrows():
            try:
                # Vérification des valeurs NaN ou incorrectes
                dimension = row.get('Dimension')
                modalites = row.get('Modalites')
                indicateurs = row.get('Indicateurs')
                annee = row.get('Année') # Attention à la casse "Année" vs "Annee"
                valeur = row.get('Valeurs') # Attention à la casse "Valeurs" vs "Valeur"

                # Convertir l'année en entier si possible, sinon la laisser comme chaîne
                try:
                    annee = int(float(str(annee).strip())) if pd.notna(annee) else None
                except ValueError:
                    print(f"Avertissement: Valeur d'année '{annee}' non numérique dans la feuille '{sheet_name}', ligne {i+2}. Conservée telle quelle.")
                    annee = str(annee).strip() if pd.notna(annee) else None

                # Convertir la valeur en float si possible, sinon la laisser comme chaîne
                try:
                    valeur = float(str(valeur).strip()) if pd.notna(valeur) else None
                except ValueError:
                    print(f"Avertissement: Valeur '{valeur}' non numérique dans la feuille '{sheet_name}', ligne {i+2}. Conservée telle quelle.")
                    valeur = str(valeur).strip() if pd.notna(valeur) else None

                # Optionnel : on peut ignorer les lignes où certaines colonnes clés sont nulles
                if pd.isna(dimension) or pd.isna(modalites) or pd.isna(indicateurs) or pd.isna(annee):
                    print(f"Ligne {i+2} (feuille '{sheet_name}') ignorée (valeurs manquantes obligatoires dans Dimension, Modalites, Indicateurs ou Année)")
                    continue

                data = {
                    'Dimension': dimension,
                    'Modalites': modalites,
                    'Indicateurs': indicateurs,
                    'Annee': annee,
                    'Valeur': valeur
                }

                result = connection.execute(text(insert_query), data)
                inserted_rows_sheet += result.rowcount

            except Exception as row_err:
                print(f"Ligne {i + 2} (feuille '{sheet_name}') ignorée (erreur) : {row_err}")
                continue
        
        total_inserted_rows += inserted_rows_sheet
        print(f"✅ Données insérées avec succès pour la feuille '{sheet_name}' : {inserted_rows_sheet} lignes insérées.")

    connection.commit()
    print(f"\n✅ Toutes les données ont été insérées avec succès : {total_inserted_rows} lignes insérées au total dans la table v1_indicateur.")

except Exception as err:
    print(f"\n❌ Erreur globale lors de l'insertion : {err}")
    connection.rollback()
finally:
    connection.close()
    print("Connexion à la base de données fermée.")
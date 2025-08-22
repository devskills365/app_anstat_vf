import pandas as pd
import mysql.connector
from mysql.connector import Error

# Database and file path configurations
DB_CONFIG = {
    'user': 'root',
    'password': '10080805Tohbi',
    'host': '127.0.0.1',
    'database': 'annuaire'
}
EXCEL_FILE_PATH = 'C:/Users/DELL/OneDrive - GOUVCI/DCSARD/Action_Regionale/App/dashbord-Anstat-version_V2_atelier/dashbord-Anstat-version_V2_atelier/static/data/MATRICE_COLLECTE_SANTE.xlsx'

def insert_data_from_excel():
    conn = None
    try:
        # 1. Connect to MySQL
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connexion à la base de données réussie.")

        # 2. Read the Excel file with pandas
        df = pd.read_excel(EXCEL_FILE_PATH, engine='openpyxl')
        print("Fichier Excel lu avec succès.")

        # Print columns and first few rows for debugging
        print('Colonnes dans excel:', df.columns.tolist())
        print('Premières lignes:', df.head().to_dict())

        # 3. Drop columns with NaN or empty headers
        df = df.loc[:, ~df.columns.isna()]
        df = df.loc[:, df.columns.str.strip() != '']

        # 4. Validate the number of columns
        expected_columns = ['Domaine', 'Indicateur', 'Année', 'Source', 'Région', 'Valeur']
        if len(df.columns) != len(expected_columns):
            raise ValueError(f"Expected {len(expected_columns)} columns, but found {len(df.columns)}: {df.columns.tolist()}")

        # 5. Rename columns to match expected names
        df.columns = expected_columns

        # 6. Filter to keep only required columns
        df_filtered = df[expected_columns]

        # 7. Correct column names for SQL table
        df_filtered.rename(columns={'Année': 'Annee', 'Région': 'Region'}, inplace=True)

        # 8. Replace NaN, empty strings, and 'nan' strings with None
        df_filtered = df_filtered.replace(['nan', 'NaN', 'NAN'], None)
        df_filtered = df_filtered.replace('', None)
        df_filtered = df_filtered.where(pd.notnull(df_filtered), None)

        # 9. Round Valeur to 2 decimal places to match DECIMAL(10, 2)
        df_filtered['Valeur'] = df_filtered['Valeur'].round(2)

        # 10. Drop rows with any missing values
        df_filtered = df_filtered.dropna()

        # 11. Check for problematic rows
        nan_rows = df_filtered[df_filtered.apply(lambda row: row.astype(str).str.lower().eq('nan').any(), axis=1)]
        if not nan_rows.empty:
            print("Rows containing 'nan' (case-insensitive):", nan_rows.to_dict())

        # 12. Truncate table
        cursor.execute("TRUNCATE TABLE `indicateurs_dashbord_region`")
        print("Table 'indicateurs_dashbord_region' vidée pour la réinsertion.")

        # 13. Prepare data for insertion
        insert_query = """
        INSERT INTO indicateurs_dashbord_region (Domaine, Indicateur, Annee, Source, Region, Valeur)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        data_to_insert = [tuple(row) for row in df_filtered.itertuples(index=False, name=None)]

        # 14. Log all rows to insert
        print("Nombre total de lignes à insérer :", len(data_to_insert))
        for i, row in enumerate(data_to_insert):
            print(f"Ligne {i}: {row}")

        # 15. Insert data
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()
        print(f"{cursor.rowcount} lignes insérées avec succès.")

    except Error as e:
        print(f"Erreur d'insertion dans la base de données : {e}")
        if conn and conn.is_connected():
            conn.rollback()

    except Exception as e:
        print(f"Erreur dans le traitement des données : {e}")
        if conn and conn.is_connected():
            conn.rollback()

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("Connexion MySQL fermée.")

if __name__ == '__main__':
    insert_data_from_excel()
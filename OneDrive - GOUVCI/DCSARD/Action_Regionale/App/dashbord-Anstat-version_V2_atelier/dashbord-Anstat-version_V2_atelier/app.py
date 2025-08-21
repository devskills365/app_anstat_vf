from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify,abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
import pandas as pd
import urllib
from io import StringIO
from datetime import datetime
from unidecode import unidecode
import sys
from itertools import chain
import my_queries as qr
import config as cf
import models as ml
from config import app, db 
import io
current_dir = os.path.dirname(os.path.abspath(__file__))
config_pub_path = os.path.join(current_dir, 'config_pub')
sys.path.append(config_pub_path)
import import_publications as conf_pub
global region_publication
region_publication="PORO"# Cette variable va nous permettre 
#https://colab.research.google.com/drive/1oBqwcSMb4YTrn0NFUiQzJCiZ65uIay_S?hl=fr#scrollTo=CJAQGVAWNNPw


# Configuration du logger pour le débogage
logging.basicConfig(level=logging.DEBUG)
# Configuration de la clé secrète pour les sessions Flask

# Routes API pour récupérer les données
@app.route('/api/population', methods=['GET'])
def get_population():
    data = ml.Population.query.all()
    return jsonify([{'year': item.year, 'population': item.population} for item in data])

@app.route('/api/school_enrollment', methods=['GET'])
def get_school_enrollment():
    data = ml.SchoolEnrollment.query.all()
    return jsonify([{'year': item.year, 'enrollment_rate': item.enrollment_rate} for item in data])

@app.route('/api/age_distribution', methods=['GET'])
def get_age_distribution():
    data = ml.AgeDistribution.query.filter_by(year=2023).all()  # Filtrer par année si besoin
    return jsonify([{'age_group': item.age_group, 'population': item.population} for item in data])

def days_in_year(year):
    # Retourne 366 si bissextile, 365 sinon
    return 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365

def minutes_in_year(year):
    # Calcule le nombre total de minutes dans une année
    return days_in_year(year) * 24 * 60

def naissance_deces_pop():
    # Données démographiques prédéfinies
    data_nais_deces_pop = {
        "population": [777556, 797114, 793064, 787604, 804768, 796472],
        "population_add": [31719274, 32496830, 33293944, 34087008, 34874612, 35679380],
        "naissance": [1025716, 1047630, 1045355, 1041416, 1061168, 1054794],
        "deces": [248159, 250517, 252290, 253814, 256397, 258324],
        "year": [2025 + i for i in range(6)]  # 2025 à 2030
    }

    # Année actuelle
    current_year = datetime.now().year

    # Vérifier si l'année est dans les données
    if current_year not in data_nais_deces_pop["year"]:
        return f"Données non disponibles pour l'année {current_year}"

    # Index de l'année actuelle
    index = data_nais_deces_pop["year"].index(current_year)

    # Dates de référence et actuelle
    date_ref = datetime(current_year, 1, 1)  # Début de l'année
    date_actu = datetime.now()

    # Nombre de jours écoulés
    elapsed_days = (date_actu - date_ref).days

    # Nombre de minutes écoulées
    elapsed_minutes = (date_actu - date_ref).total_seconds() / 60

    # Données annuelles
    naissance_annuelle = data_nais_deces_pop["naissance"][index]
    deces_annuel = data_nais_deces_pop["deces"][index]
    population_annuelle = data_nais_deces_pop["population"][index]
    population_base = data_nais_deces_pop["population_add"][index]

    # Calculs
    days = days_in_year(current_year)
    minutes = minutes_in_year(current_year)

    # Naissances et décès cumulés jusqu'à maintenant
    naissance_cumulee = int(naissance_annuelle / days) * elapsed_days
    deces_cumule = int(deces_annuel / days) * elapsed_days
    pop_actuelle = population_base + int(population_annuelle / minutes * elapsed_minutes)

    return naissance_cumulee, deces_cumule, pop_actuelle

@app.route('/population_data')
def population_data():
    result = naissance_deces_pop()
    now = datetime.now()

    if isinstance(result, dict) and "error" in result:  # Gestion d'erreur
        return jsonify(result)

    naissances, deces, population = result
    data = {
        "time": now.timestamp(),  # Timestamp pour la date
        "population_actuelle": population,  # Population actuelle
        "naissances_cumulees": naissances,  # Optionnel
        "deces_cumules": deces  # Optionnel
    }
    return jsonify(data)



  
@app.route('/')
def list_regions():
    regions =  qr.options_regions() # or qr.options_regions()
    naissance, deces, pop_minute = naissance_deces_pop()
    
    # We no longer pass graph data to the template. It's fetched via API.
    return render_template('home.html',
                           naissance=naissance,
                           deces=deces,
                           pop_minute=pop_minute,
                           regions=regions)


#Bloc du dashbord------------------------------------------Pour le tableau de bord par région





# Générer les données pour toutes les régions restantes
data = {region: qr.generate_region_data() for region in  qr.options_regions()}
regions = list(data.keys())  

@app.route('/region_vitrine/<region>')  
def region_vitrine(region):  
    if region not in regions:  
        return "Region not found", 404  # Handle invalid region  
    region_data = data[region]
    global region_publication
    region_publication=region
    return render_template('region_vitrine.html',  
                           indicateurs=region_data['indicateurs'],  
                           region_name=region_publication,  
                           all_regions=regions) 

#--------------------------------------------------Fin du tableau de bord
publications_data = conf_pub.load_publications_from_db()
@app.route('/publications')
def publications_region():
    try:
        # Charger les publications (filtrées par region_publication si définie)
        publications_data = conf_pub.load_publications_from_db(region=region_publication)
        publications = list(publications_data.values())

        # Limiter la description à 100 caractères si nécessaire
        for pub in publications:
            if pub['description'] and len(pub['description']) > 100:
                pub['description'] = pub['description'][:100] + "..."

        # Charger les régions pour le menu de sélection
        regions = conf_pub.get_regions()

        # Nom de la région à afficher
        region_name = region_publication if region_publication else "Toutes les régions"

        return render_template('publications.html', publications=publications, region_name=region_name, regions=regions)
    except Exception as e:
        print(f"[ERROR] Erreur dans la route /publications : {e}")
        return "Erreur lors du chargement des publications", 500

@app.route('/publications/<title>')
def publication_detail(title):
    normalized_title = title.lower().replace('_', ' ')
    publication = None
    for pub_title, data in publications_data.items():
        normalized_pub_title = pub_title.replace('_', ' ').lower()
        if normalized_pub_title == normalized_title:
            publication = data
            break

    if not publication:
        abort(404, description=f"Publication '{normalized_title}' non trouvée")

    publication_number = f"P{list(publications_data.keys()).index(pub_title) + 1:03d}"
    return render_template('publications_detail.html',
                           publication_title=publication['title'],
                           publication_description=publication['description'],
                           publication_date=publication['date'],
                           publication_number=publication_number,
                           region_name=region_publication)








""" 
Cette fonction permet d'acceder a la page de requête
search_indicators2=Page d'acces global
search_indicatorsR=Page d'acces spécifique à une region
"""
# Routes d'accès par requete cocher et le plus simple
@app.route('/search_indicators')
def search_indicators():
    indicateurs = qr.options_indicateur()  # Fonction qui récupère les indicateurs
    return render_template('search_indicateur.html',indicateurs=indicateurs)

# Route pour afficher en fonction de la région
@app.route('/search_indicatorsR')
def search_indicatorsR():
    indicateurs = qr.options_indicateur()  # Fonction qui récupère les indicateurs
    return render_template('search_indicateurR.html',indicateurs=indicateurs)


from flask import jsonify, request

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '').strip().lower()
    if not query:
        return jsonify([])
    # Charger les données depuis MySQL
    df = qr.autocompletion()
    # Convertir en minuscule pour une recherche insensible à la casse
    df['nom_indicateur'] = df['nom_indicateur'].astype(str).str.strip().str.lower()
    # Filtrer les indicateurs qui contiennent le texte saisi
    suggestions = df[df['nom_indicateur'].str.contains(query, na=False)]['nom_indicateur'].unique().tolist()
    return jsonify(suggestions)






@app.route('/filter_indicator/<path:indicateur>')
def page_filtration_data(indicateur):
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 50))
    indicateur_SELECT = urllib.parse.unquote(indicateur)

    definitions = None
    mode_calcul = None

    # Récupérer les données depuis la base de données
    df = qr.obtention_data_mysql_niveauDesagr(indicateur_name=indicateur_SELECT, offset=offset, limit=limit)
    print(df.head())
    
    df_filtered = df.copy() 
    
    if indicateur_SELECT and 'Indicateurs' in df_filtered.columns:
        df_filtered_temp = df_filtered.copy()
        df_filtered_temp['Indicateurs_cleaned'] = df_filtered_temp['Indicateurs'].astype(str).str.strip().str.lower()
        df_filtered = df_filtered_temp[df_filtered_temp['Indicateurs_cleaned'] == indicateur_SELECT.strip().lower()].copy()
        if 'Indicateurs_cleaned' in df_filtered.columns:
            df_filtered = df_filtered.drop(columns=['Indicateurs_cleaned'])

        definitions = qr.definition_indicateur(indicateur_SELECT)
        mode_calcul = qr.mode_calcul_indicateur(indicateur_SELECT)
    
    df_filtered = df_filtered.dropna(axis=1, how='all').fillna('-').copy()
    
    df_final_rows = []
    
    for _, row in df_filtered.iterrows():
        dimension_cols = [col.strip() for col in row['Dimension'].split('/')]
        category_values = [value.strip() for value in row['Modalites'].split('/')]
        
        dimension_dict = dict(zip(dimension_cols, category_values))
        
        temp_row_dict = {
            'Indicateurs': row['Indicateurs'],
            'Valeur': row['Valeur'],
            'Annee': row['Annee']
        }
        temp_row_dict.update(dimension_dict)

        cle_pivot_table_parts = dimension_cols + ['Annee']
        temp_row_dict['cle_pivot_table'] = ",".join(cle_pivot_table_parts)
        
        df_final_rows.append(temp_row_dict)
    
    df_final = pd.DataFrame(df_final_rows)
   
    df_filtered = df_final.dropna(axis=1, how='all').copy()

    if 'Annee' in df_filtered.columns:
        df_filtered['Annee'] = pd.to_numeric(df_filtered['Annee'], errors='coerce').astype('Int64')
    if 'Valeur' in df_filtered.columns:
        df_filtered['Valeur'] = pd.to_numeric(df_filtered['Valeur'], errors='coerce')

    if df_filtered.empty:
        return render_template('no_data.html')
    
    if request.args.get('format') == 'json':
        df_json_ready = df_filtered.copy()
        for col in ['Annee', 'Valeur']:
            if col in df_json_ready.columns:
                df_json_ready[col] = df_json_ready[col].apply(lambda x: int(x) if pd.notna(x) and col == 'Annee' else (float(x) if pd.notna(x) else None))
        
        return jsonify({
            'data': df_json_ready.to_dict(orient='records'),
            'definitions': definitions,
            'mode_calcul': mode_calcul
        })
    
    print('Les colonnes dans le dataframe:',df_filtered.columns)
    print('Notre indicateur:',indicateur_SELECT)
    existing_columns = df_filtered.columns.tolist()
    columns_to_exclude = ['Valeur', 'Indicateurs', 'cle_pivot_table']
    desaggregation_columns = [col for col in existing_columns if col not in columns_to_exclude]
    print('liste des colonnes:',desaggregation_columns)
    
    return render_template(
        'result.html',
        definitions=definitions,
        mode_calcul=mode_calcul,
        colonne_valable=desaggregation_columns,
        indicateur2=indicateur_SELECT
    )

# Accès spécefique à une région
@app.route('/search_indicatorsR/<path:indicateur>') 
def request_indicateurR(indicateur):
    # Charger les données depuis MySQL
    
    df= qr.get_data_from_mysql_VR(region_publication)
    indicateur_SELECT = urllib.parse.unquote(indicateur)
    definitions=None
    # Obtenir les options pour chaque filtre (indicateur, région, etc.
    df_filtered = pd.DataFrame()
    df_filtered =df
    # Appliquer le filtre si 'indicateur' existe et que la sélection d'indicateur est présente
    if indicateur_SELECT and 'Indicateurs' in df_filtered.columns:
        # Convertir la colonne 'indicateur' en chaînes de caractères
        df_filtered['Indicateurs'] = df_filtered['Indicateurs'].astype(str).str.strip().str.lower()
        definitions=qr.definition_indicateur(indicateur_SELECT)
        mode_calcul=qr.mode_calcul_indicateur(indicateur_SELECT)
        
        # Appliquer le filtre sur la colonne 'indicateur'
        df_filtered = df_filtered[df_filtered['Indicateurs'] == indicateur_SELECT.strip().lower()]
    else:
        print("Aucun filtre appliqué sur l'indicateur")
    # Supprimer les colonnes contenant uniquement des NaN
    df_filtered = df_filtered.dropna(axis=1, how='all')
    df_filtered = df_filtered.fillna('-')
    df_final = pd.DataFrame()
    for _, row in df_filtered.iterrows():
            dimension_cols = row['Dimension'].split('/')
            category_values = row['Modalites'].split('/')
            dimension_cols = [col.strip() for col in dimension_cols]
            category_values = [value.strip() for value in category_values]
            dimension_dict = dict(zip(dimension_cols, category_values))
            temp_row = pd.Series(dimension_dict)
            temp_row['Indicateurs'] = row['Indicateurs']
            temp_row["Valeur"] = row["Valeur"]
            temp_row["Annee"] = row["Annee"]
            cle_pivot_table = ",".join(dimension_cols) + ",Annee"
            temp_row["cle_pivot_table"] = cle_pivot_table
            # Ajouter cette ligne nettoyée au DataFrame final
            df_final = pd.concat([df_final, temp_row.to_frame().T], ignore_index=True)
            
    df_filtered = df_final.dropna(axis=1, how='all')
    if df_filtered.empty:
            return render_template('no_data.html')  # Rediriger vers la page 'Aucune donnée disponible'
    # Stocker le DataFrame filtré dans la session pour une utilisation ultérieure
    df_filtered_json = df_filtered.to_json(orient='split')  # Convertir en JSON pour le stockage
    session['df_filtered'] = df_filtered_json
    # Obtenir les colonnes valables pour les désagrégations
    existing_columns = df_filtered.columns.tolist()
    columns_to_exclude = ['Valeur', 'Indicateurs','cle_pivot_table']
    desaggregation_columns = [col for col in existing_columns if col not in columns_to_exclude]
    return render_template(
        'result.html',
        definitions=definitions,
        mode_calcul=mode_calcul,
        colonne_valable=desaggregation_columns,  # Colonnes à utiliser pour désagréger les données
        indicateur2=indicateur_SELECT,  # Indicateur sélectionné
        df_filtered=df_filtered_json  # Data JSON pour le filtrage
    )

#----------------Autocomplétion



    
@app.route('/process_columns', methods=['POST'])
def process_columns():
    data_request = request.get_json()
    row_columns = data_request.get('row_columns', [])
    col_columns = data_request.get('col_columns', [])
    value_column = data_request.get('value_column', 'Valeur')
    indicateur_name = data_request.get('indicateur_name') # Nouveau : Récupérer l'indicateur depuis le front-end
    my_index_selection = [row_columns, col_columns]

    if not indicateur_name:
        return jsonify({"error": "Nom de l'indicateur manquant dans la requête"}), 400

    # Étape 1 : Récupérer les données brutes directement depuis la base de données
    df = qr.obtention_data_mysql_requete(indicateur_name=indicateur_name)
    
    if df.empty:
        return jsonify({"error": f"Aucune donnée trouvée pour l'indicateur '{indicateur_name}'"}), 400

    # Étape 2 : Appliquer les mêmes transformations que dans request_indicateur2
    df_filtered = df.copy() 
    df_final_rows = []
    
    for _, row in df_filtered.iterrows():
        if pd.notna(row.get('Dimension')) and pd.notna(row.get('Modalites')):
            dimension_cols = [col.strip() for col in row['Dimension'].split('/')]
            category_values = [value.strip() for value in row['Modalites'].split('/')]
            
            dimension_dict = dict(zip(dimension_cols, category_values))
            
            temp_row_dict = {
                'Indicateurs': row.get('Indicateurs'),
                'Valeur': row.get('Valeur'),
                'Annee': row.get('Annee')
            }
            temp_row_dict.update(dimension_dict)

            cle_pivot_table_parts = dimension_cols + ['Annee']
            temp_row_dict['cle_pivot_table'] = ",".join(cle_pivot_table_parts)
            
            df_final_rows.append(temp_row_dict)
    
    df_final = pd.DataFrame(df_final_rows)
    
    df_filtered = df_final.dropna(axis=1, how='all').copy()
    print('data issue V2 , prête analysée',df_final.columns)
    # Nettoyage et conversion des types comme précédemment
    if value_column in df_filtered.columns:
        df_filtered[value_column] = df_filtered[value_column].astype(str).str.replace(' ', '').str.replace(',', '.')
        df_filtered[value_column] = pd.to_numeric(df_filtered[value_column], errors='coerce')
        df_filtered = df_filtered.dropna(subset=[value_column])
    
    if 'Annee' in df_filtered.columns:
        df_filtered['Annee'] = df_filtered['Annee'].astype(str).str.replace(' ', '').str.replace(',', '.')
        df_filtered['Annee'] = pd.to_numeric(df_filtered['Annee'], errors='coerce').astype('Int64')

    try:
        my_index_flat = list(chain.from_iterable(my_index_selection))
        my_index_set = set(my_index_flat)

        data = df_filtered[df_filtered['cle_pivot_table'].apply(lambda x: set(x.split(',')) == my_index_set)].copy()
        
        print('Les colonnes des données extraire:',data.columns)
        
        print('Afficher',data.head())
        pivot_table = pd.pivot_table(
            data,
            index=row_columns,
            columns=col_columns,
            values=value_column,
            aggfunc='first'
        )
        
        pivot_table.reset_index(inplace=True)
        
        processed_columns = []
        for col in pivot_table.columns:
            if isinstance(col, tuple):
                processed_columns.append([str(item) for item in col])
            else:
                processed_columns.append([str(col)])

        result_data = {
            "columns": processed_columns,
            "index": list(pivot_table.index),
            "data": pivot_table.values.tolist()
        }
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la création du tableau croisé dynamique : {e}"}), 400

    return jsonify(result_data)




#Pour la liste des indicateur dans template domaine-sous-domaine-indicateur, pour la domaine indicateur
@app.route('/get_data2')
def get_data2():
    # Charger le fichier Excel
    df = pd.read_excel('search_indicateur.xlsx')
    # Grouper les données par Domaine et Thématique
    data = df.groupby(['Domaine', 'Thematique'])['Indicateurs'].apply(list).to_dict()
    data_str_keys = {f"{key[0]}, {key[1]}": value for key, value in data.items()}

    # Retourner les données en JSON
    return jsonify(data_str_keys)




#-------------------------------------------------FIN API

if __name__ == '__main__':
    app.run(debug=True)
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
import import_publications as conf_pub
from itertools import chain
import my_queries as qr
import config as cf
from config import app, db 
import io
global region_publication
region_publication="PORO"# Cette variable va nous permettre 
#https://colab.research.google.com/drive/1oBqwcSMb4YTrn0NFUiQzJCiZ65uIay_S?hl=fr#scrollTo=CJAQGVAWNNPw
#brew services restart elastic/tap/elasticsearch-full
#redis-server

# Configuration du logger pour le débogage
logging.basicConfig(level=logging.DEBUG)
# Configuration de la clé secrète pour les sessions Flask


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
    regions = qr.options_regions()
    naissance,deces,pop_minute=naissance_deces_pop()
    # Données
    years = [2019, 2020, 2021, 2022, 2023]
    population = [24.0, 27.0, 27.4, 29.8, 30.38]
    school_enrollment_rate = [75, 76, 78, 79, 80]
    age_groups = ['0-14 ans', '15-24 ans', '25-54 ans', '55 - 59 ans','60 -64 ','65-69','70-74 ans']
    age_distribution = [40, 20, 30, 10, 18, 20]
    liste_region=regions
    return render_template('home.html',
                        naissance=naissance,
                        deces=deces,
                        pop_minute=pop_minute,
                        years=years,
                        population=population,
                        school_enrollment_rate=school_enrollment_rate,
                        age_groups=age_groups,
                        age_distribution=age_distribution,
                        regions=regions,
    )




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




@app.route('/search_indicators2/<path:indicateur>') 
def request_indicateur2(indicateur):
    # Charger les données depuis MySQL
    df= qr.get_data_from_mysql_V1()
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
            dimension_cols = row['Dimension'].split(',')
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
            dimension_cols = row['Dimension'].split(',')
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
from flask import jsonify, request

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '').strip().lower()
    if not query:
        return jsonify([])
    # Charger les données depuis MySQL
    df = qr.get_data_from_mysql_V1()
    # Vérifier que la colonne 'Indicateurs' existe
    if 'Indicateurs' not in df.columns:
        return jsonify([])
    # Convertir en minuscule pour une recherche insensible à la casse
    df['Indicateurs'] = df['Indicateurs'].astype(str).str.strip().str.lower()
    # Filtrer les indicateurs qui contiennent le texte saisi
    suggestions = df[df['Indicateurs'].str.contains(query, na=False)]['Indicateurs'].unique().tolist()
    return jsonify(suggestions)








"""
Cette fonction a pour rôle de permet le charger des données des requêtes
Aussi cette partie est dedié dans les requêtes utilisatrices.
Toutes les fonctions pour la requêtes sont écrites ici.
"""



@app.route('/request_indicateur', methods=['GET', 'POST'])
def request_indicateur():
    # Charger les données depuis MySQL
    data_mysql = qr.get_data_from_mysql_V1()
    # Obtenir les options pour chaque filtre (indicateur, région, etc.)
    indicateurs_options = qr.options_indicateur()
    indicateur_SELECT = None
    df_filtered = pd.DataFrame()
    definitions = None
    mode_calcul = None
    if request.method == 'GET':
        indicateur_SELECT = request.args.get('indicateur_elastic')
        df_filtered = data_mysql
        print('indicateur pris:',indicateur_SELECT)
        
        if indicateur_SELECT and 'Indicateurs' in df_filtered.columns:
            try:
                definitions = qr.definition_indicateur(indicateur_SELECT)
                mode_calcul = qr.mode_calcul_indicateur(indicateur_SELECT)
                
                df_filtered['Indicateurs'] = df_filtered['Indicateurs'].astype(str).str.strip().str.lower()
                df_filtered = df_filtered[df_filtered['Indicateurs'] == indicateur_SELECT.strip().lower()]
                
                if df_filtered.empty:
                    return render_template('no_data.html')  # Rediriger vers la page 'Aucune donnée disponible'
                    
            except Exception as e:
                print(f"Erreur lors de la récupération de l'indicateur: {e}")
                definitions = "Indicateur non disponible"
                mode_calcul = "Non défini"
        
        df_final = pd.DataFrame()
        df_filtered = df_filtered.fillna('-')
        for _, row in df_filtered.iterrows():
            dimension_cols = row['Dimension'].split(',')
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
            df_final = pd.concat([df_final, temp_row.to_frame().T], ignore_index=True)
        
        df_filtered = df_final.dropna(axis=1, how='all')
        
        if df_filtered.empty:
            return render_template('no_data.html')  # Rediriger vers la page 'Aucune donnée disponible'
        
        df_filtered_json = df_filtered.to_json(orient='split')
        session['df_filtered'] = df_filtered_json
        existing_columns = df_filtered.columns.tolist()
        columns_to_exclude = ['Valeur', 'Indicateurs','cle_pivot_table']
        desaggregation_columns = [col for col in existing_columns if col not in columns_to_exclude]
    
    return render_template(
        'result.html',
        definitions=definitions,
        mode_calcul=mode_calcul,
        colonne_valable=desaggregation_columns,
        indicateurs=indicateurs_options,
        indicateur2=indicateur_SELECT,
        df_filtered=df_filtered_json
    )

#
    
@app.route('/process_columns', methods=['POST'])
def process_columns():
    # Récupérer les colonnes envoyées par la requête AJAX
    data = request.get_json()
    row_columns = data.get('row_columns', [])
    col_columns = data.get('col_columns', [])
    value_column = data.get('value_column', 'Valeur')
    my_index=[row_columns,col_columns]
    #print("Les choix utilisateurs",my_index)
    # Charger les données réelles depuis la session ou depuis MySQL si nécessaire
    df_filtered_json = session.get('df_filtered', None)
    if df_filtered_json:
        df_filtered = pd.read_json(io.StringIO(df_filtered_json), orient='split')
    else:
        return jsonify({"error": "Aucune donnée disponible dans la session"}), 400
    # Vérification et conversion de la colonne 'valeur' en numérique
    if value_column in df_filtered.columns:
        try:
            df_filtered[value_column] = pd.to_numeric(df_filtered[value_column], errors='coerce')
            df_filtered = df_filtered.dropna(subset=[value_column])
        except Exception as e:
            return jsonify({"error": f"La colonne '{value_column}' contient des données non numériques : {e}"}), 400
    try:

        my_index= list(chain.from_iterable(my_index))
        data_V1=my_index
        #Ordonnée la data
        df_filtered['cle_pivot_table'] = sorted(df_filtered['cle_pivot_table'])
        # Convertir my_index en un ensemble pour faciliter la comparaison
        my_index_set = set(my_index)

        # Filtrer les lignes de df_filtered où cle_pivot_table contient les mêmes éléments que my_index
        data = df_filtered[df_filtered['cle_pivot_table'].apply(lambda x: set(x.split(',')) == my_index_set)]
        data['Annee'] = df_filtered['Annee'].astype(str)

        # Afficher le DataFrame filtré pour vérification
        pivot_table = pd.pivot_table(
            data,
            index=row_columns,
            columns=col_columns,
            values=value_column,
            aggfunc='sum',
            fill_value=0
        )
        pivot_table = pivot_table 
        # Réinitialiser l'index pour convertir les données en format JSON structuré
        pivot_table.reset_index(inplace=True)
        result_data = {
            "columns": [list(map(str, col)) if isinstance(col, tuple) else [str(col)] for col in pivot_table.columns],
            "index": list(pivot_table.index),
            "data": pivot_table.values.tolist()
        }
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la création du tableau croisé dynamique : {e}"}), 400

    return jsonify(result_data)


@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        # Charger les données filtrées depuis la session
        df_filtered_json = session.get('df_filtered', None)
        if df_filtered_json is None:
            return jsonify({"error": "Aucune donnée filtrée disponible."}), 404
        # Convertir le JSON en DataFrame et ensuite en dictionnaire
        df_filtered = pd.read_json(df_filtered_json, orient='split')
        data = df_filtered.to_dict(orient='records')
        # Affichage pour vérifier le contenu
        return jsonify(data)
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        return jsonify({"error": "Une erreur est survenue lors du chargement des données."}), 500



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


# Generateur de données excel
@app.route('/generateur')
def generateur():
    return render_template('generateur_excel.html')

#-------------------------------------------------FIN API

if __name__ == '__main__':
    app.run(debug=True)
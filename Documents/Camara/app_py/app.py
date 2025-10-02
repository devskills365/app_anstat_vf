from flask import  render_template, request, session, jsonify,abort
import os
import pop_naissance
import logging
import pandas as pd
import urllib
from sqlalchemy import func

from datetime import datetime
import sys
from itertools import chain
import my_queries as qr
import models as ml
from config import app, db 
import description_region as dr
current_dir = os.path.dirname(os.path.abspath(__file__))
config_pub_path = os.path.join(current_dir, 'config_pub')
sys.path.append(config_pub_path)
import publication as conf_pub
from models import (  # Import models from the corrected models.py
    IndicateursDashbordNational,
    IndicateursDashbordRegion,
    RatiosEleveEnseignant,
    TauxNatalite,
    PopulationRegionale,
    PersonnelMedical,
    TauxAlphabetisation,
    TauxBruteScolarite,
    TauxElectrification,
     DescriptionRegion,
     SearchIndicateur
)

global region_publication
region_publication="PORO"# Cette variable va nous permettre 
#https://colab.research.google.com/drive/1oBqwcSMb4YTrn0NFUiQzJCiZ65uIay_S?hl=fr#scrollTo=CJAQGVAWNNPw
# Pour transformer les données des indicateurs nationaux (fichier du directeur)
#https://colab.research.google.com/drive/1JUqEvhPJQErgB1DPo87JzXu1FlpqTZm8
# Pour inserer les données dans json
#https://colab.research.google.com/drive/1W-OEye7rhuI4s_hJUOESPJfeJIKbPY-h

# Configuration du logger pour le débogage
logging.basicConfig(level=logging.DEBUG)


#_________________________________________________________________Fin région, seulement les departement
# Routes API pour récupérer les données
@app.route('/api/population', methods=['GET'])
def get_population():
    data = ml.Population.query.all()
    return jsonify([{'year': item.year, 'population': item.population} for item in data])

@app.route('/population_data')
def population_data():
    result = pop_naissance.naissance_deces_pop()
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



 # Page principale (home page) 
@app.route('/')
def list_regions():
    regions =  qr.options_regions() # or qr.options_regions()
    naissance, deces, pop_minute = pop_naissance.naissance_deces_pop()
    
    # We no longer pass graph data to the template. It's fetched via API.
    return render_template('home.html',
                           naissance=naissance,
                           deces=deces,
                           pop_minute=pop_minute,
                           regions=regions)

#------------------pour la page home , les indicateurs clés
## Indicateurs nationaux________________________________________Nationaux

@app.route('/api/data/ihpc')
def get_ihpc():
    # Exécution de la requête SQLAlchemy
    data = db.session.query(
        IndicateursDashbordNational.Annee,
        func.round(IndicateursDashbordNational.Valeur, 2).label('Valeur')
    ).filter(
        IndicateursDashbordNational.Indicateur == 'Inflation annuelle moyenne (IHPC – ANStat)'
    ).order_by(
        IndicateursDashbordNational.Annee
    ).all()
    
    # Transformation des résultats SQLAlchemy en dictionnaire
    formatted_data = [{'Annee': row.Annee, 'Valeur': float(row.Valeur) if row.Valeur is not None else None} for row in data]
    
    # Renvoyer directement la réponse JSON
    return jsonify(formatted_data)


@app.route('/api/data/ipc')
def get_ipc():
    data = db.session.query(
        IndicateursDashbordNational.Annee,
        func.round(IndicateursDashbordNational.Valeur, 2).label('Valeur')
    ).filter(
        IndicateursDashbordNational.Indicateur == 'Indice de Perception de la Corruption (IPC)'
    ).order_by(
        IndicateursDashbordNational.Annee
    ).all()
    
    # Correctly format the data for JSON output
    formatted_data = [{'Annee': row.Annee, 'Valeur': float(row.Valeur) if row.Valeur is not None else None} for row in data]
    return jsonify(formatted_data)



@app.route('/api/data/sante-budget')
def get_sante_budget():
    data = db.session.query(
        IndicateursDashbordNational.Annee,
        func.round(IndicateursDashbordNational.Valeur, 2).label('Valeur')
    ).filter(
        IndicateursDashbordNational.Indicateur == 'Dépenses publiques consacrées à la santé en pourcentage du budget'
    ).order_by(
        IndicateursDashbordNational.Annee
    ).all()
    
    # Correctly format the data for JSON output
    formatted_data = [{'Annee': row.Annee, 'Valeur': float(row.Valeur) if row.Valeur is not None else None} for row in data]
    return jsonify(formatted_data)


#Bloc du dashbord------------------------------------------Pour le tableau de bord par région


@app.route('/region_vitrine/<region>')
def region_vitrine(region):
    # Récupérer la description depuis la base
    session['region_data'] = region
    try:
        descr_region = db.session.query(DescriptionRegion).filter(
            DescriptionRegion.Nom == region
        ).first()

        if descr_region:
            description_text = descr_region.Description
        else:
            description_text = "Description non disponible."

    except Exception as e:
        print(f"Erreur lors de la récupération de la description de la région : {e}")
        description_text = "Erreur lors de la récupération de la description."

    return render_template(
        'region_vitrine.html',
        region_name=region,
        description=description_text
    )


@app.route('/api/data/ppcs')
def get_ppcs():
    region = session.get('region_data')
    if not region:
        return jsonify({'error': 'Aucune région sélectionnée'}), 400
    data = IndicateursDashbordRegion.query.filter(
        IndicateursDashbordRegion.Region == region,
        IndicateursDashbordRegion.Indicateur == 'Proportion de la population vivant à moins de 5 Km d’un centre de santé'
    ).order_by(
        IndicateursDashbordRegion.Annee
    ).all()
    
    # Correctly format the decimal value
    formatted_data = [{'Annee': row.Annee, 'Valeur': float(row.Valeur) if row.Valeur is not None else None} for row in data]
    return jsonify(formatted_data)


@app.route('/api/data/nbre-lit-hbts')
def get_nbre_lit_1000_hbts():
    region = session.get('region_data')
    if not region:
        return jsonify({'error': 'Aucune région sélectionnée'}), 400
    data = IndicateursDashbordRegion.query.filter(
        IndicateursDashbordRegion.Region == region,
        IndicateursDashbordRegion.Indicateur == 'Nombre de lits pour 1000 Habitants'
    ).order_by(
        IndicateursDashbordRegion.Annee
    ).all()
    
    # Correctly format the decimal value
    formatted_data = [{'Annee': row.Annee, 'Valeur': float(row.Valeur) if row.Valeur is not None else None} for row in data]
    return jsonify(formatted_data)


@app.route('/api/data/taux-alphabetisation')
def get_taux_alphabetisation():
    region = session.get('region_data')
    if not region:
        return jsonify({'error': 'Aucune région sélectionnée'}), 400
    
    data = TauxAlphabetisation.query.filter_by(
        region=region
    ).order_by(
        TauxAlphabetisation.year
    ).all()
    
    # Correctly format the decimal value
    formatted_data = [{'year': row.year, 'taux': float(row.taux) if row.taux is not None else None} for row in data]
    return jsonify(formatted_data)

@app.route('/api/data/taux-brute-scolarite')
def get_taux_brute_scolarite():
    region = session.get('region_data')
    if not region:
        return jsonify({'error': 'Aucune région sélectionnée'}), 400
    
    data = IndicateursDashbordRegion.query.filter(
        IndicateursDashbordRegion.Region == region,
        IndicateursDashbordRegion.Indicateur == 'Ratio élève/salle de classe au primaire'
    ).order_by(
        IndicateursDashbordRegion.Annee
    ).all()
    
    # Correctly format the decimal value
    formatted_data = [{'Annee': row.Annee, 'Valeur': float(row.Valeur) if row.Valeur is not None else None} for row in data]
    return jsonify(formatted_data)


# Couverture de téléphonie mobile 
@app.route('/api/data/taux-couverture-telephone')
def get_taux_electrification():
    region = session.get('region_data')
    if not region:
        return jsonify({'error': 'Aucune région sélectionnée'}), 400
    print("Couverture region:",region)
    data = IndicateursDashbordRegion.query.filter(
        IndicateursDashbordRegion.Region == region,
        IndicateursDashbordRegion.Indicateur == 'Couverture de téléphonie mobile '
    ).order_by(
        IndicateursDashbordRegion.Annee
    ).all()
    
    # Correctly format the decimal value
    formatted_data = [{'Annee': row.Annee, 'Valeur': float(row.Valeur) if row.Valeur is not None else None} for row in data]
    return jsonify(formatted_data)






publications_data = conf_pub.load_publications_from_db()
@app.route('/publications')
def publications_region():
    try:
        # Charger les publications (filtrées par region_publication si définie)
        publications_data = conf_pub.load_publications_from_db()
        publications = list(publications_data.values())

        # Limiter la description à 100 caractères si nécessaire
        for pub in publications:
            if pub['description'] and len(pub['description']) > 100:
                pub['description'] = pub['description'][:100] + "..."

        # Charger les régions pour le menu de sélection
        regions = conf_pub.get_regions()

        # Nom de la région à afficher
        region_name = region_publication if region_publication else "Toutes les régions"

        return render_template('publications.html', publications=publications)
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




@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '').strip().lower()
    if not query:
        return jsonify([])
    # Charger les données depuis MySQL
    df = qr.autocompletion()
    # Convertir en minuscule pour une recherche insensible à la casse
    df['Indicateurs'] = df['Indicateurs'].astype(str).str.strip().str.lower()
    # Filtrer les indicateurs qui contiennent le texte saisi
    suggestions = df[df['Indicateurs'].str.contains(query, na=False)]['Indicateurs'].unique().tolist()
    return jsonify(suggestions)



@app.route('/filter_indicator/<path:indicateur>')
def page_filtration_data(indicateur):
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 50))
    indicateur_SELECT = urllib.parse.unquote(indicateur)

    definitions = None
    mode_calcul = None

    # Récupérer les données depuis la base de données
    df = qr.obtention_data_mysql_requete(indicateur_name=indicateur_SELECT, offset=offset, limit=limit)
    print("DataFrame original reçu :")
    print(df.head())
    
    # Filtrer par l'indicateur sélectionné
    if not df.empty and 'Indicateurs' in df.columns:
        df_filtered = df[df['Indicateurs'].astype(str).str.strip().str.lower() == indicateur_SELECT.strip().lower()].copy()
        
        definitions = qr.definition_indicateur(indicateur_SELECT)
        mode_calcul = qr.mode_calcul_indicateur(indicateur_SELECT)
    else:
        return render_template('no_data.html')
    
    # Créer dynamiquement les colonnes de désagrégation
    for index, row in df_filtered.iterrows():
        try:
            dimension_cols = [col.strip() for col in row['Dimension'].split('/')]
            category_values = [value.strip() for value in row['Modalites'].split('/')]
            
            dimension_dict = dict(zip(dimension_cols, category_values))
            
            for key, value in dimension_dict.items():
                if key not in df_filtered.columns:
                    df_filtered[key] = None
                df_filtered.at[index, key] = value
        except Exception as e:
            # Gérer les erreurs de format de données
            print(f"Erreur de traitement des données à la ligne {index}: {e}")
            
    # Créer la colonne 'cle_pivot_table'
    existing_cols_for_pivot = [col for col in df_filtered.columns if col not in ['Indicateurs', 'Valeur', 'Annee', 'Dimension', 'Modalites']]
    df_filtered['cle_pivot_table'] = df_filtered[existing_cols_for_pivot].apply(
        lambda x: ','.join(x.dropna().astype(str)), axis=1
    )
    
    # Convertir les colonnes en types numériques
    if 'Annee' in df_filtered.columns:
        df_filtered['Annee'] = pd.to_numeric(df_filtered['Annee'], errors='coerce').astype('Int64')
    if 'Valeur' in df_filtered.columns:
        df_filtered['Valeur'] = pd.to_numeric(df_filtered['Valeur'], errors='coerce')
    
    df_filtered = df_filtered.dropna(axis=1, how='all').fillna('-').copy()

    # Le reste de votre code pour la réponse HTML ou JSON
    if df_filtered.empty:
        return render_template('no_data.html')
    
    if request.args.get('format') == 'json':
        df_json_ready = df_filtered.copy()
        for col in ['Annee', 'Valeur']:
            if col in df_json_ready.columns:
                df_json_ready[col] = df_json_ready[col].apply(
                    lambda x: int(x) if pd.notna(x) and col == 'Annee' else (float(x) if pd.notna(x) else None)
                )
        return jsonify({
            'data': df_json_ready.to_dict(orient='records'),
            'definitions': definitions,
            'mode_calcul': mode_calcul
        })
    
    # Préparer les colonnes pour l'affichage dans le template
    existing_columns = df_filtered.columns.tolist()
    columns_to_exclude = ['Valeur', 'Indicateurs', 'cle_pivot_table', 'Dimension', 'Modalites','id']
    desaggregation_columns = [col for col in existing_columns if col not in columns_to_exclude]
    
    print('Les colonnes dans le dataframe final:', df_filtered.columns)
    print('Notre indicateur:', indicateur_SELECT)
    print('Liste des colonnes de désagrégation:', desaggregation_columns)
    
    return render_template(
        'result.html',
        definitions=definitions,
        mode_calcul=mode_calcul,
        colonne_valable=desaggregation_columns,
        indicateur2=indicateur_SELECT
    )
# Accès spécefique à une région

#/filter_indicator/<path:indicateur>


#__________________________
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
    
    
    df_final = pd.DataFrame(df_filtered)
 
    print('data issue V2 , prête analysée',df_final.shape)
    df_filtered = df_final.dropna(axis=1, how='all').copy()
 
    
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
        
        print('Les colonnes des données extraire:',data.head())
        #print('Afficher',data.head())
        
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
from collections import defaultdict
@app.route('/get_data2')
def get_data2():
    try:
        # Récupérer tous les enregistrements depuis la table search_indicateurs
        rows = db.session.query(
            SearchIndicateur.Domaine,
            SearchIndicateur.Thematique,
            SearchIndicateur.Indicateurs
        ).all()

        # Grouper les indicateurs par Domaine et Thématique
        data = defaultdict(list)
        for domaine, thematique, indicateur in rows:
            key = f"{domaine}, {thematique}"
            data[key].append(indicateur)

        # Convertir en dict classique pour JSON
        data_dict = dict(data)

        return jsonify(data_dict)

    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")
        return jsonify({})




#-------------------------------------------------FIN API

if __name__ == '__main__':
    app.run(debug=True, port=5000)
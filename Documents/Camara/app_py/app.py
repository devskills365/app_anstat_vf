from flask import render_template, request, session, jsonify, abort
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
from models import (
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
# Suite de traitement:
#https://colab.research.google.com/drive/1jVuPWAfmAMnlyLG8JKBt9QiBCKjlCW5k#scrollTo=jj3q_Xy7w_K5
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

    if isinstance(result, dict) and "error" in result:
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
    regions = qr.options_regions() # or qr.options_regions()
    naissance, deces, pop_minute = pop_naissance.naissance_deces_pop()
    
    # We no longer pass graph data to the template. It's fetched via API.
    return render_template('home.html',
                            naissance=naissance,
                            deces=deces,
                            pop_minute=pop_minute,
                            regions=regions)

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


#Pour obtenir 
@app.route('/filter_indicator/<path:indicateur>')
def page_filtration_data(indicateur):

    indicateur_SELECT = urllib.parse.unquote(indicateur)
    definitions = None
    mode_calcul = None
    desaggregation_columns = qr.obtention_data_mysql_niveauDesagr(indicateur_SELECT)

    print('Notre indicateur:', indicateur_SELECT)
    print('Liste des colonnes de désagrégation:', desaggregation_columns)
    
    return render_template(
        'result.html',
        definitions=definitions,
        mode_calcul=mode_calcul,
        colonne_valable=desaggregation_columns,
        indicateur2=indicateur_SELECT
    )




    
@app.route('/process_columns', methods=['POST'])
def process_columns():
    data_request = request.get_json()
    row_columns = data_request.get('row_columns', [])
    col_columns = data_request.get('col_columns', [])
    value_column = data_request.get('value_column', 'Valeur')
    indicateur_name = data_request.get('indicateur_name')
    
    # Récupérer les paramètres de pagination depuis l'URL
    offset = request.args.get('offset', type=int)
    limit = request.args.get('limit', type=int)
    
    my_index_selection = [row_columns, col_columns]
    
    # 1. Calculer l'ensemble des colonnes sélectionnées pour le filtrage
    my_index_flat = list(chain.from_iterable(my_index_selection))
    
    if not my_index_flat:
         return jsonify({"columns": [], "index": [], "data": []})
    
    my_index_set = set(my_index_flat) # <-- C'est cet ensemble qui doit être passé au query

    print('Vérification des valeurs reçues:', my_index_selection)

    if not indicateur_name:
        return jsonify({"error": "Nom de l'indicateur manquant dans la requête"}), 400

    # Étape 1 : Récupérer les données brutes directement depuis la base de données
    # CORRECTION : Passer my_index_set, offset et limit
    print('taille:',len(my_index_set))
    if len(my_index_set)>1:
        df = qr.obtention_data_mysql_requete(
            indicateur_name=indicateur_name,
            my_index_set=my_index_set,
            offset=offset,
            limit=limit
        )
    
    if df.empty:
        return jsonify({"columns": [], "index": [], "data": []})

    # Étape 2 : Appliquer les transformations
    df_filtered = df.copy() 
    
    df_final = pd.DataFrame(df_filtered)
    
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
        data = df_filtered[df_filtered['cle_pivot_table'].apply(lambda x: my_index_set.issubset(set(x.split(','))))].copy()
        
        print('Les colonnes des données extraites:',data.head())
        
        required_cols = row_columns + col_columns + [value_column]
        if not all(col in data.columns for col in required_cols):
             missing_cols = [col for col in required_cols if col not in data.columns]
             return jsonify({"error": f"Certaines colonnes sélectionnées ({', '.join(missing_cols)}) ne sont pas disponibles dans les données filtrées."}), 400

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
        import traceback
        traceback.print_exc()
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
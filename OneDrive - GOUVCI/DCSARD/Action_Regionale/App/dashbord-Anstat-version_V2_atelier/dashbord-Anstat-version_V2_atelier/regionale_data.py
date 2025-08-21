import mysql.connector

# Données originales du fichier JavaScript
data_ratio_eleve_enseignant = {
    'Tengrela': [
        {'year': 2019, 'ratio': 45}, {'year': 2020, 'ratio': 43}, {'year': 2021, 'ratio': 42},
        {'year': 2022, 'ratio': 41}, {'year': 2023, 'ratio': 40}, {'year': 2024, 'ratio': 39}
    ],
    'Boundiali': [
        {'year': 2019, 'ratio': 50}, {'year': 2020, 'ratio': 49}, {'year': 2021, 'ratio': 48},
        {'year': 2022, 'ratio': 47}, {'year': 2023, 'ratio': 46}, {'year': 2024, 'ratio': 45}
    ],
    "Kouto": [
        {'year': 2019, 'ratio': 38}, {'year': 2020, 'ratio': 37}, {'year': 2021, 'ratio': 36},
        {'year': 2022, 'ratio': 35}, {'year': 2023, 'ratio': 34}, {'year': 2024, 'ratio': 33}
    ]
}

data_natalite = {
    'Tengrela': [
        {'year': 2013, 'natalite': 20}, {'year': 2014, 'natalite': 22}, {'year': 2015, 'natalite': 18},
        {'year': 2016, 'natalite': 21}, {'year': 2017, 'natalite': 19}, {'year': 2018, 'natalite': 24},
        {'year': 2019, 'natalite': 23}, {'year': 2020, 'natalite': 22}, {'year': 2021, 'natalite': 25},
        {'year': 2022, 'natalite': 26}, {'year': 2023, 'natalite': 27}
    ],
    'Boundiali': [
        {'year': 2013, 'natalite': 25}, {'year': 2014, 'natalite': 26}, {'year': 2015, 'natalite': 24},
        {'year': 2016, 'natalite': 23}, {'year': 2017, 'natalite': 25}, {'year': 2018, 'natalite': 27},
        {'year': 2019, 'natalite': 28}, {'year': 2020, 'natalite': 26}, {'year': 2021, 'natalite': 29},
        {'year': 2022, 'natalite': 30}, {'year': 2023, 'natalite': 31}
    ],
    "Kouto": [
        {'year': 2013, 'natalite': 18}, {'year': 2014, 'natalite': 19}, {'year': 2015, 'natalite': 17},
        {'year': 2016, 'natalite': 20}, {'year': 2017, 'natalite': 21}, {'year': 2018, 'natalite': 22},
        {'year': 2019, 'natalite': 23}, {'year': 2020, 'natalite': 21}, {'year': 2021, 'natalite': 24},
        {'year': 2022, 'natalite': 25}, {'year': 2023, 'natalite': 26}
    ]
}

data_population = [
    {'departement': "Tengrela", 'hommes': 60000, 'femmes': 60000},
    {'departement': "Boundiali", 'hommes': 45000, 'femmes': 50000},
    {'departement': "Kouto", 'hommes': 55000, 'femmes': 55000},
  
]

data_medical = [
    {'corps': "Infirmiers", 'Tengrela': 80, 'Boundiali': 60, 'Kouto': 75},
    {'corps': "Sage-femmes", 'Tengrela': 40, 'Boundiali': 30, 'Kouto': 35},
    {'corps': "Généralistes", 'Tengrela': 30, 'Boundiali': 25, 'Kouto': 40},
]

# Les autres données ne changent pas car elles ont déjà la colonne 'region'
data_idh = [
    {'region': 'Bagoue', 'year': 2016, 'isf': 0.55},
    {'region': 'Bagoue', 'year': 2020, 'isf': 0.72},
    {'region': 'Bagoue', 'year': 2022, 'isf': 0.60},
    {'region': 'Bagoue', 'year': 2023, 'isf': 0.65},
]
data_taux_chomage = [
    {'region': 'Bagoue', 'year': 2008, 'taux': 12},
    {'region': 'Bagoue', 'year': 2010, 'taux': 8},
    {'region': 'Bagoue', 'year': 2018, 'taux': 10},
    {'region': 'Bagoue', 'year': 2023, 'taux': 9},
]
data_population_poro = [
    {'type': "Urbaine", 'count': 150000},
    {'type': "Rurale", 'count': 250000},
]
data_alphabetisation = [
    {'region': 'Bagoue', 'year': 2016, 'taux': 45},
    {'region': 'Bagoue', 'year': 2017, 'taux': 48},
    {'region': 'Bagoue', 'year': 2018, 'taux': 50},
    {'region': 'Bagoue', 'year': 2019, 'taux': 52},
    {'region': 'Bagoue', 'year': 2020, 'taux': 55},
    {'region': 'Bagoue', 'year': 2021, 'taux': 58},
    {'region': 'Bagoue', 'year': 2022, 'taux': 60},
    {'region': 'Bagoue', 'year': 2023, 'taux': 62},
]
data_taux_brute = [
    {'region': 'Bagoue', 'year': 2018, 'taux': 85},
    {'region': 'Bagoue', 'year': 2019, 'taux': 87},
    {'region': 'Bagoue', 'year': 2020, 'taux': 89},
    {'region': 'Bagoue', 'year': 2021, 'taux': 90},
    {'region': 'Bagoue', 'year': 2022, 'taux': 92},
]
data_taux_electrification = [
    {'region': 'Bagoue', 'year': 2018, 'nombre': 60},
    {'region': 'Bagoue', 'year': 2019, 'nombre': 65},
    {'region': 'Bagoue', 'year': 2020, 'nombre': 70},
    {'region': 'Bagoue', 'year': 2021, 'nombre': 75},
    {'region': 'Bagoue', 'year': 2022, 'nombre': 80},
]

# Variable pour la région par défaut
DEFAULT_REGION = 'Bagoue'

def init_db():
    try:
        conn = mysql.connector.connect(
            user='root',
            password='10080805Tohbi',
            host='127.0.0.1',
            database='annuaire'
        )
        cursor = conn.cursor()

        # Nettoyer les tables
        cursor.execute('TRUNCATE TABLE ratios_eleve_enseignant')
        cursor.execute('TRUNCATE TABLE taux_natalite')
        cursor.execute('TRUNCATE TABLE population_regionale')
        cursor.execute('TRUNCATE TABLE personnel_medical')
        cursor.execute('TRUNCATE TABLE isf')
        cursor.execute('TRUNCATE TABLE taux_chomage')
        cursor.execute('TRUNCATE TABLE population_urbaine_rurale')
        cursor.execute('TRUNCATE TABLE taux_alphabetisation')
        cursor.execute('TRUNCATE TABLE taux_brute_scolarite')
        cursor.execute('TRUNCATE TABLE taux_electrification')

        # Insertion des données
        # Ratios Élève/Enseignant
        for dep, ratios in data_ratio_eleve_enseignant.items():
            for item in ratios:
                # Ajout de 'region' dans la requête INSERT et le tuple de données
                cursor.execute('INSERT INTO ratios_eleve_enseignant (departement, year, ratio, region) VALUES (%s, %s, %s, %s)', (dep, item['year'], item['ratio'], DEFAULT_REGION))
        
        # Taux de Natalité
        for dep, natalites in data_natalite.items():
            for item in natalites:
                # Ajout de 'region' dans la requête INSERT et le tuple de données
                cursor.execute('INSERT INTO taux_natalite (departement, year, natalite, region) VALUES (%s, %s, %s, %s)', (dep, item['year'], item['natalite'], DEFAULT_REGION))
        
        # Population
        for item in data_population:
            # Ajout de 'region' dans la requête INSERT et le tuple de données
            cursor.execute('INSERT INTO population_regionale (departement, hommes, femmes, region) VALUES (%s, %s, %s, %s)', (item['departement'], item['hommes'], item['femmes'], DEFAULT_REGION))
        
        # Personnel Médical
        for item in data_medical:
            for dep in ["Tengrela", "Boundiali", "Kouto"]:
                # Ajout de 'region' dans la requête INSERT et le tuple de données
                cursor.execute('INSERT INTO personnel_medical (corps, departement, nombre, region) VALUES (%s, %s, %s, %s)', (item['corps'], dep, item.get(dep.replace("'", ''), 0), DEFAULT_REGION))
        
        # Les tables suivantes ont déjà la colonne 'region', donc la modification est minime
        # ISF
        for item in data_idh:
            cursor.execute('INSERT INTO isf VALUES (%s, %s, %s)', (item['region'], item['year'], item['isf']))
        
        # Taux de Chômage
        for item in data_taux_chomage:
            cursor.execute('INSERT INTO taux_chomage VALUES (%s, %s, %s)', (item['region'], item['year'], item['taux']))
        
        # Population Urbaine/Rurale
        for item in data_population_poro:
            cursor.execute('INSERT INTO population_urbaine_rurale VALUES (%s, %s, %s)', ('Poro', item['type'], item['count']))
        
        # Taux d'Alphabétisation
        for item in data_alphabetisation:
            cursor.execute('INSERT INTO taux_alphabetisation VALUES (%s, %s, %s)', (item['region'], item['year'], item['taux']))

        # Taux Brut de Scolarité
        for item in data_taux_brute:
            cursor.execute('INSERT INTO taux_brute_scolarite VALUES (%s, %s, %s)', (item['region'], item['year'], item['taux']))

        # Taux d'Électrification
        for item in data_taux_electrification:
            cursor.execute('INSERT INTO taux_electrification VALUES (%s, %s, %s)', (item['region'], item['year'], item['nombre']))
        
        conn.commit()
        print("Données insérées avec succès dans la base de données MySQL.")

    except mysql.connector.Error as err:
        print(f"Erreur de connexion à MySQL : {err}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    init_db()
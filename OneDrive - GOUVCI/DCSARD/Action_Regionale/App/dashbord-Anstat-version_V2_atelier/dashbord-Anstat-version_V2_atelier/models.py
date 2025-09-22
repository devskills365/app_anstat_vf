from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine

# Initialisation de SQLAlchemy
db = SQLAlchemy()

# Modèle pour la table 'directionstatistique'
class DirectionStatistique(db.Model):
    __tablename__ = 'directionstatistique'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<DirectionStatistique(id={self.id}, nom={self.nom})>"

# Modèle pour la table 'region'
class Region(db.Model):
    __tablename__ = 'region'
    region_id = db.Column(db.Integer, primary_key=True)
    f_direction_stat_id = db.Column(db.Integer, db.ForeignKey('directionstatistique.id'), nullable=True)
    nom_region = db.Column(db.Text, nullable=True)
    direction_stat = db.relationship('DirectionStatistique', backref='regions', lazy=True)

    def __repr__(self):
        return f"<Region(region_id={self.region_id}, nom_region={self.nom_region})>"

# Modèle pour la table 'domaine'
class Domaine(db.Model):
    __tablename__ = 'domaine'
    domaine_id = db.Column(db.Integer, primary_key=True)
    nom_domaine = db.Column(db.Text, nullable=True)
    indicateurs = db.relationship('Indicateur', backref='domaine', lazy=True)

    def __repr__(self):
        return f"<Domaine(domaine_id={self.domaine_id}, nom_domaine={self.nom_domaine})>"

# Modèle pour la table 'indicateur'
class Indicateur(db.Model):
    __tablename__ = 'indicateur'
    indicateur_id = db.Column(db.Integer, primary_key=True)
    f_domaine_id = db.Column(db.Integer, db.ForeignKey('domaine.domaine_id'), nullable=True)
    nom_indicateur = db.Column(db.Text, nullable=True)
    definition = db.Column(db.Text, nullable=True)
    mode_calcul = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Indicateur(indicateur_id={self.indicateur_id}, nom_indicateur={self.nom_indicateur})>"

# Modèle pour la table 'indicateur_v2'
class IndicateurV2(db.Model):
    __tablename__ = 'indicateur_v2'
    indicateur_id = db.Column(db.Integer, primary_key=True)
    indicateur = db.Column(db.Text, nullable=True)
    definitions = db.Column(db.Text, nullable=True)
    mode_calcul = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<IndicateurV2(indicateur_id={self.indicateur_id}, indicateur={self.indicateur})>"

# Modèle pour la table 'v1_indicateur'
class V1Indicateur(db.Model):
    __tablename__ = 'v1_indicateur'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Dimension = db.Column(db.String(255), nullable=True)
    Modalites = db.Column(db.String(255), nullable=True)
    Indicateurs = db.Column(db.String(255), nullable=True)
    Annee = db.Column(db.String(25), nullable=True)
    Valeur = db.Column(db.DECIMAL(15, 5), nullable=True)
    cle_dimension = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<V1Indicateur(id={self.id}, Indicateurs={self.Indicateurs}, Annee={self.Annee})>"

# Modèle pour la table 'indicateurs_dashbord_national'
class IndicateursDashbordNational(db.Model):
    __tablename__ = 'indicateurs_dashbord_national'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Domaine = db.Column(db.String(255), nullable=True)
    Indicateur = db.Column(db.String(255), nullable=False)
    Annee = db.Column(db.Integer, nullable=False)
    Source = db.Column(db.String(255), nullable=True)
    Definition = db.Column(db.Text, nullable=True)
    periode_production = db.Column(db.String(255), nullable=True)
    unite = db.Column(db.String(50), nullable=True)
    Valeur = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<IndicateursDashbordNational(id={self.id}, Indicateur={self.Indicateur}, Annee={self.Annee})>"

# Modèle pour la table 'indicateurs_dashbord_region'
class IndicateursDashbordRegion(db.Model):
    __tablename__ = 'indicateurs_dashbord_region'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Domaine = db.Column(db.String(255), nullable=False)
    Indicateur = db.Column(db.String(255), nullable=False)
    Annee = db.Column(db.Integer, nullable=False)
    Source = db.Column(db.String(255), nullable=True)
    Region = db.Column(db.String(255), nullable=False)
    Valeur = db.Column(db.DECIMAL(10, 2), nullable=False)

    def __repr__(self):
        return f"<IndicateursDashbordRegion(id={self.id}, Indicateur={self.Indicateur}, Region={self.Region}, Annee={self.Annee})>"

# Modèle pour la table 'isf'
class Isf(db.Model):
    __tablename__ = 'isf'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region = db.Column(db.String(255), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    isf = db.Column(db.DECIMAL(5, 2), nullable=True)

    def __repr__(self):
        return f"<Isf(region={self.region}, year={self.year}, isf={self.isf})>"

# Modèle pour la table 'personnel_medical'
class PersonnelMedical(db.Model):
    __tablename__ = 'personnel_medical'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    corps = db.Column(db.String(255), nullable=True)
    departement = db.Column(db.String(255), nullable=True)
    nombre = db.Column(db.Integer, nullable=True)
    region = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<PersonnelMedical(corps={self.corps}, region={self.region})>"

# Modèle pour la table 'population_regionale'
class PopulationRegionale(db.Model):
    __tablename__ = 'population_regionale'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    departement = db.Column(db.String(255), nullable=True)
    hommes = db.Column(db.Integer, nullable=True)
    femmes = db.Column(db.Integer, nullable=True)
    region = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<PopulationRegionale(departement={self.departement}, region={self.region})>"

# Modèle pour la table 'population_urbaine_rurale'
class PopulationUrbaineRurale(db.Model):
    __tablename__ = 'population_urbaine_rurale'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region = db.Column(db.String(255), nullable=True)
    type_pop = db.Column(db.String(255), nullable=True)
    count = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<PopulationUrbaineRurale(region={self.region}, type_pop={self.type_pop})>"

# Modèle pour la table 'publications'
class Publications(db.Model):
    __tablename__ = 'publications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categorie = db.Column(db.String(100), nullable=False)
    nom = db.Column(db.String(255), nullable=False)
    nom_region = db.Column(db.String(150), nullable=True)
    fichier = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    resume = db.Column(db.Text, nullable=True)
    date_production = db.Column(db.Date, nullable=True)
    date_publication = db.Column(db.Date, nullable=True)
    mise_a_jour = db.Column(db.DateTime, nullable=True, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f"<Publications(id={self.id}, nom={self.nom})>"

# Modèle pour la table 'ratios_eleve_enseignant'
class RatiosEleveEnseignant(db.Model):
    __tablename__ = 'ratios_eleve_enseignant'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    departement = db.Column(db.String(255), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    ratio = db.Column(db.DECIMAL(5, 2), nullable=True)
    region = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<RatiosEleveEnseignant(departement={self.departement}, year={self.year}, ratio={self.ratio})>"

# Modèle pour la table 'taux_alphabetisation'
class TauxAlphabetisation(db.Model):
    __tablename__ = 'taux_alphabetisation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region = db.Column(db.String(255), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    taux = db.Column(db.DECIMAL(5, 2), nullable=True)

    def __repr__(self):
        return f"<TauxAlphabetisation(region={self.region}, year={self.year}, taux={self.taux})>"

# Modèle pour la table 'taux_brute_scolarite'
class TauxBruteScolarite(db.Model):
    __tablename__ = 'taux_brute_scolarite'
    region = db.Column(db.String(255), primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    taux = db.Column(db.DECIMAL(5, 2), nullable=True)

    def __repr__(self):
        return f"<TauxBruteScolarite(region={self.region}, year={self.year}, taux={self.taux})>"

# Modèle pour la table 'taux_chomage'
class TauxChomage(db.Model):
    __tablename__ = 'taux_chomage'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region = db.Column(db.String(255), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    taux = db.Column(db.DECIMAL(5, 2), nullable=True)

    def __repr__(self):
        return f"<TauxChomage(region={self.region}, year={self.year}, taux={self.taux})>"

# Modèle pour la table 'taux_electrification'
class TauxElectrification(db.Model):
    __tablename__ = 'taux_electrification'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    region = db.Column(db.String(255), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    nombre = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<TauxElectrification(region={self.region}, year={self.year}, nombre={self.nombre})>"

# Modèle pour la table 'taux_natalite'
class TauxNatalite(db.Model):
    __tablename__ = 'taux_natalite'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    departement = db.Column(db.String(255), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    natalite = db.Column(db.DECIMAL(5, 2), nullable=True)
    region = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<TauxNatalite(departement={self.departement}, year={self.year}, natalite={self.natalite})>"


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DataRequete(db.Model):
    __tablename__ = "data_requete"
    __table_args__ = {'extend_existing': True}
    __mapper_args__ = {'primary_key': []}  # table sans clé primaire

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Clé primaire
    Indcateurs=db.Column(db.Text, name="Indicateurs", nullable=False)
    Valeur=db.Column(db.Text, name="Valeur", nullable=True)
    Annee=db.Column(db.Text, name="Annee", nullable=True)
    cle_pivot_table=db.Column(db.Text, name="cle_pivot_table", nullable=True)
    region = db.Column(db.Text, name="Région", nullable=True)
    groupe_ages = db.Column(db.Text, name="Groupe d'âges", nullable=True)
    departement = db.Column(db.Text, name="Département", nullable=True)
    sous_prefecture = db.Column(db.Text, name="Sous-préfecture", nullable=True)
    ages = db.Column(db.Text, name="Âges", nullable=True)
    type_centre_etat_civil = db.Column(db.Text, name="Type de centre d'état civil", nullable=True)
    source_donnees_admnistratives = db.Column(db.Text, name="Source de données admnistratives", nullable=True)
    delai_declaration = db.Column(db.Text, name="Délai de Déclaration", nullable=True)
    statut_decision = db.Column(db.Text, name="Statut de la décision", nullable=True)
    type_consentenement = db.Column(db.Text, name="Type de consentenement", nullable=True)
    statut = db.Column(db.Text, name="Statut", nullable=True)
    cycle = db.Column(db.Text, name="Cycle", nullable=True)
    niveau_prescolaire = db.Column(db.Text, name="Niveau Préscolaire", nullable=True)
    niveau_primaire = db.Column(db.Text, name="Niveau Primaire", nullable=True)
    niveau_secondaire_1 = db.Column(db.Text, name="Niveau Secondaire 1er cycle", nullable=True)
    niveau_secondaire_2 = db.Column(db.Text, name="Niveau Secondaire 2nd cycle", nullable=True)
    niveau_technique = db.Column(db.Text, name="Niveau Technique", nullable=True)
    niveau_superieur = db.Column(db.Text, name="Niveau Supérieur", nullable=True)
    niveau_professionnel = db.Column(db.Text, name="Niveau Professionnel", nullable=True)
    type_examen = db.Column(db.Text, name="Type d'examen", nullable=True)
    commodites = db.Column(db.Text, name="Commodités", nullable=True)
    categorie_enseignants_publics = db.Column(db.Text, name="Catégorie d'enseignants publics", nullable=True)
    categorie_enseignants_prives = db.Column(db.Text, name="Catégorie d'enseignants privés", nullable=True)
    grade_enseignants_primaire = db.Column(db.Text, name="Grade d'enseignants du primaire", nullable=True)
    groupe_ages_scar_pr = db.Column(db.Text, name="Groupe Ages scar_pr", nullable=True)
    lieu_accouchement = db.Column(db.Text, name="Lieu d'accouchement", nullable=True)
    etat_vaccinal = db.Column(db.Text, name="Etat vaccinal", nullable=True)
    types_vaccination = db.Column(db.Text, name="Types de vaccination", nullable=True)
    pathologie = db.Column(db.Text, name="Pathologie", nullable=True)
    tranche_age = db.Column(db.Text, name="Tranche d'âge", nullable=True)
    maladies_pev = db.Column(db.Text, name="Maladies du PEV", nullable=True)
    maladies_infectieuses = db.Column(db.Text, name="Maladies infectieuses", nullable=True)
    infections_respiratoire_aigue = db.Column(db.Text, name="Infections respiratoire aigüe", nullable=True)
    maladies_ist = db.Column(db.Text, name="Maladies IST", nullable=True)
    type_maladie = db.Column(db.Text, name="Type de Maladie", nullable=True)
    activites_iec = db.Column(db.Text, name="Activités IEC", nullable=True)
    service_medicaux = db.Column(db.Text, name="Service Médicaux", nullable=True)
    types_infrastructures_prives = db.Column(db.Text, name="Types d'infrastructures privés", nullable=True)
    types_infrastructures_publique = db.Column(db.Text, name="Types d'infrastructures publique", nullable=True)
    type_medecin = db.Column(db.Text, name="Type de médecin", nullable=True)
    types_suivi = db.Column(db.Text, name="Types de suivi", nullable=True)
    types_vulnerabilites = db.Column(db.Text, name="Types de vulnérabilités", nullable=True)
    types_prises_charge = db.Column(db.Text, name="Types de prises en charge", nullable=True)
    niveau = db.Column(db.Text, name="Niveau", nullable=True)
    type_prestations = db.Column(db.Text, name="Type des Prestations", nullable=True)
    trimestre = db.Column(db.Text, name="Trimestre", nullable=True)
    type_infra_sport = db.Column(db.Text, name="Type d'infrastructures ou organisations sportives", nullable=True)
    disciplines_sportives = db.Column(db.Text, name="Disciplines sportives", nullable=True)
    type_infra_culturelles = db.Column(db.Text, name="Type d'infrastructures culturelles", nullable=True)
    type_patrimoine_culturel = db.Column(db.Text, name="Type de Patrimoines culturels", nullable=True)
    type_patrimoine_immat = db.Column(db.Text, name="Type de Patrimoines culturels immatériels", nullable=True)
    type_actions_culturelles = db.Column(db.Text, name="Type d'actions culturelles et artistiques", nullable=True)
    type_operateurs_oeuvres = db.Column(db.Text, name="Type d'opérateurs des œuvres de l'esprit", nullable=True)
    type_groupes_culturels = db.Column(db.Text, name="Type de groupes culturels", nullable=True)
    type_manifestations_culturelles = db.Column(db.Text, name="Type de manifestations culturelles", nullable=True)
    type_culture_export = db.Column(db.Text, name="Type de culture d'exportation", nullable=True)
    type_culture_vivriere = db.Column(db.Text, name="type de culture vivrière", nullable=True)
    type_culture_maraichere = db.Column(db.Text, name="type de culture maraichère", nullable=True)
    type_produit_rente = db.Column(db.Text, name="type de produit agricole de rente", nullable=True)
    type_produit_vivrier = db.Column(db.Text, name="type de produit vivrier", nullable=True)
    especes = db.Column(db.Text, name="Espèces", nullable=True)
    type_animal = db.Column(db.Text, name="Type d’animal", nullable=True)
    type_peche = db.Column(db.Text, name="Type de Pêche", nullable=True)
    produits = db.Column(db.Text, name="Produits", nullable=True)
    type_projets_realises = db.Column(db.Text, name="Type de projets réalisés", nullable=True)
    type_poissons = db.Column(db.Text, name="Type de poissons", nullable=True)
    type_produits_miniers = db.Column(db.Text, name="Type de produits miniers", nullable=True)
    type_minierais = db.Column(db.Text, name="Type de minérais", nullable=True)
    type_produits_petrol = db.Column(db.Text, name="Type de produits pétroliers", nullable=True)
    type_stations = db.Column(db.Text, name="Type de stations", nullable=True)
    etat_ouvrages = db.Column(db.Text, name="Etat des ouvrages", nullable=True)
    type_ouvrages = db.Column(db.Text, name="Type d'ouvrages", nullable=True)
    type_abonnement = db.Column(db.Text, name="Type d'abonnement", nullable=True)
    types_vehicules = db.Column(db.Text, name="Types de véhicules", nullable=True)
    categories_permis = db.Column(db.Text, name="Catégories de permis", nullable=True)
    type_vehicules_marchandises = db.Column(db.Text, name="Type de véhicules marchandises", nullable=True)
    type_vehicules_passagers = db.Column(db.Text, name="Type de véhicules passagers", nullable=True)
    categories_routes = db.Column(db.Text, name="catégories de routes", nullable=True)
    compagnies_transport = db.Column(db.Text, name="Compagnies de transport", nullable=True)
    type_transport = db.Column(db.Text, name="Type de transport", nullable=True)
    type_abonnes = db.Column(db.Text, name="type d'abonnés", nullable=True)
    nature_mandat = db.Column(db.Text, name="nature du mandat", nullable=True)
    categorie_hotels = db.Column(db.Text, name="Catégorie d’hôtels", nullable=True)
    nature_juridique = db.Column(db.Text, name="Nature juridique", nullable=True)
    nationalite = db.Column(db.Text, name="Nationalité", nullable=True)
    secteur_activites = db.Column(db.Text, name="Secteur d'activités", nullable=True)
    collectivites_territoriales = db.Column(db.Text, name="Collectivités territoriales", nullable=True)
    secteurs_activite = db.Column(db.Text, name="Secteurs d'activité", nullable=True)
    regime_imposition = db.Column(db.Text, name="Régime d’imposition", nullable=True)
    forme_juridique = db.Column(db.Text, name="Forme juridique", nullable=True)
    type_impots = db.Column(db.Text, name="Type d'impôts", nullable=True)
    type_nationalite = db.Column(db.Text, name="Type de nationalité", nullable=True)
    type_infra_aquacoles = db.Column(db.Text, name="Types d'infrastructures de production aquacoles", nullable=True)
    types_especes_eleves = db.Column(db.Text, name="Types d’espèces élevés", nullable=True)
    produits_petrol = db.Column(db.Text, name="Produits pétroliers", nullable=True)
    domaines = db.Column(db.Text, name="Domaines", nullable=True)
    mois = db.Column(db.Text, name="Mois", nullable=True)
    directions_regionales = db.Column(db.Text, name="Directions régionales/Ministères", nullable=True)
    milieu_residence = db.Column(db.Text, name="Milieu de résidence", nullable=True)
    situation_emploi = db.Column(db.Text, name="Situation de l’emploi", nullable=True)
    branche_activites = db.Column(db.Text, name="Branche d'activités", nullable=True)
    secteur_chomage = db.Column(db.Text, name="Secteur d'activités du chomage technique", nullable=True)
    categories = db.Column(db.Text, name="Catégories", nullable=True)
    secteur_licenciement = db.Column(db.Text, name="Secteur d'activités du licenciement collectif", nullable=True)
    projets_realises = db.Column(db.Text, name="Projets réalisés", nullable=True)
    type_violence = db.Column(db.Text, name="Type de violence", nullable=True)
    activites_prevention_vbg = db.Column(db.Text, name="Activités de prévention (VBG)", nullable=True)
    activites_prevention_enfants = db.Column(db.Text, name="Activités de prévention chez les enfants", nullable=True)
    type_violence_enfance = db.Column(db.Text, name="Type de violence (protection de l'enfance)", nullable=True)
    nature_services = db.Column(db.Text, name="Nature des services", nullable=True)
    types_sorties_interventions = db.Column(db.Text, name="Types de sorties d'interventions", nullable=True)
    types_victimes = db.Column(db.Text, name="Types de victimes", nullable=True)
    types_moyens_extinction = db.Column(db.Text, name="Types de moyens d’extinction", nullable=True)
    type_juriduction = db.Column(db.Text, name="Type de juriduction", nullable=True)
    nature_affaires = db.Column(db.Text, name="Nature des affaires", nullable=True)
    type_criminalites = db.Column(db.Text, name="Type de Criminalités", nullable=True)
    type_infractions = db.Column(db.Text, name="Type d'infractions", nullable=True)
    type_infractions_biens = db.Column(db.Text, name="Type d'infractions (atteinte aux biens)", nullable=True)
    type_infractions_corporelle = db.Column(db.Text, name="Type d'infractions (atteinte corporelle)", nullable=True)
    type_infractions_moeurs = db.Column(db.Text, name="Type d'infractions (atteinte aux  mœurs)", nullable=True)
    type_infractions_autres = db.Column(db.Text, name="Type d'infractions (autre infraction)", nullable=True)
    type_affaire = db.Column(db.Text, name="Type d'affaire", nullable=True)
    parti_politique = db.Column(db.Text, name="Parti politique", nullable=True)
    sexe = db.Column(db.Text, name="Sexe", nullable=True)
    mairies = db.Column(db.Text, name="Mairies", nullable=True)
    national = db.Column(db.Text, name="National", nullable=True)

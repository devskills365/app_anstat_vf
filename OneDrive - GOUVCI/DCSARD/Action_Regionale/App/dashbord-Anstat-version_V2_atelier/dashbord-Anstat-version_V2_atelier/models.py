from flask_sqlalchemy import SQLAlchemy

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

    # Relation avec DirectionStatistique
    direction_stat = db.relationship('DirectionStatistique', backref='regions', lazy=True)

    def __repr__(self):
        return f"<Region(region_id={self.region_id}, nom_region={self.nom_region})>"

# Modèle pour la table 'domaine'
class Domaine(db.Model):
    __tablename__ = 'domaine'

    domaine_id = db.Column(db.Integer, primary_key=True)
    nom_domaine = db.Column(db.Text, nullable=True)

    # Relation avec Indicateur
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
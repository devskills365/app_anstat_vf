/* Ici , ily a un filtre sur l'année et l'indicateur */
USE annuaire;

-- Table pour l'évolution de la population
CREATE TABLE population (
    id INTEGER PRIMARY KEY auto_increment,
    year INTEGER NOT NULL,
    population INTEGER NOT NULL
);

-- Table pour le taux de scolarisation
CREATE TABLE school_enrollment (
    id INTEGER PRIMARY KEY auto_increment,
    year INTEGER NOT NULL,
    enrollment_rate FLOAT NOT NULL
);

-- Table pour la répartition par âge
CREATE TABLE age_distribution (
    id INTEGER PRIMARY KEY auto_increment,
    age_group TEXT NOT NULL,
    population INTEGER NOT NULL,
    year INTEGER NOT NULL
);

-- Insertion dans la table
-- Exemple de données pour population
INSERT INTO population (year, population) VALUES
(2019, 28000000),
(2020, 28500000),
(2021, 29000000),
(2022, 29500000),
(2023, 30000000);

-- Exemple pour taux de scolarisation
INSERT INTO school_enrollment (year, enrollment_rate) VALUES
(2019, 60),
(2020, 62),
(2021, 65),
(2022, 68),
(2023, 70);

-- Exemple pour répartition par âge (2023)
INSERT INTO age_distribution (age_group, population, year) VALUES
('0-14', 8000000, 2023),
('15-24', 6000000, 2023),
('25-54', 10000000, 2023),
('55-64', 3000000, 2023),
('65+', 2000000, 2023);



-- Pour les région

-- Création des tables
CREATE TABLE `ratios_eleve_enseignant` (
    `departement` VARCHAR(255),
    `year` INT,
    `ratio` DECIMAL(5, 2)
);

CREATE TABLE `taux_natalite` (
    `departement` VARCHAR(255),
    `year` INT,
    `natalite` DECIMAL(5, 2)
);

CREATE TABLE `population_regionale` (
    `departement` VARCHAR(255),
    `hommes` INT,
    `femmes` INT
);

CREATE TABLE `personnel_medical` (
    `corps` VARCHAR(255),
    `departement` VARCHAR(255),
    `nombre` INT
);

CREATE TABLE `isf` (
    `region` VARCHAR(255),
    `year` INT,
    `isf` DECIMAL(5, 2)
);

CREATE TABLE `taux_chomage` (
    `region` VARCHAR(255),
    `year` INT,
    `taux` DECIMAL(5, 2)
);

CREATE TABLE `population_urbaine_rurale` (
    `region` VARCHAR(255),
    `type_pop` VARCHAR(255),
    `count` INT
);

CREATE TABLE `taux_alphabetisation` (
    `region` VARCHAR(255),
    `year` INT,
    `taux` DECIMAL(5, 2)
);

CREATE TABLE `taux_brute_scolarite` (
    `region` VARCHAR(255),
    `year` INT,
    `taux` DECIMAL(5, 2)
);

CREATE TABLE `taux_electrification` (
    `region` VARCHAR(255),
    `year` INT,
    `nombre` INT
);

























































SELECT
    i.nomIndicateur AS Indicateur,
    GROUP_CONCAT(DISTINCT d.nomDimension ORDER BY d.nomDimension ASC SEPARATOR ', ') AS Dimensions,
    GROUP_CONCAT(DISTINCT m.nomModalites ORDER BY m.nomModalites ASC SEPARATOR ' / ') AS Modalites,
    a.valAnnees AS Annee,
    don.valDonnees AS Valeur
FROM
    indicateurs i
JOIN
    donnees don ON i.idIndicateurs = don.f_idIndicateurs
JOIN
    annees a ON don.f_idAnnees = a.idAnnees
LEFT JOIN
    donnees_modalites dm ON don.idDonnees = dm.f_idDonnees
LEFT JOIN
    modalites m ON dm.f_idModalites = m.idModalites
LEFT JOIN
    dimensions d ON m.f_idDimensions = d.idDimensions
WHERE
    a.valAnnees = 2009 AND i.nomIndicateur = 'Effectif de la population' -- Ajout du filtre pour l'indicateur
GROUP BY
    i.nomIndicateur,
    a.valAnnees,
    don.valDonnees
ORDER BY
    i.nomIndicateur,
    a.valAnnees;
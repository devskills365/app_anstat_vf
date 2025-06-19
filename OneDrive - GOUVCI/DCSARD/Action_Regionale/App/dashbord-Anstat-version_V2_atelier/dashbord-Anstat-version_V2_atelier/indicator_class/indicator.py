from typing import Dict, List, Any

class Indicator:
    def __init__(self, domaine: str, modal: Dict[str, str], 
                 metadata: Dict[str, Any], value: Any, definition: str, source_of_data: str):
        """
        Initialise un indicateur sans attribut level explicite.
        """
        # Validations
        if not domaine or not isinstance(domaine, str):
            raise ValueError("Le domaine doit être une chaîne non vide.")
        if not modal or not isinstance(modal, dict):
            raise ValueError("Modal doit être un dictionnaire non vide.")
        if not all(isinstance(key, str) and isinstance(value, str) for key, value in modal.items()):
            raise ValueError("Les clés et valeurs de modal doivent être des chaînes.")

        self._domaine = domaine
        self._modal = modal
        self._metadata = metadata
        self._value = value
        self._definition = definition
        self._source_of_data = source_of_data

    # Getters
    @property
    def domaine(self) -> str:
        return self._domaine

    @property
    def level(self) -> List[str]:
        return list(self._modal.keys())

    @property
    def modal(self) -> Dict[str, str]:
        return self._modal

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata

    @property
    def value(self) -> Any:
        return self._value

    @property
    def definition(self) -> str:
        return self._definition

    @property
    def source_of_data(self) -> str:
        return self._source_of_data

    # Setter pour value
    @value.setter
    def value(self, new_value: Any):
        if new_value is not None:
            self._value = new_value
        else:
            raise ValueError("La valeur ne peut pas être None.")

    def __str__(self) -> str:
        return (f"Indicator(domaine={self._domaine}, level={self.level}, "
                f"modal={self._modal}, value={self._value}, "
                f"definition={self._definition}, source={self._source_of_data})")

    # Méthode pour un affichage formaté
    def formatted_display(self) -> str:
        modal_str = ", ".join(f"{k}: {v}" for k, v in self._modal.items())
        return (f"Indicateur:\n"
                f"  Domaine: {self._domaine}\n"
                f"  Modalités: {modal_str}\n"
                f"  Valeur: {self._value}\n"
                f"  Définition: {self._definition}\n"
                f"  Source: {self._source_of_data}\n"
                f"  Métadonnées: {self._metadata}")

# Fonction pour créer et afficher 5 indicateurs
def display_five_indicators():
    # Liste pour stocker les indicateurs
    indicators = []

    # Création de 5 indicateurs fictifs
    try:
        # Indicateur 1
        indicators.append(Indicator(
            domaine="Santé",
            modal={"Région": "Poro", "Sexe": "Féminin", "Année": "2020"},
            metadata={"unité": "pourcentage"},
            value=75.5,
            definition="Taux de vaccination contre la grippe",
            source_of_data="Ministère de la Santé"
        ))

        # Indicateur 2
        indicators.append(Indicator(
            domaine="Éducation",
            modal={"Région": "Abidjan", "Sexe": "Masculin", "Année": "2021"},
            metadata={"unité": "nombre"},
            value=1200,
            definition="Nombre d'étudiants inscrits",
            source_of_data="Ministère de l'Éducation"
        ))

        # Indicateur 3
        indicators.append(Indicator(
            domaine="Santé",
            modal={"Région": "Yamoussoukro", "Sexe": "Féminin", "Année": "2022"},
            metadata={"unité": "pourcentage"},
            value=82.3,
            definition="Taux de couverture sanitaire",
            source_of_data="OMS"
        ))

        # Indicateur 4
        indicators.append(Indicator(
            domaine="Économie",
            modal={"Région": "Poro", "Année": "2023"},
            metadata={"unité": "USD"},
            value=15000,
            definition="Revenu moyen par habitant",
            source_of_data="Banque Mondiale"
        ))

        # Indicateur 5
        indicators.append(Indicator(
            domaine="Environnement",
            modal={"Région": "Abidjan", "Année": "2024"},
            metadata={"unité": "tonnes"},
            value=500,
            definition="Émissions de CO2",
            source_of_data="Agence de l'Environnement"
        ))

        # Affichage simple
        print("=== Affichage simple des 5 indicateurs ===")
        for i, indicator in enumerate(indicators, 1):
            print(f"Indicateur {i}: {indicator}")

        # Affichage formaté
        print("\n=== Affichage formaté des 5 indicateurs ===")
        for i, indicator in enumerate(indicators, 1):
            print(f"\nIndicateur {i}")
            print("-" * 50)
            print(indicator.formatted_display())

    except ValueError as e:
        print(f"Erreur lors de la création des indicateurs : {e}")

# Exécution
if __name__ == "__main__":
    display_five_indicators()
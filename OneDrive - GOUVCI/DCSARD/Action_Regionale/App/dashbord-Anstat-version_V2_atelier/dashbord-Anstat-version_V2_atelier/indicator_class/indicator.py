from typing import Dict, List, Any

class Indicator:
    def __init__(self, indicateur: str, domaine: str, subDomaine: str, modal: Dict[str, str],
                 metadata: Dict[str, Any], value: Any, definition: str, source_of_data: str):
        """
        Initialise un indicateur.

        Args:
            indicateur (str): Le nom de l'indicateur (ex. "Nombre de personnes vaccinées", "Taux de scolarisation").
            domaine (str): Le domaine de l'indicateur (ex. santé, éducation).
            subDomaine (str): Le sous-domaine de l'indicateur (ex. vaccination, santé publique).
            modal (Dict[str, str]): Dictionnaire des modalités (ex. {"Région": "Poro", "Sexe": "Féminin", "Année": "2020"}).
            metadata (Dict[str, Any]): Métadonnées associées.
            value (Any): Valeur de l'indicateur.
            definition (str): Définition de l'indicateur.
            source_of_data (str): Source des données.
        """
        # Validations
        if not indicateur or not isinstance(indicateur, str):
            raise ValueError("L'indicateur doit être une chaîne non vide.")
        if not domaine or not isinstance(domaine, str):
            raise ValueError("Le domaine doit être une chaîne non vide.")
        if not subDomaine or not isinstance(subDomaine, str):
            raise ValueError("Le sous-domaine doit être une chaîne non vide.")
        if not modal or not isinstance(modal, dict):
            raise ValueError("Modal doit être un dictionnaire non vide.")
        if not all(isinstance(key, str) and isinstance(value, str) for key, value in modal.items()):
            raise ValueError("Les clés et valeurs de modal doivent être des chaînes.")

        self._indicateur = indicateur
        self._domaine = domaine
        self._subDomaine = subDomaine
        self._modal = modal
        self._metadata = metadata
        self._value = value
        self._definition = definition
        self._source_of_data = source_of_data

    # Getters
    @property
    def indicateur(self) -> str:
        return self._indicateur

    @property
    def domaine(self) -> str:
        return self._domaine

    @property
    def subDomaine(self) -> str:
        return self._subDomaine

    @property
    def level(self) -> List[str]:
        """Retourne les dimensions (clés de modal) comme level."""
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

    # Setters
    @indicateur.setter
    def indicateur(self, new_indicateur: str):
        if not new_indicateur or not isinstance(new_indicateur, str):
            raise ValueError("Le nom de l'indicateur doit être une chaîne non vide.")
        self._indicateur = new_indicateur

    @value.setter
    def value(self, new_value: Any):
        if new_value is not None:
            self._value = new_value
        else:
            raise ValueError("La valeur ne peut pas être None.")

    @subDomaine.setter
    def subDomaine(self, new_subDomaine: str):
        if not new_subDomaine or not isinstance(new_subDomaine, str):
            raise ValueError("Le sous-domaine doit être une chaîne non vide.")
        self._subDomaine = new_subDomaine

    # Méthode pour mettre à jour une modalité
    def update_modal(self, dimension: str, value: str):
        if dimension not in self._modal:
            raise ValueError(f"La dimension '{dimension}' n'existe pas dans modal.")
        if not isinstance(value, str):
            raise ValueError("La valeur de la modalité doit être une chaîne.")
        self._modal[dimension] = value
        print(f"Modalité '{dimension}' mise à jour avec la valeur '{value}'.")


    # Méthode pour ajouter une nouvelle dimension et modalité
    def add_dimension(self, dimension: str, modal_value: str):
        if not isinstance(dimension, str) or not isinstance(modal_value, str):
            raise ValueError("La dimension et la modalité doivent être des chaînes.")
        if dimension in self._modal:
            raise ValueError(f"La dimension '{dimension}' existe déjà.")
        self._modal[dimension] = modal_value
        print(f"Nouvelle dimension '{dimension}' ajoutée avec la valeur '{modal_value}'.")
      

    # Méthode pour supprimer une dimension et sa modalité
    def remove_dimension(self, dimension: str):
        if dimension not in self._modal:
            raise ValueError(f"La dimension '{dimension}' n'existe pas dans modal.")
        del self._modal[dimension]
        print(f"Dimension '{dimension}' supprimée.")
 

    # Méthode pour afficher l'indicateur (représentation pour les développeurs)
    def __repr__(self) -> str:
        return (f"Indicator(indicateur='{self._indicateur}', domaine='{self._domaine}', "
                f"subDomaine='{self._subDomaine}', modal={self._modal}, value={self._value})")

    # Méthode pour un affichage formaté (pour les utilisateurs finaux)
    def formatted_display(self) -> str:
        modal_str = ", ".join(f"{k}: {v}" for k, v in self._modal.items())
        level_str = ", ".join(self.level)
        return (f"Indicateur: {self._indicateur}\n"
                f"  Domaine: {self._domaine}\n"
                f"  Sous-domaine: {self._subDomaine}\n"
                f"  Dimensions (Level): {level_str}\n"
                f"  Modalités: {modal_str}\n"
                f"  Valeur: {self._value}\n"
                f"  Définition: {self._definition}\n"
                f"  Source: {self._source_of_data}\n"
                f"  Métadonnées: {self._metadata}")


class IndicatorManager:
    def __init__(self):
        self.indicators: List[Indicator] = []

    def add_indicator(self, indicator: Indicator):
        """Ajoute un indicateur à la liste."""
        if not isinstance(indicator, Indicator):
            raise TypeError("L'objet à ajouter doit être une instance de 'Indicator'.")
        # Consider adding logic to prevent adding duplicate indicators based on
        # a unique combination (e.g., indicateur name, domaine, subDomaine, and modal).
        self.indicators.append(indicator)
        print(f"Indicateur ajouté : {indicator.indicateur}")
  

    def remove_indicator(self, indicator_to_remove: Indicator):
        """Supprime un indicateur de la liste."""
        try:
            self.indicators.remove(indicator_to_remove)
            print(f"Indicateur '{indicator_to_remove.indicateur}' supprimé.")
     
        except ValueError:
            print(f"Erreur: L'indicateur '{indicator_to_remove.indicateur}' n'a pas été trouvé.")

    def update_indicator(self, old_indicator: Indicator, new_indicator_data: Dict[str, Any]):
        """
        Met à jour un indicateur existant.

        Args:
            old_indicator (Indicator): L'indicateur existant à mettre à jour.
            new_indicator_data (Dict[str, Any]): Un dictionnaire contenant les nouvelles données
                                                 pour les attributs de l'indicateur.
                                                 Ex: {"value": 150, "subDomaine": "nouv_sous_domaine", "indicateur": "Nouveau Nom"}
        """
        try:
            index = self.indicators.index(old_indicator)
            current_indicator = self.indicators[index]

            for key, value in new_indicator_data.items():
                if hasattr(current_indicator, key):
                    # Use setters if available, otherwise direct assignment
                    if key == 'indicateur':
                        current_indicator.indicateur = value
                    elif key == 'value':
                        current_indicator.value = value
                    elif key == 'subDomaine':
                        current_indicator.subDomaine = value
                    elif key == 'modal' and isinstance(value, dict):
                        # For modal, you might want to provide specific update_modal, add_dimension, remove_dimension
                        # or replace it entirely. Here, we'll replace for simplicity.
                        current_indicator._modal = value # Direct access, consider adding a setter for modal if needed
                    elif key == 'metadata' and isinstance(value, dict):
                        current_indicator._metadata = value # Direct access
                    elif key == 'definition':
                        current_indicator._definition = value
                    elif key == 'source_of_data':
                        current_indicator._source_of_data = value
                    elif key == 'domaine': # Added setter for domaine if needed, or direct assignment
                        current_indicator._domaine = value
                    else:
                        setattr(current_indicator, f"_{key}", value) # Fallback for other attributes
                else:
                    print(f"Avertissement: L'attribut '{key}' n'existe pas dans l'objet Indicator.")
            print(f"Indicateur '{current_indicator.indicateur}' mis à jour.")
    
        except ValueError:
            print(f"Erreur: L'indicateur '{old_indicator.indicateur}' n'a pas été trouvé pour la mise à jour.")
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'indicateur: {e}")

    def find_indicator(self, **kwargs) -> List[Indicator]:
        """
        Recherche des indicateurs basés sur les critères fournis.
        Ex: find_indicator(domaine="Santé", indicateur="Nombre de personnes vaccinées", modal={"Région": "Poro"})
        """
        found_indicators = []
        for indicator in self.indicators:
            match = True
            for key, value in kwargs.items():
                if key == "modal":
                    if not all(item in indicator.modal.items() for item in value.items()):
                        match = False
                        break
                elif hasattr(indicator, key):
                    if getattr(indicator, key) != value:
                        match = False
                        break
                elif hasattr(indicator, f"_{key}"): # Check private attributes
                     if getattr(indicator, f"_{key}") != value:
                        match = False
                        break
                else:
                    match = False # If the attribute doesn't exist
                    break
            if match:
                found_indicators.append(indicator)
        return found_indicators


if __name__ == "__main__":
    print('--- Initialisation et affichage ---')
    # Création d'un indicateur
    indicator1 = Indicator(
        indicateur="Pourcentage de filles vaccinées",
        domaine="Santé",
        subDomaine="Vaccination",
        modal={"Région": "Poro", "Sexe": "Féminin", "Année": "2020"},
        metadata={"Unité": "%", "Type": "Taux"},
        value=85.5,
        definition="Pourcentage de filles vaccinées contre la rougeole.",
        source_of_data="Ministère de la Santé"
    )
    print(indicator1.formatted_display())
    print("\n--- Test des setters ---")
    indicator1.value = 88.0
    indicator1.subDomaine = "Vaccination Infantile"
    indicator1.indicateur = "Taux de vaccination des enfants"
    print(f"Nouvelle valeur: {indicator1.value}")
    print(f"Nouveau sous-domaine: {indicator1.subDomaine}")
    print(f"Nouveau nom de l'indicateur: {indicator1.indicateur}")


    print("\n--- Test des fonctions de modalité ---")
    indicator1.update_modal("Année", "2021")
    print(f"Modalités après mise à jour: {indicator1.modal}")

    try:
        indicator1.add_dimension("Groupe d'âge", "0-5 ans")
        print(f"Modalités après ajout: {indicator1.modal}")
        indicator1.add_dimension("Région", "Est") # Ceci devrait lever une erreur
    except ValueError as e:
        print(f"Erreur attendue lors de l'ajout d'une dimension existante: {e}")

    try:
        indicator1.remove_dimension("Sexe")
        print(f"Modalités après suppression: {indicator1.modal}")
        indicator1.remove_dimension("Ville") # Ceci devrait lever une erreur
    except ValueError as e:
        print(f"Erreur attendue lors de la suppression d'une dimension inexistante: {e}")

    print("\n--- Test du Manager d'Indicateurs ---")
    manager = IndicatorManager()

    # Ajout d'indicateurs
    manager.add_indicator(indicator1)

    indicator2 = Indicator(
        indicateur="Taux de scolarisation au primaire",
        domaine="Éducation",
        subDomaine="Scolarisation",
        modal={"Région": "Poro", "Niveau": "Primaire", "Année": "2022"},
        metadata={"Unité": "%", "Type": "Taux"},
        value=92.1,
        definition="Pourcentage d'enfants scolarisés au primaire.",
        source_of_data="Ministère de l'Éducation"
    )
    manager.add_indicator(indicator2)

    indicator3 = Indicator(
        indicateur="Taux de mortalité infantile",
        domaine="Santé",
        subDomaine="Mortalité",
        modal={"Région": "Bas-Sassandra", "Année": "2021"},
        metadata={"Unité": "Pour 1000 naissances vivantes", "Type": "Taux"},
        value=45.7,
        definition="Nombre de décès d'enfants de moins d'un an pour 1000 naissances vivantes.",
        source_of_data="Institut National de la Statistique"
    )
    manager.add_indicator(indicator3)

    print("\n--- Indicateurs après ajout ---")
    for ind in manager.indicators:
        print(ind)

    print("\n--- Mise à jour d'un indicateur ---")
    # Mettre à jour la valeur et ajouter une nouvelle métadonnée à indicator1
    manager.update_indicator(indicator1, {"value": 90.0, "metadata": {"Unité": "%", "Type": "Taux", "Fréquence": "Annuelle"}})
    print(f"Indicateur 1 après mise à jour: {indicator1.formatted_display()}")

    # Mettre à jour le sous-domaine et le nom de l'indicateur de indicator2
    manager.update_indicator(indicator2, {"subDomaine": "Taux de scolarisation Général", "indicateur": "Taux de scolarisation"})
    print(f"Indicateur 2 après mise à jour du sous-domaine et du nom: {indicator2}")

    print("\n--- Recherche d'indicateurs ---")
    found = manager.find_indicator(domaine="Santé")
    print(f"Indicateurs trouvés dans le domaine 'Santé': {found}")

    found_by_name = manager.find_indicator(indicateur="Taux de mortalité infantile")
    print(f"Indicateurs trouvés par nom 'Taux de mortalité infantile': {found_by_name}")

    found_by_modal = manager.find_indicator(modal={"Région": "Poro", "Année": "2021"})
    print(f"Indicateurs trouvés avec modalité {{'Région': 'Poro', 'Année': '2021'}}: {found_by_modal}")

    found_by_subdomaine = manager.find_indicator(subDomaine="Scolarisation")
    print(f"Indicateurs trouvés avec sous-domaine 'Scolarisation': {found_by_subdomaine}")


    print("\n--- Suppression d'un indicateur ---")
    manager.remove_indicator(indicator2)

    print("\n--- Indicateurs après suppression ---")
    for ind in manager.indicators:
        print(ind)

    # Essayer de supprimer un indicateur qui n'existe plus
    manager.remove_indicator(indicator2)
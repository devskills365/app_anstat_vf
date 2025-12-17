# =========================================================
# 💡 Nouvelle Fonction : Traitement Vectoriel des Dimensions
# =========================================================
import pandas as pd
def expand_dimensions(df):
    """
    Transforme les colonnes 'Dimension' et 'Modalites' (format 'A/B') 
    en colonnes séparées (A et B) de manière vectorielle.
    
    Correction: Gère mieux les valeurs NaN/None/vides dans 'Dimension' et 'Modalites'.
    """
    # Cloner pour éviter le SettingWithCopyWarning et s'assurer que les colonnes existent
    df_copy = df.copy()

    if df_copy.empty or 'Dimension' not in df_copy.columns or 'Modalites' not in df_copy.columns:
        return df_copy.dropna(axis=1, how='all')

    def process_row(row):
        """Fonction interne pour traiter une ligne et créer la Series des nouvelles colonnes."""
        
        dim_str = str(row.get('Dimension')).strip()
        mod_str = str(row.get('Modalites')).strip()
        
        # 💡 CORRECTION : Vérifie si les données sont valides avant de splitter
        if not dim_str or dim_str.lower() in ('none', 'nan') or \
           not mod_str or mod_str.lower() in ('none', 'nan'):
            return pd.Series({})
            
        try:
            dims = [col.strip() for col in dim_str.split('/')]
            values = [val.strip() for val in mod_str.split('/')]
            
            # Création du dictionnaire des nouvelles colonnes
            valid_pairs = [(d, v) for d, v in zip(dims, values) if d and v]
            return pd.Series(dict(valid_pairs))
            
        except Exception:
            # En cas d'erreur de format inattendue, retourne un objet vide
            return pd.Series({})

    # Application vectorielle: Ceci est la partie performante.
    expanded_df = df_copy.apply(process_row, axis=1)

    # Concaténer les nouvelles colonnes et supprimer les colonnes originales
    cols_to_drop = ['Dimension', 'Modalites']
    df_result = pd.concat([df_copy.drop(columns=cols_to_drop, errors='ignore'), expanded_df], axis=1)

    return df_result.dropna(axis=1, how='all')
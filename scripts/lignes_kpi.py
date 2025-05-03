import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate
import numpy as np

# 1. Import du fichier Excel
def import_data(filename):
    try:
        df = pd.read_excel(filename)
        print(f"Fichier Excel {filename} chargé avec succès.")
        return df
    except FileNotFoundError:
        print("Erreur: Fichier non trouvé.")
        return None
    except Exception as e:
        print(f"Erreur lors du chargement du fichier Excel: {str(e)}")
        return None

# 2. Calcul des indicateurs avec corrections
def calculate_indicators(df):
    # Calcul des indicateurs de base
    df['TBF (h)'] = df['To (h)'] - df['Ta (h)']
    df['MTTR'] = df['Ta (h)'] / df['Nombre des pannes']
    df['MTBF'] = df['TBF (h)'] / df['Nombre des pannes']
    
    # Taux de défaillance en pourcentage (λ * 100)
    df['Taux de défaillance (%)'] = (1 / df['MTBF']) * 100
    
    # Formule corrigée de fiabilité (R(t) = e^(-t/MTBF))
    df['Fiabilité'] = np.exp(-df['TBF (h)'] * (df['Taux de défaillance (%)']/ 100))
    
    # Disponibilité en pourcentage
    df['Disponibilité (%)'] = (df['MTBF'] / (df['MTBF'] + df['MTTR'])) * 100
    
    # Arrondir les valeurs
    df = df.round({
        'MTTR': 2,
        'MTBF': 2,
        'Taux de défaillance (%)': 2,
        'Fiabilité': 4,
        'Disponibilité (%)': 2
    })
    
    return df

# 3. Génération de l'image du tableau
def generate_table_image(df, output_img):
    plt.figure(figsize=(12, 8))
    plt.axis('off')
    
    # Création du tableau avec tabulate
    table = tabulate(df, headers='keys', tablefmt='grid', showindex=False, numalign='center')
    
    # Affichage du tableau
    plt.text(0, 1, table, fontfamily='monospace', fontsize=10, va='top')
    plt.tight_layout()
    plt.savefig(output_img, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Image du tableau générée: {output_img}")

# 4. Sauvegarde du nouveau fichier Excel
def save_new_excel(df, output_file):
    try:
        # Réorganiser les colonnes pour une meilleure lisibilité
        cols_order = ['Ligne ', 'To (h)', 'Ta (h)', 'Nombre des pannes', 
                     'MTTR', 'MTBF', 'Taux de défaillance (%)',
                     'Fiabilité', 'Disponibilité (%)']
        df = df[cols_order]
        
        df.to_excel(output_file, index=False)
        print(f"Nouveau fichier Excel généré: {output_file}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier Excel: {str(e)}")

# Exécution principale
if __name__ == "__main__":
    # Paramètres
    input_file = "output/lignes.xlsx"  # Fichier Excel d'entrée
    output_file = "donnees_analyse_maintenance.xlsx"  # Fichier Excel de sortie
    output_img = "tableau_analyse_maintenance.png"  # Image du tableau
    
    # Traitement
    df = import_data(input_file)
    if df is not None:
        df = calculate_indicators(df)
        generate_table_image(df, output_img)
        save_new_excel(df, output_file)
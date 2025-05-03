import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import sys

def load_and_filter_data(machines_file, zones_file):
    """Charge et filtre les machines des lignes Zone A"""
    try:
        print("\n=== Chargement des fichiers ===")
        # Charger les fichiers avec dtype pour éviter les conversions automatiques
        df_machines = pd.read_excel(machines_file, engine='openpyxl')
        df_zones = pd.read_excel(zones_file, engine='openpyxl')
        
        # Debug: afficher les colonnes et échantillons
        print("\nColonnes dans machines:", df_machines.columns.tolist())
        print("3 premières lignes machines:\n", df_machines.head(3))
        print("\nColonnes dans zones:", df_zones.columns.tolist())
        print("3 premières lignes zones:\n", df_zones.head(3))

        # Normaliser les noms de colonnes
        df_machines = df_machines.rename(columns={
            'Parent asset ': 'Ligne',
            'Asset Name': 'Machine',
            'Total Time (h)': 'Ta (h)'
        })

        # Nettoyage approfondi des noms de ligne
        df_machines['Ligne'] = (df_machines['Ligne']
                               .astype(str)
                               .str.upper()
                               .str.replace('S3PEUS', 'S03PES')
                               .str.replace(' ', '')
                               .str.strip())
        
        df_zones['Ligne'] = (df_zones['Ligne']
                            .astype(str)
                            .str.upper()
                            .str.replace('S3PEUS', 'S03PES')
                            .str.replace(' ', '')
                            .str.strip())

        print("\nValeurs uniques Lignes (machines):", df_machines['Ligne'].unique())
        print("Valeurs uniques Lignes (zones):", df_zones['Ligne'].unique())

        # Fusion en gardant toutes les machines pour debug
        df_merged = pd.merge(df_machines, df_zones, on='Ligne', how='left')
        
        # Debug après merge
        print("\nAprès merge - Valeurs manquantes Zone:", df_merged['Zone'].isna().sum())
        print("Zones distribuées:", df_merged['Zone'].value_counts(dropna=False))

        # Filtrer uniquement les machines Zone A
        machines_zone_a = df_merged[df_merged['Zone'] == 'A'].copy()
        
        if machines_zone_a.empty:
            # Debug avancé
            missing_zones = df_merged[df_merged['Zone'].isna()]
            print("\nDebug - Machines sans zone correspondante:")
            print(missing_zones[['Machine', 'Ligne']].to_markdown(index=False))
            
            zone_a_lignes = df_zones[df_zones['Zone'] == 'A']['Ligne'].unique()
            print("\nLignes Zone A dans fichier zones:", zone_a_lignes)
            
            raise ValueError("Aucune machine ne correspond aux lignes Zone A. Voir debug ci-dessus.")
        
        print(f"\n=== {len(machines_zone_a)} machines Zone A trouvées ===")
        return machines_zone_a
    
    except Exception as e:
        print(f"\nERREUR: {str(e)}", file=sys.stderr)
        return None

def apply_pareto_analysis(df, output_file):
    """Applique l'analyse Pareto et génère les résultats"""
    try:
        print("\n=== Analyse Pareto ===")
        # Préparation des données
        pareto_df = df.sort_values('Ta (h)', ascending=False)
        pareto_df['Cumul'] = pareto_df['Ta (h)'].cumsum()
        total_ta = pareto_df['Ta (h)'].sum()
        pareto_df['% cumulé'] = (pareto_df['Cumul'] / total_ta) * 100
        
        # Identification des machines critiques (80%)
        pareto_df['Criticité'] = pareto_df['% cumulé'].apply(
            lambda x: 'A' if x <= 80 else 'BC')
        
        # Export des résultats
        cols = ['Machine', 'Ligne', 'Ta (h)', 'Cumul', '% cumulé', 'Criticité']
        pareto_df[cols].to_excel(output_file, index=False)
        
        print(f"Résultats exportés vers {output_file}")
        return pareto_df
    
    except Exception as e:
        print(f"ERREUR dans Pareto: {str(e)}", file=sys.stderr)
        return None

def create_pareto_chart(df, image_file):
    """Crée et sauvegarde le diagramme de Pareto"""
    try:
        print("\n=== Création du diagramme ===")
        plt.style.use('ggplot')
        fig, ax1 = plt.subplots(figsize=(16, 8))
        
        # Tri des données
        df_sorted = df.sort_values('Ta (h)', ascending=False)
        
        # Configuration des couleurs
        colors = df_sorted['Criticité'].map({'A': '#d62728', 'BC': '#1f77b4'})
        
        # Barres (temps d'arrêt)
        bars = ax1.bar(
            df_sorted['Machine'], 
            df_sorted['Ta (h)'], 
            color=colors,
            width=0.7
        )
        
        # Configuration des axes
        ax1.set_xlabel('Machines', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Temps d\'arrêt (h)', fontsize=12, fontweight='bold')
        plt.xticks(
            rotation=45, 
            ha='right',
            fontsize=10,
            rotation_mode='anchor'
        )
        
        # Courbe (% cumulé)
        ax2 = ax1.twinx()
        line, = ax2.plot(
            df_sorted['Machine'], 
            df_sorted['% cumulé'], 
            color='#ff7f0e', 
            marker='D', 
            ms=5, 
            linewidth=2.5,
            markeredgecolor='black'
        )
        
        ax2.set_ylabel('% Cumulé', color='#ff7f0e', fontsize=12, fontweight='bold')
        ax2.yaxis.set_major_formatter(PercentFormatter())
        ax2.grid(False)
        
        # Seuil des 80%
        ax2.axhline(
            y=80, 
            color='#2ca02c', 
            linestyle=':', 
            linewidth=2, 
            alpha=0.7
        )
        ax2.text(
            len(df_sorted)*0.95, 
            81, 
            'Seuil 80%', 
            color='#2ca02c', 
            fontsize=11,
            ha='right'
        )
        
        # Titre et légende
        plt.title(
            'Analyse Pareto - Machines Critiques (Zone A)\n', 
            pad=20, 
            fontsize=14, 
            fontweight='bold',
            loc='left'
        )
        
        legend_elements = [
            plt.Rectangle((0,0), 1, 1, fc='#d62728', edgecolor='none', label='Critique (A)'),
            plt.Rectangle((0,0), 1, 1, fc='#1f77b4', edgecolor='none', label='Non-critique (BC)'),
            plt.Line2D([0], [0], color='#ff7f0e', marker='D', lw=2.5, label='% Cumulé'),
            plt.Line2D([0], [0], color='#2ca02c', linestyle=':', lw=2, label='Seuil 80%')
        ]
        
        plt.legend(
            handles=legend_elements,
            loc='lower center',
            bbox_to_anchor=(0.5, -0.35),
            ncol=4,
            frameon=True,
            fontsize=10
        )
        
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.25)
        
        # Sauvegarde
        plt.savefig(
            image_file, 
            dpi=300, 
            bbox_inches='tight',
            facecolor='white'
        )
        print(f"Diagramme sauvegardé: {image_file}")
        
        # Titre et légende
        plt.title('Diagramme de Pareto - Lignes de pesage', 
             pad=20, fontsize=14, fontweight='bold')

        legend_elements = [
            plt.Rectangle((0,0), 1, 1, fc='#1f77b4', edgecolor='none'),
            plt.Rectangle((0,0), 1, 1, fc='#d62728', edgecolor='none'),
            plt.Line2D([0], [0], color='#ff7f0e', marker='o', linewidth=2.5),
            plt.Line2D([0], [0], color='#2ca02c', linestyle='--', linewidth=1.5)
        ]

        plt.legend(legend_elements, 
                ['Temps d\'arrêt (h)', 'Ligne prioritaires (≤80%)', 
                    '% Cumulé', 'Seuil 80%'],
                loc='upper left', framealpha=1)

        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()
        plt.close()
        
    except Exception as e:
        print(f"ERREUR dans création graphique: {str(e)}", file=sys.stderr)

def generate_report(df):
    """Génère un rapport détaillé"""
    try:
        critical = df[df['Criticité'] == 'A']
        total_ta = df['Ta (h)'].sum()
        
        print("\n=== RAPPORT FINAL ===")
        print(f"• Machines analysées: {len(df)}")
        print(f"• Machines critiques (A): {len(critical)}")
        print(f"• Temps d'arrêt total: {total_ta:.2f} heures")
        print(f"• Temps d'arrêt critique: {critical['Ta (h)'].sum():.2f} heures ({critical['Ta (h)'].sum()/total_ta*100:.1f}%)")
        
        print("\nTOP 5 MACHINES CRITIQUES:")
        print(critical[['Machine', 'Ligne', 'Ta (h)', '% cumulé']]
              .head(5)
              .to_markdown(index=False, floatfmt=".2f"))
        
    except Exception as e:
        print(f"ERREUR dans génération rapport: {str(e)}", file=sys.stderr)

def main():
    # Configuration
    config = {
        'machines_file': "output/machines.xlsx",
        'zones_file': "output/zones_lignes.xlsx",
        'output_excel': "resultats_pareto.xlsx",
        'output_image': "diagramme_pareto.png"
    }
    
    print("=== DÉBUT DU TRAITEMENT ===")
    
    # 1. Chargement et filtrage
    machines_zone_a = load_and_filter_data(config['machines_file'], config['zones_file'])
    if machines_zone_a is None:
        sys.exit(1)
    
    # 2. Analyse Pareto
    pareto_result = apply_pareto_analysis(machines_zone_a, config['output_excel'])
    if pareto_result is None:
        sys.exit(1)
    
    # 3. Création du diagramme
    create_pareto_chart(pareto_result, config['output_image'])
    
    # 4. Rapport final
    generate_report(pareto_result)
    
    print("\n=== TRAITEMENT TERMINÉ AVEC SUCCÈS ===")

if __name__ == "__main__":
    main()
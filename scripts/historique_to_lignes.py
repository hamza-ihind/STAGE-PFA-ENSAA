import pandas as pd

def process_excel_data(input_path: str, output_path: str):
    sheets = pd.read_excel(input_path, sheet_name=["Lignes", "Arrêts"])

    # === Calcul de "To" Total des lignes de pesage (converti en heures) ===
    df_lignes = sheets['Lignes']
    filtered_lignes = df_lignes[
        (df_lignes['Station'] == 'STATION03') &
        (df_lignes["Ligne "].str.contains('PEUS', na=False))
    ]
    agg_lignes = (
        filtered_lignes
        .groupby('Ligne ')['MIN']
        .sum()
        .reset_index()
        .rename(columns={'MIN': 'To (h)'})
    )
    # Conversion minutes -> heures
    agg_lignes['To (h)'] = agg_lignes['To (h)'] / 60

    # === Calcul de "Ta" Total et nombre de pannes (converti en heures) ===
    df_arrets = sheets['Arrêts']
    motifs_selectionnes = [
        "Panne Machine Signée",
        "Panne Machine Non Signée"
    ]
    
    filtered_arrets = df_arrets[
        (df_arrets['Station'] == 'STATION03') &
        (df_arrets['Lignes'].str.contains('S3PEUS', na=False)) &
        (df_arrets['Motifs D\'arrets'].isin(motifs_selectionnes))
    ]
    
    # Calcul du temps d'arrêt total et du nombre de pannes
    agg_arrets = (
        filtered_arrets
        .groupby('Lignes')
        .agg(
            Ta=('Durée DT', 'sum'),
            Nb_pannes=('Durée DT', 'count')
        )
        .reset_index()
        .rename(columns={
            'Lignes': 'Ligne ',
            'Ta': 'Ta (h)',
            'Nb_pannes': 'Nombre des pannes'
        })
    )
    # Conversion minutes -> heures
    agg_arrets['Ta (h)'] = agg_arrets['Ta (h)'] / 60

    # === Combiner les résultats ===
    final_result = pd.merge(agg_lignes, agg_arrets, on='Ligne ', how='outer')
    
    # Remplacer les NaN par 0 pour les lignes sans arrêts des motifs sélectionnés
    final_result['Ta (h)'] = final_result['Ta (h)'].fillna(0)
    final_result['Nombre des pannes'] = final_result['Nombre des pannes'].fillna(0).astype(int)

    # Arrondir à 2 décimales pour les heures
    final_result['To (h)'] = final_result['To (h)'].round(2)
    final_result['Ta (h)'] = final_result['Ta (h)'].round(2)

    # Export to Excel
    final_result.to_excel(output_path, index=False)

    return final_result


result = process_excel_data("input/data_lignes.xlsx", "output/lignes.xlsx")
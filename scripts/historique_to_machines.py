import pandas as pd

def process_machine_data(input_path: str, output_path: str):
    df = pd.read_excel(input_path)
    
    # Filtrer les machines de pesage
    filtered_data = df[
        (df['Ligne'].str.startswith('S03PES', na=False)) &
        (df['Machine'].str.startswith('M-S03-Pes', na=False))
    ].copy()
    
    # Grouper par machine et sommer le temps, en conservant le Parent asset
    result = (
        filtered_data
        .groupby(['Machine', 'Ligne'])['Ta (h)']
        .sum().reset_index().rename(columns={'Ta (h)': 'Ta (h)', 'Machine': 'Machine', 'Ligne': 'Ligne'})
    )
    
    # Exporter vers Excel
    result.to_excel(output_path, index=False)
    
    return result

# Exécution du traitement
result = process_machine_data("input/data_machines.xlsx", "output/machines.xlsx")
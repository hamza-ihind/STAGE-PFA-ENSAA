import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# 1. Chargement des données
try:
    df = pd.read_excel("output/lignes.xlsx")
except UnicodeDecodeError:
    df = pd.read_excel("output/lignes.xlsx")

# 2. Préparation des données pour Pareto
df_sorted = df.sort_values(by="Ta (h)", ascending=False)
df_sorted['Cumul'] = df_sorted['Ta (h)'].cumsum()
total_ta = df_sorted['Ta (h)'].sum()
df_sorted['% cumulé'] = (df_sorted['Cumul'] / total_ta) * 100

# 3. Identification des lignes critiques (80%)
critical_lines = df_sorted[df_sorted['% cumulé'] <= 80]
if len(critical_lines) == len(df_sorted):  # Si tout est critique
    critical_lines = df_sorted.iloc[:int(len(df_sorted)*0.8)]

# 4. Création du fichier Zones
zone_data = []
for _, row in df_sorted.iterrows():
    ligne = row['Ligne ']
    zone = "A" if row['% cumulé'] <= 80 else "BC"
    zone_data.append({'Ligne': ligne, 'Zone': zone})

zone_df = pd.DataFrame(zone_data)
zone_output_path = "output/zones_lignes.xlsx"
zone_df.to_excel(zone_output_path, index=False)
print(f"Fichier des zones généré : {zone_output_path}")

# 5. Création du diagramme de Pareto (inchangé)
plt.style.use('ggplot')
fig, ax1 = plt.subplots(figsize=(14, 7))

# Barres (temps d'arrêt)
bars = ax1.bar(df_sorted['Ligne '], df_sorted['Ta (h)'], color='#1f77b4')
# Colorier les barres critiques
for i, bar in enumerate(bars):
    if i < len(critical_lines):
        bar.set_color('#d62728')

ax1.set_xlabel('Ligne ', fontsize=12, fontweight='bold')
ax1.set_ylabel('Temps d\'arrêt (h)', color='#1f77b4', fontsize=12, fontweight='bold')
ax1.tick_params(axis='y', labelcolor='#1f77b4')
plt.xticks(rotation=45, ha='right', fontsize=10)

# Courbe (% cumulé)
ax2 = ax1.twinx()
line, = ax2.plot(df_sorted['Ligne '], df_sorted['% cumulé'], 
                 color='#ff7f0e', marker='o', ms=6, linewidth=2.5)
ax2.set_ylabel('% Cumulé', color='#ff7f0e', fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor='#ff7f0e')
ax2.yaxis.set_major_formatter(PercentFormatter())

# Ligne des 80% et annotation
ax2.axhline(y=80, color='#2ca02c', linestyle='--', linewidth=1.5, alpha=0.7)
ax2.text(len(df_sorted)-0.5, 81, 'Seuil 80%', color='#2ca02c', fontsize=10)

# Point d'intersection
intersect_idx = (df_sorted['% cumulé'] >= 80).idxmax()
if pd.notna(intersect_idx):
    ax2.plot(intersect_idx, df_sorted.loc[intersect_idx, '% cumulé'], 
            'o', markersize=8, color='#d62728', alpha=0.7)
    ax2.annotate(f"{df_sorted.loc[intersect_idx, 'Ligne ']}: {df_sorted.loc[intersect_idx, '% cumulé']:.1f}%",
                xy=(intersect_idx, df_sorted.loc[intersect_idx, '% cumulé']),
                xytext=(10, -20), textcoords='offset points',
                arrowprops=dict(arrowstyle="->", color='#d62728'),
                bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8),
                fontsize=9)

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
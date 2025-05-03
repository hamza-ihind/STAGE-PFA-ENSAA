import pandas as pd
import numpy as np
from math import log, exp
from config.gravity_keywords import GRAVITY_WEIGHTS
from config.frequency_keywords import FREQUENCY_WEIGHTS
from config.detect_keywords import DETECT_WEIGHTS

class AMDEXCalculator:
    def __init__(self):
        # Chargement des pondérations
        self.gravity_weights = GRAVITY_WEIGHTS
        self.frequency_weights = FREQUENCY_WEIGHTS
        self.detect_weights = DETECT_WEIGHTS
        
        # Paramètres de calibration
        self.mttr_ref = 2.0  # Valeur de référence MTTR (heures)
        self.failure_rate_ref = 0.01  # Taux de défaillance de référence

    def load_data(self, keywords_path, kpi_path):
        """Charge et fusionne les données"""
        keywords_df = pd.read_excel(keywords_path)
        kpi_df = pd.read_excel(kpi_path)
        
        # Fusion sur la colonne 'Organe'
        return pd.merge(
            keywords_df, 
            kpi_df, 
            on='Organe', 
            how='inner'
        ).dropna()

    def calculate_gravity(self, row):
        """G = Moyenne pondérée des mots-clés * ln(1 + MTTR/MTTR_ref) + (Temps arrêt/Temps opérationnel)"""
        keywords = [w.split(':')[0] for w in row['Mots_clés'].split(', ')]
        scores = []
        
        for word in keywords:
            if word in self.gravity_weights:
                scores.append(self.gravity_weights[word])
        
        if not scores:
            avg_g = 1.0
        else:
            avg_g = np.mean(scores)
        
        time_impact = row['Temps_arrêt'] / row['Temps_operation']
        mttr_impact = log(1 + row['MTTR'] / self.mttr_ref)
        
        return min(10, avg_g * mttr_impact + time_impact)

    def calculate_frequency(self, row):
        """F = (1 - exp(-λt)) * (1 + moyenne F_keywords/10)"""
        lambda_val = row['Nombre_pannes'] / row['Temps_operation']
        prob_failure = 1 - exp(-lambda_val * 30)  # Sur 30 jours
        
        keywords = [w.split(':')[0] for w in row['Mots_clés'].split(', ')]
        f_scores = [self.frequency_weights.get(w, 1) for w in keywords]
        text_factor = 1 + (np.mean(f_scores) / 10) if f_scores else 1.0
        
        return min(10, prob_failure * text_factor)

    def calculate_detectability(self, row):
        """D = 10 - (α*Disponibilité + β*moyenne D_keywords)"""
        keywords = [w.split(':')[0] for w in row['Mots_clés'].split(', ')]
        d_scores = [self.detect_weights.get(w, 5) for w in keywords]
        text_factor = np.mean(d_scores) if d_scores else 5.0
        
        return max(1, 10 - (0.6*row['Disponibilité'] + 0.4*text_factor))

    def calculate_criticity(self, row):
        """C = G * F * D * (1 + Taux_défaillance/Taux_référence)"""
        G = row['Gravité']
        F = row['Fréquence']
        D = row['Détectabilité']
        failure_ratio = (row['Nombre_pannes']/row['Temps_operation']) / self.failure_rate_ref
        
        return G * F * D * (1 + min(failure_ratio, 3))  # Cap à 3x le taux de référence

    def run_analysis(self, keywords_path, kpi_path, output_path):
        """Exécute l'analyse complète"""
        try:
            # 1. Chargement des données
            df = self.load_data(keywords_path, kpi_path)
            
            # 2. Calcul des indicateurs
            df['Gravité'] = df.apply(self.calculate_gravity, axis=1)
            df['Fréquence'] = df.apply(self.calculate_frequency, axis=1)
            df['Détectabilité'] = df.apply(self.calculate_detectability, axis=1)
            df['Criticité'] = df.apply(self.calculate_criticity, axis=1)
            
            # 3. Post-traitement
            df['Priorité'] = pd.cut(
                df['Criticité'],
                bins=[0, 30, 100, float('inf')],
                labels=['Négligeable', 'Contrôle préventif', 'Action immédiate']
            )
            
            # 4. Export
            cols_to_export = [
                'Organe', 'Gravité', 'Fréquence', 'Détectabilité', 
                'Criticité', 'Priorité', 'MTTR', 'MTBF', 'Disponibilité',
                'Mots_clés'
            ]
            df[cols_to_export].to_excel(output_path, index=False)
            
            print(f"Analyse terminée. Résultats exportés dans {output_path}")
            return df
            
        except Exception as e:
            print(f"Erreur lors de l'analyse : {str(e)}")
            return None

# Exemple d'utilisation
if __name__ == "__main__":
    calculator = AMDEXCalculator()
    results = calculator.run_analysis(
        keywords_path="output/mots_cles_par_organe.xlsx",
        kpi_path="input/kpi_techniques.xlsx",
        output_path="output/resultats_amdex.xlsx"
    )
    
    if results is not None:
        print("\nAperçu des résultats :")
        print(results[['Organe', 'Criticité', 'Priorité']].head())
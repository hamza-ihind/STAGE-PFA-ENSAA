import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import defaultdict, Counter
import pandas as pd
import sys
from pathlib import Path

# Configuration des chemins
sys.path.append(str(Path(__file__).parent.parent))
from config.stopwords import STOPWORDS
from config.synonyms import SYNONYM_MAP

nltk.download(['stopwords', 'wordnet', 'punkt'], quiet=True)

class TextPreprocessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('french'))
        self.technical_stopwords = STOPWORDS
        self.synonyms = SYNONYM_MAP

    def clean_text(self, text):
        """Version optimisée avec gestion des erreurs"""
        if not isinstance(text, str) or not text.strip():
            return ""
            
        text = text.lower()
        for wrong, correct in self.synonyms.items():
            text = re.sub(rf'\b{wrong}\b', correct, text)
        
        text = re.sub(r'[^a-zéèêëàâäôöûüç\s-]', '', text)
        words = nltk.word_tokenize(text, language='french')
        
        return ' '.join(
            self.lemmatizer.lemmatize(word, pos='v') 
            for word in words
            if self._is_valid_word(word)
        )
    
    def _is_valid_word(self, word):
        """Filtre les mots selon les critères"""
        return (len(word) > 2 and 
                word not in self.stop_words and 
                word not in self.technical_stopwords)

class OrganeAnalyzer:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.organe_data = defaultdict(lambda: {
            'machines': set(),
            'lignes': set(),
            'keywords': Counter(),
            'total_ta': 0,
            'interventions': 0,
            'descriptions': []
        })

    def process_data(self, data_machines_path, pareto_result_path):
        """Traite les fichiers et génère le rapport des organes critiques"""
        try:
            # 1. Chargement des données
            df_machines = pd.read_excel(data_machines_path)
            df_pareto = pd.read_excel(pareto_result_path)
            
            print(f"\nFichier machines chargé: {len(df_machines)} interventions")
            print(f"Fichier Pareto chargé: {len(df_pareto)} machines critiques")
            
            # 2. Filtrer les machines critiques (Zone A)
            machines_critiques = df_pareto[df_pareto['Criticité'] == 'A']['Machine']
            df_filtre = df_machines[
                df_machines['Machine'].isin(machines_critiques) &
                df_machines['Ligne'].str.startswith("S03PES", na=False)
            ]
            
            print(f"Machines critiques trouvées: {len(df_filtre['Machine'].unique())}")
            print(f"Interventions analysées: {len(df_filtre)}")
            
            if len(df_filtre) == 0:
                raise ValueError("Aucune intervention trouvée pour les machines critiques")
            
            # 3. Traitement des données par organe
            for _, row in df_filtre.iterrows():
                organe = row['Organe']
                if pd.isna(organe):
                    continue
                
                # Mise à jour des métadonnées
                self.organe_data[organe]['machines'].add(row['Machine'])
                self.organe_data[organe]['lignes'].add(row['Ligne'])
                self.organe_data[organe]['total_ta'] += row.get('Ta (h)', 0)
                self.organe_data[organe]['interventions'] += 1
                
                # Traitement du texte
                description = str(row['Description'])
                self.organe_data[organe]['descriptions'].append(description)
                cleaned_text = self.preprocessor.clean_text(description)
                words = cleaned_text.split()
                self.organe_data[organe]['keywords'].update(words)
            
            # 4. Préparation des résultats
            results = []
            for organe, data in self.organe_data.items():
                # Texte combiné pour analyse globale
                full_text = ' '.join(data['descriptions'])
                cleaned_full_text = self.preprocessor.clean_text(full_text)
                
                results.append({
                    'Organe': organe,
                    'Lignes': ', '.join(sorted(data['lignes'])),
                    'Machines': ', '.join(sorted(data['machines'])),
                    'Nombre Machines': len(data['machines']),
                    'Temps Arrêt Total (h)': round(data['total_ta'], 2),
                    'Nombre Interventions': data['interventions'],
                    'Mots-clés Uniques': len(data['keywords']),
                    'Top 10 Mots-clés': ', '.join(
                        f"{word}({count})" for word, count in data['keywords'].most_common(10)
                    ),
                })
            
            # 5. Création du DataFrame final
            result_df = pd.DataFrame(results).sort_values(
                'Temps Arrêt Total (h)', ascending=False)
            
            return result_df
            
        except Exception as e:
            print(f"\nERREUR: {str(e)}", file=sys.stderr)
            return None

    def export_results(self, df, output_path):
        """Exporte les résultats vers Excel"""
        try:
            if df is None or len(df) == 0:
                raise ValueError("Aucune donnée à exporter")
            
            # Organisation des colonnes
            columns_order = [
                'Organe', 'Lignes', 'Machines', 'Nombre Machines',
                'Temps Arrêt Total (h)', 'Nombre Interventions',
                'Mots-clés Uniques', 'Top 10 Mots-clés',
            ]
            
            df[columns_order].to_excel(output_path, index=False)
            print(f"\nRésultats exportés avec succès vers: {output_path}")
            return True
            
        except Exception as e:
            print(f"\nERREUR export: {str(e)}", file=sys.stderr)
            return False

def main():
    # Configuration
    config = {
        'data_machines': "input/data_machines.xlsx",
        'pareto_result': "resultats_pareto_machines.xlsx",
        'output_file': "analyse_organes_critiques.xlsx"
    }
    
    print("=== DEBUT ANALYSE ORGANES CRITIQUES ===")
    
    # Initialisation
    analyzer = OrganeAnalyzer()
    
    # Traitement
    result_df = analyzer.process_data(
        config['data_machines'],
        config['pareto_result']
    )
    
    # Export
    if result_df is not None:
        success = analyzer.export_results(result_df, config['output_file'])
        
        if success:
            print("\n=== RESULTATS ===")
            print(f"Organes analysés: {len(result_df)}")
            print(f"Temps arrêt total: {result_df['Temps Arrêt Total (h)'].sum():.2f}h")
            
            print("\nAperçu des résultats:")
            print(result_df.head(3).to_markdown(index=False))
    
    print("\n=== TRAITEMENT TERMINE ===")

if __name__ == "__main__":
    main()
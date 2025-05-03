STOPWORDS = {
    # Termes techniques généraux
    'machine', 'peseuse', 'systeme', 'module', 'probleme',
    'etat', 'niveau', 'controle', 'panne', 'defaut',
    'equipement', 'dispositif', 'engin', 'appareil', 'unite',
    
    # Références temporelles
    'heure', 'jour', 'semaine', 'mois', 'annee', 'date',
    'moment', 'periode', 'duree', 'instant',

    # Verbes courants
    'avoir', 'etre', 'faire', 'mettre', 'prendre',
    'voir', 'dire', 'devoir', 'pouvoir', 'vouloir',
    
    # Termes de processus de maintenance
    'intervention', 'reparation', 'maintenance', 'depannage',
    'diagnostic', 'verification', 'inspection', 'test',
    'essai', 'controle', 'reglage', 'ajustement',
    
    # Termes organisationnels
    'atelier', 'poste', 'zone', 'ligne', 'secteur',
    'service', 'equipe', 'technicien', 'operateur',
    
    # Références documentaires
    'rapport', 'fiche', 'document', 'notice', 'manuel',
    'procedure', 'protocol', 'formulaire',
    
    # Unités de mesure
    'kg', 'gramme', 'tonne', 'newton', 'bar', 'psi',
    'volt', 'ampere', 'watt', 'celsius', 'pourcent',
    
    # Adjectifs courants
    'petit', 'grand', 'bon', 'mauvais', 'nouveau',
    'ancien', 'different', 'normal', 'anormal',

    # Connecteurs logiques
    'avec', 'sans', 'pour', 'dans', 'sur', 'sous',
    'vers', 'depuis', 'pendant',
    
    # Termes spécifiques au pesage
    'pesage', 'balance', 'cellule', 'charge', 'capacite',
    'precision', 'tarage', 'etalonnage', 'justesse'
}
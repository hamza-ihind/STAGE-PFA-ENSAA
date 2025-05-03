SYNONYM_MAP = {
    # Vibrations et bruits mécaniques
    'roulis': 'vibration',
    'tangage': 'vibration',
    'claquement': 'bruit_anormal',
    'cognement': 'impact',
    'grincement': 'frottement_sec',
    'sifflement': 'frottement_continu',
    
    # Problèmes thermiques
    'brulure': 'surchauffe',
    'echauffement': 'surchauffe_moderee',
    'sur_temp': 'surchauffe',
    't°_elevee': 'temperature_excessive',

    # Défauts électriques
    'hs': 'hors_service',
    'def_elect': 'defaut_electrique',
    'coup_circuit': 'court_circuit',
    'alim_instable': 'alimentation_instable',
    
    # Désalignements mécaniques
    'decallage': 'decalage',
    'desaxement': 'mauvais_alignement',
    'desalign': 'desalignement',
    'jeu_excessif': 'jeu_mecanique',

    # Blocages et coincements
    'grippage': 'blocage',
    'coincement': 'blocage_partiel',
    'serrage': 'blocage_par_contrainte',
    
    # Usure et corrosion
    'usure_accel': 'usure_acceleree',
    'patine': 'usure_superficielle',
    'corrod': 'corrosion',
    
    # Problèmes de mesure/capteurs
    'err_pesee': 'erreur_pesage',
    'dérive': 'derive_capteur',
    'cal_def': 'defaut_calibration',
    
    # États opérationnels
    'marche_irreg': 'fonctionnement_irregulier',
    'arret_brut': 'arret_brutal',
    'redem_err': 'erreur_redemarrage',
    
    # Défauts matériels
    'fiss_app': 'fissure_apparente',
    'deform': 'deformation',
    'cassure': 'rupture'
}
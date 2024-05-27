import json
import os
from settings import AppSettings

def sequences_reader():
    file_path = os.path.join(AppSettings.data_dir, 'sequences.json')
    with open(file_path, 'r') as file:
        sequences = json.load(file)
        return sequences

def sequences_writer(data):
    file_path = os.path.join(AppSettings.data_dir, 'sequences.json')
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        return "Séquence créée avec succés !"
    except FileNotFoundError:
        return "Le fichier 'sequences.json' n'a pas été trouvé"
    except PermissionError:
        return "Erreur : Permission refusée, impossible d'enregistrer le fichier"
    except TypeError:
        return "Erreur lors de la sérialisation des données au format JSON"
    except OSError:
        return "Espace disque insuffisant ou erreur du système d'exploitation"

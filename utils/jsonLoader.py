import json


def sequences_reader():
    with open('../data/sequences.json', 'r') as file:
        sequences = json.load(file)
        return sequences


def sequences_writer(data):
    try:
        with open('../data/sequences.json', 'w') as file:
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

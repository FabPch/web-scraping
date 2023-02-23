import csv
import requests

POST_URL = 'https://sig.ville.gouv.fr/recherche-adresses-qp-polville-v2019'
PRIORITAIRE = 'adresse recherchée est située dans le quartier prioritaire'
NON_PRIORITAIRE = 'est pas située dans un quartier prioritaire'
NON_TROUVE = 'Aucune voie correspondante pour cette recherche'

def get_adresse_info(adresse):
    payload = {
        'num_adresse': adresse['num_adresse'],
        'nom_voie': adresse['nom_voie'],
        'nom_commune': adresse['nom_commune'],
        'code_postal': adresse['code_postal'],
    }
    response = requests.post(POST_URL, data=payload)
    response.encoding = 'utf-8'
    return response.json()

def print_adresse_info(adresse_info, adresse):
    if PRIORITAIRE in adresse_info['fullResponseTpl']:
        print('zone prioritaire pour', adresse['nom_commune'])
    elif NON_PRIORITAIRE in adresse_info['fullResponseTpl']:
        print('zone non prioritaire pour', adresse['nom_commune'])
    elif NON_TROUVE in adresse_info['fullResponseTpl']:
        print('non trouvé pour', adresse['nom_commune'])
    else:
        print('autre chose pour', adresse['nom_commune'])

def main():
    with open('adresses.csv', encoding='utf-8') as adresses_file:
        reader = csv.DictReader(adresses_file, delimiter=',')
        for adresse in reader:
            adresse_info = get_adresse_info(adresse)
            print_adresse_info(adresse_info, adresse)

if __name__ == '__main__':
    main()

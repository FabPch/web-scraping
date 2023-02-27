import csv
import requests
import pandas as pd

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

# if __name__ == '__main__':
#     main()

def read_excel_file(file_name):
    use_cols = ['Organisation - Numéro de maison', 'Organisation - Nom de rue/route', 'Organisation - Ville/agglomération/village/localité', 'Organisation - Code postal']

    df = pd.read_excel(file_name, usecols=use_cols, dtype=str)

    new_col_names =  {
        use_cols[0]: 'num_adresse'
        , use_cols[1]: 'nom_voie'
        , use_cols[2]: 'nom_commune'
        , use_cols[3]: 'code_postal'
    }

    df_renamed = df.rename(mapper=new_col_names, axis=1)

    df_with_json_payload = df_renamed.apply(lambda x: x.to_json(), axis=1)
    print(df_with_json_payload.head(10))

read_excel_file('organizations-11557216-596.xlsx')
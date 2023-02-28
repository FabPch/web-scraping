import requests
import pandas as pd

POST_URL = 'https://sig.ville.gouv.fr/recherche-adresses-qp-polville-v2019'
PRIORITAIRE = 'adresse recherchée est située dans le quartier prioritaire'
NON_PRIORITAIRE = 'est pas située dans un quartier prioritaire'
NON_PRIORITAIRE_2 = 'abrite pas de quartiers prioritaires'
NON_PRIORITAIRE_3 = 'pas de lien avec un quartier prioritaire'
NON_TROUVE = 'Aucune voie correspondante pour cette recherche'
NON_TROUVE_2 = 'Veuillez précisez le numéro recherché dans la voie'
FILE_NAME = 'organizations-11557216-596.xlsx'

def get_adresse_info(adresse):
    payload = {
        'num_adresse': adresse['Organisation - Numéro de maison'],
        'nom_voie': adresse['Organisation - Nom de rue/route'],
        'nom_commune': adresse['Organisation - Ville/agglomération/village/localité'],
        'code_postal': adresse['Organisation - Code postal'],
    }
    response = requests.post(POST_URL, data=payload)
    response.raise_for_status()
    response.encoding = 'utf-8'
    return response.json()

def is_in_quartier_prioritaire(adresse_info, adresse):
    info = adresse_info['fullResponseTpl']
    nom_commune = adresse['Organisation - Ville/agglomération/village/localité']

    if PRIORITAIRE in info:
        return 'True'
    elif (NON_PRIORITAIRE in info) | (NON_PRIORITAIRE_2 in info) | (NON_PRIORITAIRE_3 in info):
        return 'False'
    elif (NON_TROUVE in info) | (NON_TROUVE_2 in info):
        return 'Non trouvé'
    else:
        print('autre chose pour', nom_commune)
        # print(adresse_info['fullResponseTpl'])
        return 'Presque...'

def main():
    df = pd.read_excel(FILE_NAME, dtype=str)

    print(f'row count: {len(df.index)}')

    for index, adresse in df.iterrows():
        try:
            adresse_info = get_adresse_info(adresse)
            result = is_in_quartier_prioritaire(adresse_info, adresse)
            df.loc[index, 'is_in_quartier_prioritaire'] = result
        except Exception as err:
            print(err)
            df.loc[index, 'is_in_quartier_prioritaire'] = 'Non trouvé'
    
    num_non_trouvées = (df['is_in_quartier_prioritaire'] == 'Non trouvé').sum()
    print(f'Nombre adresses non trouvées: {num_non_trouvées}')

    df.to_excel('response.xlsx', index=False)

if __name__ == '__main__':
    main()

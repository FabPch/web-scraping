import requests
import pandas as pd

POST_URL = 'https://sig.ville.gouv.fr/recherche-adresses-qp-polville-v2019'

PRIORITAIRE = 'adresse recherchée est située dans le quartier prioritaire'
NON_PRIORITAIRE = 'est pas située dans un quartier prioritaire'
NON_PRIORITAIRE_2 = 'abrite pas de quartiers prioritaires'
NON_PRIORITAIRE_3 = 'pas de lien avec un quartier prioritaire'
NON_PRIORITAIRE_4 = 'adresse recherchée est située dans la ZFU'
NON_TROUVE = 'Aucune voie correspondante pour cette recherche'
NON_TROUVE_2 = 'Veuillez précisez le numéro recherché dans la voie'
NON_TROUVE_3 = 'Choisissez une commune parmi la liste'
NON_TROUVE_4 = 'Nous ne sommes pas en mesure de pr'

FILE_NAME = 'organizations-11557216-596.xlsx'
FILE_NAME_ANSWER = 'response.xlsx'

def get_adresse_info(adresse):
    """
    Send web POST request with school adresse as payload.
    Receive information about the location (is in priority zone ?) 
    """
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
    """
    From web response content, determine if the school is in a priority zone.
    (Several different answers are expected, even for the same result)
    
    If the different answers do not appear in the response, a file is written
    with the web response content. Then it can be analyzed manually later, in order
    to add another possible answer.
    """
    info = adresse_info['fullResponseTpl']
    nom_commune = adresse['Organisation - Ville/agglomération/village/localité']

    if PRIORITAIRE in info:
        return 'True'
    elif any(non_pr in info for non_pr in [NON_PRIORITAIRE, NON_PRIORITAIRE_2, NON_PRIORITAIRE_3, NON_PRIORITAIRE_4]):
        return 'False'
    elif any(non_tr in info for non_tr in[NON_TROUVE, NON_TROUVE_2, NON_TROUVE_3, NON_TROUVE_4]):
        return 'Non trouvé'
    else:
        with open(f'info-{nom_commune}', 'w') as file:
            file.write(info)
        print('autre chose pour', nom_commune)
        return 'Presque...'

def main():
    """
    Iterate on each row from Excel file:
        1. Get adresse information from Excel content
        2. Send web request with the adresse to get more information about the location
        3. From the web response, determine if the adresse is in priority zone
        4. Write Excel file with the new column is_in_quartier_prioritaire
    """
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

    df.to_excel(FILE_NAME_ANSWER, index=False)

if __name__ == '__main__':
    main()

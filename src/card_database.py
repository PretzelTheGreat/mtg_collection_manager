import os
from src import util_funcs
from datetime import date as date

def construct_card_database():
    # this should only be run once a week
    # the data in AllIdentifers.json from https://mtgjson.com/ will be reformatted
    # to fit a better data storage style for my program, while maintaining most of the data
    # that comes with the file.

    # first download the file, if a download for today does not exist
    today = date.today()
    filename = f"AllIdentifiers_{today.isoformat()}.json"
    zipfile_name = f"AllIdentifiers_{today.isoformat()}.json.zip"
    download_url = 'https://mtgjson.com/api/v5/AllIdentifiers.json.zip'
    if filename not in os.listdir('resources/mtgjson_data'):
        util_funcs.download_file_from_url(download_url, zipfile_name)
        util_funcs.unzip_file_to_loc(f'resources/tmp/{zipfile_name}', 'resources/mtgjson_data')
        os.system(f'move resources\\mtgjson_data\\AllIdentifiers.json resources\\mtgjson_data\\{filename}')

    # next, create the databse from the data
    card_database = {}
    keys = ['availability', 'colorIdentity', 'colors', 'convertedManaCost', 'keywords', 'layout', 
            'legalities', 'manaCost', 'manaValue', 'name', 'number', 'originalText', 'originalType', 'power',
            'rarity', 'rulings', 'subtypes', 'supertypes', 'text', 'toughness', 'type', 'types']
    
    cards_by_identifiers = util_funcs.import_json_file(f'resources/mtgjson_data/{filename}')

    for uuid, data in cards_by_identifiers['data'].items():
        setCode = data['setCode']
        name = data['name']
        filtered_keys = {k:v for k, v in data.items() if k in keys}

        if name not in card_database.keys():
            filtered_keys['uuids'] = {setCode: uuid}
            card_database[name] = filtered_keys

        else:
            card_database[name]['uuids'][setCode] = uuid

    util_funcs.export_json_file('resources/databases/card_database.json', card_database)


def load_card_database():
    filename = 'card_database.json'
    metadata = util_funcs.import_json_file("resources/database_update_metadata.json")
    if filename not in os.listdir('resources/databases') or date.fromisoformat(metadata["card_database"]) < date.today():
        construct_card_database()
        metadata["card_database"] = date.today().isoformat()
        util_funcs.export_json_file("resources/database_update_metadata.json", metadata)

    return util_funcs.import_json_file(f"resources/databases/{filename}")
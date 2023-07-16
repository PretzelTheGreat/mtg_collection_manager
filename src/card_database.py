import os
import platform
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
        if platform.system() == "Windows":
            os.system(f'move resources\\mtgjson_data\\AllIdentifiers.json resources\\mtgjson_data\\{filename}')
        elif platform.system() == "Linux":
            os.system(f'mv resources/mtgjson_data/AllIdentifiers.json resources/mtgjson_data/{filename}')

    # next, create the databse from the data
    # in this step the 'number' field is renamed to setNumber, because number is too ambiguous,
    # and doesn't indicate what it's related to
    card_database = {}
    keys = ['availability', 'colorIdentity', 'colors', 'convertedManaCost', 'keywords', 'layout', 
            'legalities', 'manaCost', 'manaValue', 'name', 'number', 'originalText', 'originalType', 'power',
            'rarity', 'rulings', 'subtypes', 'supertypes', 'text', 'toughness', 'type', 'types']
    
    cards_by_identifiers = util_funcs.import_json_file(f'resources/mtgjson_data/{filename}')

    for uuid, data in cards_by_identifiers['data'].items():
        setCode = data['setCode']
        name = data['name']
        filtered_keys = {k:v for k, v in data.items() if k in keys}
        filtered_keys['setNumber'] = filtered_keys['number']
        void = filtered_keys.pop('number')

        if name not in card_database.keys():
            filtered_keys['uuids'] = {setCode: {filtered_keys['setNumber']: uuid}}
            card_database[name] = filtered_keys

        else:
            if setCode not in card_database[name]['uuids']:
                card_database[name]['uuids'][setCode] = {filtered_keys['setNumber']: uuid}
            else:
                card_database[name]['uuids'][setCode][filtered_keys['setNumber']] = uuid

    util_funcs.export_json_file('resources/databases/card_database.json', card_database)


def load_card_database():
    filename = 'card_database.json'
    metadata = util_funcs.import_json_file("resources/tmp/database_update_metadata.json")
    if filename not in os.listdir('resources/databases') or date.fromisoformat(metadata["card_database"]) < date.today():
        construct_card_database()
        metadata["card_database"] = date.today().isoformat()
        util_funcs.export_json_file("resources/tmp/database_update_metadata.json", metadata)

    return util_funcs.import_json_file(f"resources/databases/{filename}")
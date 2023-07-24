import os
import re
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
        setNumber = filtered_keys['number']
        void = filtered_keys.pop('number')

        if name not in card_database.keys():
            filtered_keys['uuids'] = {setCode: {setNumber: uuid}}
            card_database[name] = filtered_keys

        else:
            if setCode not in card_database[name]['uuids']:
                card_database[name]['uuids'][setCode] = {setNumber: uuid}
            else:
                card_database[name]['uuids'][setCode][setNumber] = uuid

    util_funcs.export_json_file('resources/databases/card_database.json', card_database)


def load_card_database():
    filename = 'card_database.json'
    metadata = util_funcs.import_json_file("resources/tmp/database_update_metadata.json")
    if filename not in os.listdir('resources/databases') or date.fromisoformat(metadata["card_database"]) < date.today():
        construct_card_database()
        metadata["card_database"] = date.today().isoformat()
        util_funcs.export_json_file("resources/tmp/database_update_metadata.json", metadata)

    return util_funcs.import_json_file(f"resources/databases/{filename}")

def generate_validation_files(database):
    # this will generate all the temporary files that are used for validating the 
    # search criteria input by the user
    # this function is configured to check if the file already exists before writing data
    types_file_found = True if 'types_key_results.txt' in os.listdir('resources/tmp') else False
    subtypes_file_found = True if 'subtypes_key_results.txt' in os.listdir('resources/tmp') else False
    supertypes_file_found = True if 'supertypes_key_results.txt' in os.listdir('resources/tmp') else False
    keywords_file_found = True if 'keywords_results.txt' in os.listdir('resources/tmp') else False
        
    subtypes_key = []
    supertypes_key = []
    types_key = []
    keywords = []

    for card in database.values():
        for t in card['types']:
            if t not in types_key:
                types_key.append(t)

        for t in card['subtypes']:
            if t not in subtypes_key:
                subtypes_key.append(t)

        for t in card['supertypes']:
            if t not in supertypes_key:
                supertypes_key.append(t)

        if 'keywords' in card.keys():
            for keyword in card['keywords']:
                if keyword not in keywords:
                    keywords.append(keyword)

    if not types_file_found:
        util_funcs.export_text_file('resources/tmp/types_key_results.txt', types_key)
    
    if not subtypes_file_found:
        util_funcs.export_text_file('resources/tmp/subtypes_key_results.txt', subtypes_key)

    if not supertypes_file_found:
        util_funcs.export_text_file('resources/tmp/supertypes_key_results.txt', supertypes_key)
    
    if not keywords_file_found:
        util_funcs.export_text_file('resources/tmp/keywords_results.txt', keywords)

def parse_search_string(search_string):
    # this function will take in user input string, that contains a key:value fields separated by spaces
    # and will convert it to key:value with the keys matching the database keys, returning a dict with 
    # the desired search criteria
    # database_keys = ['availability', 'colorIdentity', 'colors', 'convertedManaCost', 'keywords', 'layout', 
    #                  'legalities', 'manaCost', 'manaValue', 'name', 'number', 'originalText', 'originalType', 'power',
    #                  'rarity', 'rulings', 'subtypes', 'supertypes', 'text', 'toughness', 'type', 'types']

    # the format of search string should look like this
    # name:[card name]
    # rty:[rarity] col:[colors]

    # find all quoted substrings within the main string
    # and then iterate over regex search results to convert spaces in the quotes
    # to underscores, replacing the original text in the search string
    key_value_pairs = re.compile(r'([\w]+:(?:(?:[\w]+|"[\w\W\s]*?")(?:,)?)+)')
    result = key_value_pairs.findall(search_string)

    # these keys require specific input so it will be validated against the following criteria
    validation_criteria = {'rarity': ["common", "uncommon", "rare", "mythic"], 
                           'colors': ['W', 'U', 'B', 'R', 'G'], 
                           'colorIdentity': ['W', 'U', 'B', 'R', 'G'],
                           'manaCost': r'(\{(?:[WUBRG](?:\/[WUBRGP])?|[0-9]|X)\}+)',
                           'legalities': ["Legal", "Restricted", "Illegal"],
                           'keywords': util_funcs.import_text_file('resources/tmp/keywords_results.txt'),
                           'types': util_funcs.import_text_file('resources/tmp/types_key_results.txt'),
                           'subtypes': util_funcs.import_text_file('resources/tmp/subtypes_key_results.txt'),
                           'supertypes': util_funcs.import_text_file('resources/tmp/supertypes_key_results.txt')}

    database_keys_mapping = {'coi': 'colorIdentity', 'cmc': 'convertedManaCost', 'col':'colors', 'kyw':'keywords',
                            'mnc': 'manaCost', 'mnv': 'manaValue', 'name': 'name', 'pwr': 'power',
                            'rty': 'rarity', 'rul': 'rulings', 'sbt': 'subtypes', 'spt': 'supertypes', 'text': 'text',
                            'tgh': 'toughness', 'tps': 'types', 'leg': 'legalities'}
    
    # convert search string into a dict with the key:value pairs
    search_terms = {}

    for r in result:
        k, v = r.split(':')
        
        # handle any comma seperated value fields, excluding text and name fields
        if ',' in v and (k != 'text' or k != 'name'):
            v = v.split(',')

        # remove any quotes in a string
        if '"' in v:
            v = v.replace('"', '')

        # convert certain fields to floats
        if k == 'cmc' or k == 'mnv':
            v = float(v)

        # handle colors and color identity fields
        # any combo of WUBRG in a string means explicitly those colors
        # comma seperated WUBRG denotes any combination of those colors
        if k == 'col' or k == 'coi':
            new_v = {"type": "", "colors_to_match": []}

            if type(v) == str:
                if k == 'col':
                    new_v["type"] = "explicit_colors"
                elif k == 'coi':
                    new_v["type"] = "explicit_colorIdentity"
                new_v["colors_to_match"] = list(v)

            elif type(v) == list:
                if k == 'col':
                    new_v["type"] = "includes_colors"
                elif k == 'coi':
                    new_v["type"] = "includes_colorIdentity"
                new_v["colors_to_match"] = v

            v = new_v


        search_terms[database_keys_mapping[k]] = v

    util_funcs.log_message(f'search_terms: {search_terms}', 'DEBUG')
    return search_terms

def compare_colors(colors_to_match, card_colors, mode):
    # this simplifies matching the two lists of colors to each other
    # includes - the card_colors contains any of the colors asked for in colors to match, to include
    #            colorless cards
    # explicit - will only match the colors provided. (i.e: 'WU' will only match multicolor white/blue cards)

    if 'includes' in mode:
        if len(card_colors) == 0:
            return True
        else:
            # this loop will go through all the colors to match and see if the color
            # is in the cards colors. In theory, if a color is not in there, it will
            # pass it, moving to the next block. if no match is found, then it will
            # go down to the final return statement returning false
            for color in colors_to_match:
                if color in card_colors:
                    return True
                
    elif 'explicit' in mode:
        if mode == 'explicit_colorIdentity' and len(card_colors) == 0:
            return True
        
        elif mode == 'explicit_colors' and len(colors_to_match) == 0 and len(card_colors) == 0:
            return True
        
        else:
            matches = 0
            for color in colors_to_match:
                if color in card_colors:
                    matches += 1

            if matches == len(card_colors) and matches == len(colors_to_match):
                return True

    # the function returns false by default, meaning all other cases of true
    # should be handled above            
    return False

def search_list_for_any_match(search_terms, data_to_check):
    # this is an ambiguous function that will take in a list of values to check
    # and see if any of them are in the data_to_check
    # on the first match, true is returned, with false meaning no matches
    # were found
    if type(search_terms) == str:
        if search_terms in data_to_check:
            return True
        
    elif type(search_terms) == list: 
        for term in search_terms:
            if term in data_to_check:
                return True
        
    return False

def search_database(database, search_string):
    # searches the database with the matching search terms
    # the function treats all terms as ANDed together, only
    # returning a list of cards that match all of the criteria
    # individual keys can have ORed terms
    search_terms = parse_search_string(search_string)

    # this is the intermediate list and the final result
    results = database

    for key, term_to_match in search_terms.items():
        # this will ensure that the key being search for will be in the results
        results = {k:v for k, v in results.items() if key in v.keys()}

        # handle special cases first
        if key == "colors" or key=="colorIdentity":
            type_of_match = term_to_match['type']
            colors = term_to_match['colors_to_match']


            if len(colors) == 0:
                # handles all colorless cards
                results = {k:v for k, v in results.items() if len(v['colors']) == 0}

            elif 'includes' in type_of_match:
                results = {k:v for k, v in results.items() if compare_colors(colors, v[key], type_of_match)}

            elif 'explicit' in type_of_match:
                results = {k:v for k, v in results.items() if compare_colors(colors, v[key], type_of_match)}

        elif key == "rarity":            
            # then check for matches
            results = {k:v for k, v in results.items() if v['rarity'] in term_to_match}

        elif key == "text":
            results = {k:v for k, v in results.items() if term_to_match in v['text']}

        elif key == "types":
            results = {k:v for k, v in results.items() if search_list_for_any_match(term_to_match, v['types'])}

        

    return results
from src import util_funcs
from datetime import timedelta as timedelta
from datetime import date as date
import os
import platform

MTGJSON_DATA = "resources/mtgjson_data"

# price_file_location: https://mtgjson.com/api/v5/AllPrices.json.zip
# identifiers_location: https://mtgjson.com/api/v5/AllIdentifiers.json.zip

def reformat_card_data(data):
    # because the data from MTGJSON is a large file with a bunch of unecessary data
    # the intent of this function is to reformat the data to be organized by the cards name
    # because cards have multiple printings, the data stored will be by the setcode for each card
    # so later pricing info can be added to each cards printing.

    mapping = {}

    for k, v in data.items():
        if mapping.get(v['name']):
            mapping[v['name']][v['setCode']] = {'uuid': k}
        
        else:
            mapping[v['name']] = {v['setCode']: {'uuid': k}}

    return mapping

def get_recent_pricing(price_info):
    # this will take the pricing data, and will use the most recent date that
    # is provided
    price_data = {}

    for treatment, data in price_info.items():
        price_dates = [date.fromisoformat(x) for x in data.keys()]
        price_dates.sort(reverse=True)
        latest_date = price_dates[0]
        
        price_data['price_date'] = latest_date.isoformat()
        price_data[treatment] = data[latest_date.isoformat()]

    return price_data


def get_uuids_with_pricing_data(card_database, pricing_data):
    cards_to_process = {}

    for card_name, data in card_database.items():
        for setCode, setNumbers in data['uuids'].items():
            for setNumber, uuid in setNumbers.items():
                if uuid in pricing_data.keys():
                    cards_to_process[uuid] = {'setCode': setCode, 'name': card_name, 'setNumber': setNumber}

    return cards_to_process

def map_pricing_data_to_cards(pricing_data, card_database, sites=['tcgplayer', 'cardkingdom']):
    pricing_database = {}

    # first get all the uuid's of cards that have pricing data
    cards_to_check = get_uuids_with_pricing_data(card_database, pricing_data)

    cards_with_paper_printing = [x for x in cards_to_check.keys() if 'paper' in pricing_data[x].keys()]

    for uuid in cards_with_paper_printing:
        name = cards_to_check[uuid]['name']
        setCode = cards_to_check[uuid]['setCode']
        setNumber = cards_to_check[uuid]['setNumber']
        if name not in pricing_database.keys():
            pricing_database[name] = {setCode: {setNumber: {}}}

        else:
            if setCode not in pricing_database[name].keys():
                pricing_database[name][setCode] = {setNumber: {}}

            else:
                if setNumber not in pricing_database[name][setCode].keys():
                    pricing_database[name][setCode][setNumber] = {}

        site_pricing = {}
        for site, price_data in pricing_data[uuid]['paper'].items():
            if site in sites and price_data['currency'] == 'USD':
                site_pricing[site] = {'retail': {}, 'buylist': {}}

                retail_prices = price_data.get('retail')
                buylist_prices = price_data.get('buylist')

                if retail_prices != None:
                    site_pricing[site]['retail'] = get_recent_pricing(retail_prices)
                else:
                    site_pricing[site]['retail']['error'] = "no retail pricing available"
                
                if buylist_prices != None:
                    site_pricing[site]['buylist'] = get_recent_pricing(buylist_prices)
                else:
                    site_pricing[site]['buylist']['error'] = "no buylist pricing available"

        pricing_database[name][setCode][setNumber] = site_pricing

    return pricing_database

def download_card_pricing_info():
    today = date.today()
    filename = f"AllPrices_{today.isoformat()}.json"
    zipfile_name = f"AllPrices_{today.isoformat()}.json.zip"
    download_url = 'https://mtgjson.com/api/v5/AllPrices.json.zip'
    if filename not in os.listdir('resources/mtgjson_data'):
        util_funcs.download_file_from_url(download_url, zipfile_name)
        util_funcs.unzip_file_to_loc(f'resources/tmp/{zipfile_name}', 'resources/mtgjson_data')
        if platform.system() == "Windows":
            os.system(f'move resources\\mtgjson_data\\AllPrices.json resources\\mtgjson_data\\{filename}')
        elif platform.system() == "Linux":
            os.system(f'mv resources/mtgjson_data/AllPrices.json resources/mtgjson_data/{filename}')

def consturct_card_pricing_info(card_database):
    # this function should be run after the card_database is generated, hence why the card_database is 
    # a required input
    
    today = date.today()
    filename = f"AllPrices_{today.isoformat()}.json"
    download_card_pricing_info()
    

    pricing_data = util_funcs.import_json_file(f"resources/mtgjson_data/{filename}")

    # map the pricing data to the card info
    pricing_info = map_pricing_data_to_cards(pricing_data['data'], card_database)

    util_funcs.export_json_file("resources/databases/price_info/pricing_database.json", pricing_info)

    return pricing_info

def load_pricing_database(card_database):
    filename = 'pricing_database.json'
    metadata = util_funcs.import_json_file("resources/tmp/database_update_metadata.json")
    if filename not in os.listdir('resources/databases/price_info') or date.fromisoformat(metadata["pricing_info"]) < date.today():
        consturct_card_pricing_info(card_database)
        metadata["pricing_info"] = date.today().isoformat()
        util_funcs.export_json_file("resources/tmp/database_update_metadata.json", metadata)

    return util_funcs.import_json_file(f"resources/databases/price_info/{filename}")


def get_price_from_card_db(card_info, price_database, site):
    # card info needs to be in the following format:
    # {"name": "", "setCode": "", "setNumber: "", "treatment": ""}
    current_price = 0

    try:
        set_price_data = price_database[card_info["name"]][card_info['setCode']]
        current_price = set_price_data[card_info["setNumber"]][site]['retail'][card_info['treatment']]

    except AttributeError:
        util_funcs.log_message(f"{card_info} cause an error when getting the price", "WARNING")

    except KeyError:
        util_funcs.log_message(f"{card_info} does not have pricing data with this informmation", "WARNING")
    
    if current_price == None:
        current_price = 0

    return current_price


def get_valuation_of_deck(deck_info, price_database, site="tcgplayer"):
    # Get the price valuation of the deck
    # the deck should store the setcode of the card to ensure the proper card price
    # is being used
    # it also defaults to tcgplayer as the preferred site to use, cardkingdom is available as an alternative
    total_value = 0
    errors = []

    commander_value = get_price_from_card_db(deck_info["commander"], price_database, site)

    if commander_value > 2:
        total_value += commander_value

    for card_type, data in deck_info["the_99"].items():
        if card_type != "basic_lands":
            if len(data) > 0:
                for card_info in data:
                    card_value = get_price_from_card_db(card_info, price_database, site)

                    if card_value != None:
                        if card_value > 2:
                            total_value += card_value
                    else:
                        errors.append(card_info)

    util_funcs.log_message(f"Errors in get_valuation_of_deck({deck_info['name']}): {errors}", "INFO")

    return round(total_value, 2)
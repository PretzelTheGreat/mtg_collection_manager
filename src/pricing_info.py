import src.util_funcs as util_funcs
from datetime import timedelta as timedelta
from datetime import date as date
import os

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


def get_todays_price(price_info):
    today = date.today()
    yesterday = today - timedelta(days=1)
    price_data = {}

    # first, it will check to see if there is pricing data for today
    # if not it will check one day before today

    for treatment, data in price_info.items():
        price_dates = data.keys()

        if today.isoformat() in price_dates:
            price_data['price_date'] = today.isoformat()
            price_data[treatment] = data[today.isoformat()]

        elif yesterday.isoformat() in price_dates:
            price_data['price_date'] = yesterday.isoformat()
            price_data[treatment] = data[yesterday.isoformat()]
        

    return price_data

def map_pricing_data_to_cards(price_info, card_data, sites_to_use=['tcgplayer', 'cardkingdom']):
    # take the imported price info and map it to each card, by set and price of today
    # the pricing data will be held in a separate structure, in order for ease of access
    price_data = {}
    for card_name, data in card_data.items():
        price_data[card_name] = {}
        # at this level, it includes all the data for the cards
        # since the price data is stored by the uuid for each printing, work with that
        for setCode, uuid in data['uuids'].items():
            price_data[card_name][setCode] = {}
            card_prices_by_site = {}
            if uuid in price_info.keys():
                card_pricing_all = price_info.get(uuid)
                if 'paper' in card_pricing_all.keys():
                    current_card_prices = card_pricing_all.get('paper')

                    for site, price_data in current_card_prices.items():
                        if site in sites_to_use:
                            if price_data['currency'] == 'USD':
                                if not card_prices_by_site.get(site):
                                    card_prices_by_site[site] = {'retail': {}, 'buylist': {}}
                                
                                retail_prices = price_data.get('retail')
                                buylist_prices = price_data.get('buylist')

                                if retail_prices != None:
                                    card_prices_by_site[site]['retail'] = get_recent_pricing(retail_prices)
                                else:
                                    card_prices_by_site[site]['retail']['error'] = "no retail pricing available"
                                
                                if buylist_prices != None:
                                    card_prices_by_site[site]['buylist'] = get_recent_pricing(buylist_prices)
                                else:
                                    card_prices_by_site[site]['buylist']['error'] = "no buylist pricing available"

                else:
                    price_data[card_name][setCode]['prices'] = {"error": "no paper printing available"}
            
            else:
                price_data[card_name][setCode]['prices'] = {"error": "no pricing data available"}
            
            price_data[card_name][setCode]['prices'] = card_prices_by_site


            
    return price_data

def download_card_pricing_info():
    today = date.today()
    filename = f"AllPrices_{today.isoformat()}.json"
    zipfile_name = f"AllPrices_{today.isoformat()}.json.zip"
    download_url = 'https://mtgjson.com/api/v5/AllPrices.json.zip'
    if filename not in os.listdir('resources/mtgjson_data'):
        util_funcs.download_file_from_url(download_url, zipfile_name)
        util_funcs.unzip_file_to_loc(f'resources/tmp/{zipfile_name}', 'resources/mtgjson_data')
        os.system(f'move resources\\mtgjson_data\\AllPrices.json resources\\mtgjson_data\\{filename}')

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
    if filename not in os.listdir('resources/databases/price_info'):
        consturct_card_pricing_info(card_database)

    return util_funcs.import_json_file(f"resources/databases/price_info/{filename}")


def get_price_from_card_db(card_info, card_db, site):
    current_price = 0
    card_sets = card_db.get(card_info['name'])
    if card_sets:
        set_prices = card_sets[card_info["setCode"]]

        if set_prices.get('prices'):
            if set_prices['prices'].get(site):
                current_price = set_prices.get('prices').get(site).get('retail').get(card_info.get('treatment'))
    
    return current_price


def get_valuation_of_deck(deck_info, card_database, site="tcgplayer"):
    # Get the price valuation of the deck
    # the deck should store the setcode of the card to ensure the proper card price
    # is being used
    # it also defaults to tcgplayer as the preferred site to use, cardkingdom is available as an alternative
    total_value = 0
    errors = []

    commander_value = get_price_from_card_db(deck_info["commander"], card_database, site)

    if commander_value > 2:
        total_value += commander_value

    for card_type, data in deck_info["the_99"].items():
        if card_type != "basic_lands":
            if len(data) > 0:
                for card_info in data:
                    card_value = get_price_from_card_db(card_info, card_database, site)

                    if card_value != None:
                        if card_value > 2:
                            total_value += card_value
                    else:
                        errors.append(card_info)

    print(errors)

    return total_value
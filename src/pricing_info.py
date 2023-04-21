import src.util_funcs as util_funcs
from datetime import timedelta as timedelta
from datetime import date as date
import os

MTGJSON_DATA = "resources/mtgjson_data"

# TODO: at some point, include automatically downloading and unzipping the required files from https://mtgjson.com/downloads/all-files/

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


def map_pricing_data_to_cards(price_info, card_data,sites_to_use=['tcgplayer', 'cardkingdom']):
    # take the imported price info and map it to each card, by set and price of today
    for card, data in card_data.items():
        # level: card = {setcode: {}...}
        for setCode, data_2 in data.items():
            # level: setCode = {uuid: string...}
            card_prices_by_site = {}
            card_pricing_all = price_info.get(data_2['uuid'])
            if not card_pricing_all:
                break

            current_card_prices = card_pricing_all.get('paper')

            if not current_card_prices:
                break

            for site, data_3 in current_card_prices.items():
                if site in sites_to_use:
                    if data_3['currency'] == 'USD':
                        if not card_prices_by_site.get(site):
                            card_prices_by_site[site] = {'retail': {}, 'buylist': {}}
                        
                        retail_prices = data_3.get('retail')
                        buylist_prices = data_3.get('buylist')

                        if retail_prices != None:
                            card_prices_by_site[site]['retail'] = get_todays_price(retail_prices)
                        else:
                            card_prices_by_site[site]['retail']['error'] = "no retail pricing available"
                        
                        if buylist_prices != None:
                            card_prices_by_site[site]['buylist'] = get_todays_price(buylist_prices)
                        else:
                            card_prices_by_site[site]['buylist']['error'] = "no buylist pricing available"

            card_data[card][setCode]['prices'] = card_prices_by_site

    return card_data


def setup_card_pricing_info():
    # this will first check to see if a database file already exists
    # and load it if it is
    price_database_filename = f"price_database_{date.today().isoformat()}.json"
    if price_database_filename in os.listdir('resources/databases/price_info'):
        existing_data = util_funcs.import_json_file(f"resources/databases/price_info/{price_database_filename}")
        return existing_data
    
    else:

        identifiers = util_funcs.import_json_file(f"{MTGJSON_DATA}/AllIdentifiers.json")
        price_info = util_funcs.import_json_file(f"{MTGJSON_DATA}/AllPrices.json")

        # first reformat the data
        card_data = reformat_card_data(identifiers['data'])

        # then add pricing info
        card_data = map_pricing_data_to_cards(price_info['data'], card_data)

        del identifiers, price_info # releasing the data here since the data within is no longer needed

        util_funcs.export_json_file(f"resources/databases/price_info/{price_database_filename}", card_data, indent=None)

        return card_data

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
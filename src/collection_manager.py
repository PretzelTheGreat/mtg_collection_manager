import src.util_funcs as util_funcs
import src.deck_parser as deck_parser
import src.pricing_info as pricing_info
import src.card_database as card_database
from datetime import date as date
import os

class CollectionManager:
    # The collection manager will be the interface that the user will work with
    # in order to interact with their collection. There will be various methods that
    # allow the user to get statistics about their collection (total price of cards above $2,
    # usage stats, etc.)
    def __init__(self, collection_filename, debug_level="DEBUG"):
        util_funcs.DEBUG_LEVEL = debug_level
        self.initalize_environment()
        self.collection_filename = collection_filename

        # first, initalize all the relevant databases
        # there is a check built in to the loading function for the
        # card_database and pricing_data variables to see if the file
        # has been generated for the day
        self.collection = util_funcs.import_json_file(self.collection_filename)
        self.card_database = card_database.load_card_database()
        card_database.generate_validation_files(self.card_database)
        self.pricing_data = pricing_info.load_pricing_database(self.card_database)
        self.constructed_decks = {}
        self.parse_decks_folder()
        self.collection_value = 0
        self.highest_value_card = {"name": "", "setCode": "", "treatment": "", "value": 0}
        self.calculate_value_of_collection()
        
    def initalize_environment(self):
        util_funcs.create_tmp_dir()

        if 'mtgjson_data' not in os.listdir('resources'):
            os.mkdir('resources/mtgjson_data')

        if 'price_info' not in os.listdir('resources/databases'):
            os.mkdir('resources/databases/price_info')

        # creates database metadata file in case it doesn't exist
        if 'database_update_metadata.json' not in os.listdir('resources/tmp'):
            data = {"card_database": "2010-01-01","pricing_info": "2010-01-01"}
            util_funcs.export_json_file("resources/tmp/database_update_metadata.json", data)

    def parse_decks_folder(self):
        folder = "resources/decks"

        for path, subfolders, filenames in os.walk(folder):
            for subfolder in subfolders:
                self.constructed_decks[subfolder] = {}

                for filename in os.listdir(f"resources/decks/{subfolder}"):
                    if "template" not in filename:
                        f_split = filename.split('.')[0]
                        new_fname = f"resources/decks/{subfolder}/{filename}"
                        self.constructed_decks[subfolder][f_split] = {"filename": new_fname}
                        self.constructed_decks[subfolder][f_split]["deck_stats"] = deck_parser.get_deck_stats(util_funcs.import_json_file(new_fname), self.pricing_data)


    def search_for_card_in_collection(self, card_name):
        # searches for ownership info of a card from the collection
        # it will also pull various other info from the different databases
        data = {"name": card_name, "sets": [], "ownership_info": {}, "current_prices": {}}

        if card_name not in self.collection.keys():
            print(f"{card_name} is not in your collection")
            return None
        
        card_found = self.collection[card_name]
        
        sets, ownership_info, current_prices = self.calculate_ownership_info(card_name, card_found)

        data["sets"] = sets
        data["ownership_info"] = ownership_info
        data["current_prices"] = current_prices

        return data


    def calculate_ownership_info(self, card_name, card_data):
        # this is used to simplify calling for calculating the ownership info for cards in the collection

        sets = []
        ownership_info = {"treatments": {"normal": 0, "foil": 0}, "in_use": {"normal": 0, "foil": 0}}
        current_prices = {} # {setCode: {"normal": 0, "foil": 0}}

        for setCode, set_data in card_data.items():
                sets.append(setCode)
                current_prices[setCode] = {}

                for k, v in set_data.items():
                    for treatment, num in v.items():
                        current_prices[setCode][treatment] = pricing_info.get_price_from_card_db({"name": card_name, "setCode": setCode, "treatment": treatment}, self.pricing_data, "tcgplayer")
                        ownership_info[k][treatment] += num

        return sets, ownership_info, current_prices
    

    def calculate_value_of_collection(self, minimum=2.0):
        # this will get a total valuation of your collection, based on a minimum value (set by default to 2)
        total_value = 0
        highest_value_card = {"name": "", "setCode": "", "setNumber": "", "treatment": "", "value": 0}

        for card_name, card_data in self.collection.items():
            for setCode, setNumbers in card_data.items():
                for setNumber, ownership_data in setNumbers.items():
                    for treatment, num in ownership_data['treatments'].items():
                        if num > 0:
                            tmp = {"name": card_name, "setCode": setCode, "setNumber": setNumber, "treatment": treatment}
                            current_price = pricing_info.get_price_from_card_db(tmp, self.pricing_data, "tcgplayer")

                            if current_price >= minimum:
                                if current_price > highest_value_card["value"] and num > 0:
                                    highest_value_card["name"] = card_name
                                    highest_value_card["setCode"] = setCode
                                    highest_value_card["setNumber"] = setNumber
                                    highest_value_card["treatment"] = treatment
                                    highest_value_card["value"] = round(current_price, 2)

                                total_value += current_price * num

        self.collection_value = round(total_value, 2)
        self.highest_value_card = highest_value_card


    def export_pricing_data(self, include_in_use=False, minimum=2.0):
        # this function will get all the cards with a price above the minimum, and put it into a csv
        # format. by default, this will exclude all in_use cards
        final_data = []

        for card_name, card_data in self.collection.items():
            for setCode, setNumbers in card_data.items():
                for setNumber, ownership_data in setNumbers.items():
                    for treatment, num in ownership_data['treatments'].items():
                        tmp = {"name": card_name, "setCode": setCode, "setNumber": setNumber, "treatment": treatment}
                        if num > 0:
                            current_price = pricing_info.get_price_from_card_db(tmp, self.pricing_data, "tcgplayer")
                            if current_price >= minimum:
                                # this will only export any cards that are not being used. The database will only allow for 
                                # the max in_use to be equal to the number in the "treatment" key
                                final_num = num
                                if not include_in_use:
                                    final_num = num - card_data[setCode][setNumber]["in_use"][treatment]

                                if final_num > 0:
                                    tmp["copies"] = final_num
                                    tmp["card_value"] = current_price
                                    tmp["subtotal"] = current_price * final_num
                                    tmp["60% value"] = round(tmp["subtotal"] * 0.6, 2)
                                    tmp["40% value"] = round(tmp["subtotal"] * 0.4, 2)

                                    final_data.append(tmp)


        util_funcs.export_csv_file("resources/tmp/collection_valuation.csv", final_data, final_data[0].keys())


    def modify_usage_stats(self, deck_name):
        # this will be used to add/subtract usage data for decks
        # there will be a metadata file tracking each deck to see if it's usage
        # type has changed

        pass

    def search_collection(self, search_string, in_use=False):
        # this will be used to find cards that match the search criteria. 
        # first, it will search the card_database for cards that match the 
        # criteria. Then when the results are returned, it will then look for
        # the name of the cards in my_collection, returning any matching results

        owned_cards = list(self.collection.keys())

        sub_results, invalid = card_database.search_database(self.card_database, search_string)

        if not invalid:
            final_results = {}

            for k, v in sub_results.items():
                if k in owned_cards:
                    if in_use:
                        final_results[k] = v

                    else:
                        ownership_info = self.collection[k]
                        num_not_in_use = 0

                        for setCode, setNumbers in ownership_info.items():
                            # setCode: {setNumber: {treatments: {normal: 0, foil: 0}, in_use: {normal: 0, foil: 0}}}
                            for setNumber, usage_data in setNumbers.items():
                                # setNumber: {treatments: {normal: 0, foil: 0}, in_use: {normal: 0, foil: 0}}
                                owned = usage_data['treatments']['normal'] + usage_data['treatments']['foil']
                                used = usage_data['in_use']['normal'] + usage_data['in_use']['foil']
                                num_not_in_use = owned - used

                        if num_not_in_use > 0:
                            final_results[k] = v


            return final_results
        
        else:
            print(f"The search string contained errors (see below)")
            for k, v in sub_results.items():
                print(f"{k}: input was {v['input']}, error reason: {v['reason']}")
                
            # returning an empty dict to represent no results
            return {}
# this will make adding cards to the database easier
import src.util_funcs as util_funcs
import sys

# number in this context is the number that correlates to the number
# the card has for it's setCode
# card_format = {"name": "", "setCode": "", setNumber: {"treatments": {"normal": 0, "foil": 0}, "in_use": {"normal": 0, "foil": 0}}}

def manual_add_card():
    data = {"name": "", "setCode": "", "treatments": {"normal": 0, "foil": 0}, "in_use": {"normal": 0, "foil": 0}}
    while True:
        name = input("Name: ")
        setCode = input("setCode: ")
        treatment = input("treatment type: ")
        num_of_treatment = input("how many cards with this name?: ")

        print(name, setCode, treatment, num_of_treatment)
        
        check = input("Is this correct (DOUBLE CHECK SPELLING): ")

        if check.lower() == "yes" or check.lower() == "y":
            data["name"] = name.strip()
            data["setCode"] = setCode.strip()
            data["treatments"][treatment.strip()] = int(num_of_treatment)
            break

    return data

def auto_add_cards(filename):
    # this file should include the following keys:
    # name,setCode,treatment,num_of_treatment,num_in_use
    cards_to_add = util_funcs.import_csv_file(filename)
    new_cards = []

    for card in cards_to_add:
        data = {"name": "", "setCode": "", "setNumber": "", "treatments": {"normal": 0, "foil": 0}, "in_use": {"normal": 0, "foil": 0}}

        data["name"] = card["name"]
        data["setCode"] = card["setCode"]
        data["setNumber"] = card["setNumber"]

        if card["treatment"] == "normal":
            data["treatments"]["normal"] += int(card["num_of_treatment"])
            data["in_use"]["normal"] += int(card["num_in_use"])

        elif card["treatment"] == "foil":
            data["treatments"]["foil"] += int(card["num_of_treatment"])
            data["in_use"]["foil"] += int(card["num_in_use"])

        new_cards.append(data)

    deduped_list = dedupe_add_list(new_cards)

    return deduped_list


def dedupe_add_list(add_list):
    new_add_list = {}

    for card in add_list:
        combined_name = f"{card['name']}:{card['setCode']}:{card['setNumber']}"
        if combined_name not in new_add_list.keys():
            new_add_list[combined_name] = card

        else:
            new_add_list[combined_name]['treatments']['normal'] += card['treatments']['normal']
            new_add_list[combined_name]['treatments']['foil'] += card['treatments']['foil']
            new_add_list[combined_name]['in_use']['normal'] += card['in_use']['normal']
            new_add_list[combined_name]['in_use']['foil'] += card['in_use']['foil']

    return list(new_add_list.values())

def reformat_to_database_format(data):
    # this will take the deduped added list and reformat it into a format
    # that can be saved in json format
    # format = {"card_name": {"setCode": {"setNumber": {treatment data and usage data}}}}

    new_format = {}

    for card in data:
        name = card["name"]
        setCode = card["setCode"]
        setNumber = card["setNumber"]
        if name not in new_format.keys():
            new_format[name] = {setCode: {setNumber: {"treatments": card["treatments"], "in_use": card["in_use"]}}}

        else:
            if setCode not in new_format[name].keys():
                new_format[name][setCode] = {setNumber: {"treatments": card["treatments"], "in_use": card["in_use"]}}
            else:
                if setNumber not in new_format[card["name"]][card["setCode"]].keys():
                    new_format[card["name"]][card["setCode"]][card["setNumber"]] = {"treatments": card["treatments"], "in_use": card["in_use"]}

    return new_format

def merge_database_with_new_data(database, new_data):
    # this will merge an exisiting database with cards
    # added. This step will be run after the new cards are
    # deduped and reformatted to the database format
    for card_name, data in new_data.items():
        if card_name not in database.keys():
            database[card_name] = data

        else:
            for setCode, setNumbers in data.items():
                if setCode not in database[card_name].keys():
                    database[card_name][setCode] = setNumbers
                else:
                    for setNumber, ownership_data in setNumbers.items():
                        if setNumber not in database[card_name][setCode].keys():
                            database[card_name][setCode][setNumber] = ownership_data

                        else:
                            for treatment, num in ownership_data["treatments"].items():
                                database[card_name][setCode][setNumber]["treatments"][treatment] += num

                            for treatment, num in ownership_data["in_use"].items():
                                database[card_name][setCode][setNumber]["in_use"][treatment] += num

    return database

def card_adding_menu():
    cards_to_add = []

    while True:
        print("You are currently in the card adding menu. Ctrl+c to quit")

        try:
            new_card = manual_add_card()
            cards_to_add.append(new_card)
            print("\n\n")

        except KeyboardInterrupt:
            break
            
            
    deduped_list = dedupe_add_list(cards_to_add)
    new_format = reformat_to_database_format(deduped_list)

    #util_funcs.export_json_file("resources/databases/my_collection.json", final_database)
    return new_format

def calculate_number_of_cards(new_cards):
    total = 0

    for card_name, sets in new_cards.items():
        for setCode, setNumbers in sets.items():
            for setNumber, ownership_data in setNumbers.items():
                for treatment, num in ownership_data["treatments"].items():
                    total += num

    return total

def run_tool(database_filename, cards_to_add_filename):
    # this tool should preferably be run automated.
    # the manual adding is kept here as a alternate way
    existing_database = util_funcs.import_json_file(database_filename)
    new_cards_to_add = auto_add_cards(cards_to_add_filename)
    reformatted_cards = reformat_to_database_format(new_cards_to_add)
    final_database = merge_database_with_new_data(existing_database, reformatted_cards)
    util_funcs.export_json_file(database_filename, final_database)
    print(f"Database has been saved! Added {calculate_number_of_cards(reformatted_cards)} more cards!")

if len(sys.argv) > 2:
    run_tool(sys.argv[1].strip(), sys.argv[2].strip())

else:
    print(f"format: \n\tcard_input_tool [database_filename] [cards_to_add_filename]")

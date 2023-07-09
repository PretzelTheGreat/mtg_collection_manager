# this will make adding cards to the database easier
import src.util_funcs as util_funcs

card_format = {"name": "", "setCode": "", "treatments": {"normal": 0, "foil": 0}, "in_use": {"normal": 0, "foil": 0}}

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

def dedupe_add_list(add_list):
    new_add_list = {}

    for card in add_list:
        combined_name = f"{card['name']}:{card['setCode']}"
        if combined_name not in new_add_list.keys():
            new_add_list[combined_name] = card

        else:
            new_add_list[combined_name]['treatments']['normal'] += card['treatments']['normal']
            new_add_list[combined_name]['treatments']['foil'] += card['treatments']['foil']
            new_add_list[combined_name]['in_use']['normal'] += card['in_use']['normal']
            new_add_list[combined_name]['treatments']['foil'] += card['in_use']['foil']

    return list(new_add_list.values())

def reformat_to_database_format(data):
    # this will take the deduped added list and reformat it into a format
    # that can be saved in json format
    # format = {"card_name": {"setCode": {treatment data and usage data}}}

    new_format = {}

    for card in data:
        if card["name"] not in new_format.keys():
            new_format[card["name"]] = {card["setCode"]: {"treatments": card["treatments"], "in_use": card["in_use"]}}

        else:
            new_format[card["name"]][card["setCode"]] = {"treatments": card["treatments"], "in_use": card["in_use"]}

    return new_format

def merge_database_with_new_data(database, new_data):
    # this will merge an exisiting database with cards
    # added. This step will be run after the new cards are
    # deduped and reformatted to the database format
    for card_name, data in new_data.items():
        if card_name not in database.keys():
            database[card_name] = data

        else:
            for setCode, ownership_data in data.items():
                if setCode not in database[card_name].keys():
                    database[card_name][setCode] = ownership_data

                else:
                    for treatment, num in ownership_data["treatments"].items():
                        database[card_name][setCode]["treatments"][treatment] += num

                    for treatment, num in ownership_data["in_use"].items():
                        database[card_name][setCode]["in_use"][treatment] += num

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
        for setCode, ownership_data in sets.items():
            for treatment, num in ownership_data["treatments"].items():
                total += num

    return total

def run_tool():
    existing_database = util_funcs.import_json_file("resources/databases/my_collection.json")
    new_cards_to_add = card_adding_menu()
    print("\n\n")
    final_database = merge_database_with_new_data(existing_database, new_cards_to_add)
    util_funcs.export_json_file("resources/databases/my_collection.json", final_database)
    print(f"Database has been saved! Added {calculate_number_of_cards(new_cards_to_add)} more cards!")
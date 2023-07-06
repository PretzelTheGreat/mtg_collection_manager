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

    util_funcs.export_json_file("resources/databases/my_collection.json", new_format)
    
card_adding_menu()